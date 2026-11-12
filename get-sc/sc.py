import time
import numpy as np
import RPi.GPIO as GPIO
import r2r_adc # Импорт модуля работы с АЦП[cite: 2]

# Настройка параметров
CHARGE_PIN = 17
MAX_VOLTAGE = 3.3
dynamic_range = 3.295 #[cite: 2]

# Инициализация GPIO и объекта АЦП
GPIO.setmode(GPIO.BCM)
GPIO.setup(CHARGE_PIN, GPIO.OUT)
adc = r2r_adc.R2R_ADC(dynamic_range, compare_time=0.0001) #[cite: 2]

# Списки для хранения данных
time_values = []
voltage_values = []

try:
    print("Начало эксперимента: Зарядка...")
    start_time = time.time()
    
    # Подаем 1 на пин зарядки
    GPIO.output(CHARGE_PIN, 1)
    voltage = 0.0
    
    # Цикл зарядки (пока напряжение не достигнет ~95% от максимума)
    while voltage < 0.95 * MAX_VOLTAGE:
        voltage = adc.get_sc_voltage() #[cite: 2]
        voltage_values.append(voltage)
        time_values.append(time.time() - start_time)
        
    print("Конденсатор заряжен. Начало разрядки...")
    # Подаем 0 на пин для начала разрядки
    GPIO.output(CHARGE_PIN, 0)
    
    # Цикл разрядки (пока напряжение не упадет до ~5% от максимума)
    while voltage > 0.05 * MAX_VOLTAGE:
        voltage = adc.get_sc_voltage() #[cite: 2]
        voltage_values.append(voltage)
        time_values.append(time.time() - start_time)

    print("Эксперимент завершен. Сохранение данных...")
    
    # Объединение списков в двумерный массив
    data = np.column_stack((time_values, voltage_values))
    
    # Запись в файл по инструкции
    np.savetxt('data.csv',
               data,
               delimiter=',',
               fmt='%.4f',
               header='Время[с],Напряжение[В]',
               comments='',
               encoding='utf-8')
    print("Файл data.csv успешно создан!")

finally:
    # Безопасный выход и вызов деструктора[cite: 2]
    GPIO.output(CHARGE_PIN, 0)
    GPIO.cleanup()
    adc.deinit() #[cite: 2]