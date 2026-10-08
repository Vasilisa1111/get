import smbus


class MCP4725:

    def __init__(self, dynamic_range, address=0x61, verbose=True):
        self.bus = smbus.SMBus(1)

        self.address = address
        self.wm = 0x00
        self.pds = 0x00

        self.verbose = verbose
        self.dynamic_range = dynamic_range

    def deinit(self):
        "Закрывает соединение с шиной I2C."
        self.bus.close()
        if self.verbose:
            print("Соединение по I2C закрыто.")

    def set_number(self, number):
        "Отправляет 12-битное целое число (0..4095) в MCP4725."
        if not isinstance(number, int):
            print("На вход ЦАП можно подавать только целые числа")
            return

        if not (0 <= number <= 4095):
            print("Число выходит за разрядность MCP4725 (12 бит)")
            print("Устанавливаем ближайшее допустимое значение")
            number = max(0, min(4095, number))

        first_byte = self.wm | self.pds | (number >> 8)
        second_byte = number & 0xFF

        # Используем self.address вместо хардкода 0x61
        self.bus.write_byte_data(self.address, first_byte, second_byte)

        if self.verbose:
            print(
                f"Число: {number}, отправленные по I2C данные: "
                f"[0x{(self.address << 1):02X}, 0x{first_byte:02X}, 0x{second_byte:02X}]\n"
            )

    def set_voltage(self, voltage):
        "Принимает напряжение в Вольтах и передаёт число в set_number."
        if not (0.0 <= voltage <= self.dynamic_range):
            if self.verbose:
                print(
                    f"Напряжение выходит за динамический диапазон ЦАП "
                    f"(0.00 - {self.dynamic_range:.2f} В)"
                )
                print("Устанавливаем 0.0 В")
            voltage = 0.0

        number = int(round(voltage / self.dynamic_range * 4095))
        self.set_number(number)



if __name__ == "__main__":
    try:
        dac = MCP4725(dynamic_range=5.2, address=0x61, verbose=True)

        while True:
            try:
                voltage = float(input("Введите напряжение в Вольтах: "))
                dac.set_voltage(voltage)

            except ValueError:
                print("Вы ввели не число. Попробуйте ещё раз\n")

    finally:
        dac.deinit()