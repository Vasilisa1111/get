import RPi.GPIO as GPIO
class PWM_DAC:
    def __init__(self, gpio_pin, pwm_frequency, dynamic_range, verbose = False):
        self.gpio_pin = gpio_pin
        self.dynamic_range = dynamic_range
        self.verbose = verbose    
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT, initial = 0)
        self.pwm = GPIO.PWM(self.gpio_pin, pwm_frequency)
        self.pwm.start(0)
        if self.verbose:
            print(
                f"Инициализирован PWM DAC: GPIO{self.gpio_pin}, "
                f"частота {pwm_frequency} Гц, диапазон {dynamic_range:.3f} В"
            )
        
    def deinit(self):
        self.pwm.stop()
        GPIO.output(self.gpio_pin, 0)
        GPIO.cleanup()
        if self.verbose:
            print("Генерация ШИМ остановлена, настройки GPIO сброшены.")

    def set_voltage(self, voltage):
        
        if not (0.0 <= voltage <= self.dynamic_range):
            if self.verbose:
                print(
                    f"Напряжение выходит за динамический диапазон ЦАП "
                    f"(0.00 - {self.dynamic_range:.2f} В)"
                )
                print("Устанавливаем 0.0 В")
            voltage = 0.0

        
        duty_cycle = (voltage / self.dynamic_range) * 100.0
        duty_cycle = max(0.0, min(100.0, duty_cycle))

        self.pwm.ChangeDutyCycle(duty_cycle)

        if self.verbose and voltage > 0.0:
            print(
                f"Установлено напряжение: {voltage:.3f} В "
                f"(Заполнение ШИМ: {duty_cycle:.2f}%)"
            )
if __name__ == "__main__":
    try:
        dac = PWM_DAC(12, 500, 3.185, True)
        
        while True:
            try:
                voltage = float(input("Введите напряжение в Вольтах: "))
                dac.set_voltage(voltage)

            except ValueError:
                print("Вы ввели не число. Попробуйте ещё раз\n")

    finally:
        dac.deinit()