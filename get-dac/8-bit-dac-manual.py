import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
dac = [22, 27, 17, 26, 25, 21, 20, 16]
GPIO.setup(dac, GPIO.OUT)
dynamic_range=3.3
def voltage_to_number(voltage):
    if not (0.0 <= voltage <= dynamic_range):
        print(f"Напряжение выходит за динамический диапазон ЦАП (0.00 - {dynamic_range:.2f} В)")
        print("Устанавлниваем 0.0 В")
        return 0

    return int(voltage / dynamic_range * 255)
def number_to_dac(number):
    number = max(0, min(255, int(number)))
    bits = [(number >> i) & 1 for i in range(7, -1, -1)]
    GPIO.output(dac, bits)

try:
    while True:
        try:
            voltage = float(input("Введите напряжение в Вольтах: "))
            number = voltage_to_number(voltage)
            number_to_dac(number)

        except ValueError:
            print("Вы ввели не число. Попробуйте ещё раз\n")

finally:
    GPIO.output(dac, 0)
    GPIO.cleanup()