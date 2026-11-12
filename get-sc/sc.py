import time
import numpy as np
import RPi.GPIO as GPIO
import r2r_adc 

CHARGE_PIN = 17
MAX_VOLTAGE = 2.7
dynamic_range = 2.667 

GPIO.setmode(GPIO.BCM)
GPIO.setup(CHARGE_PIN, GPIO.OUT)
adc = r2r_adc.R2R_ADC(dynamic_range, compare_time=0.0001) 
time_values = []
voltage_values = []

try:
    print("Начало эксперимента: Зарядка...")
    start_time = time.time()
    
 
    GPIO.output(CHARGE_PIN, 1)
    voltage = 0.0
    
    # Цикл зарядки 
    while voltage < 0.95 * MAX_VOLTAGE:
        voltage = adc.get_sc_voltage() 
        voltage_values.append(voltage)
        time_values.append(time.time() - start_time)
        
    print("Конденсатор заряжен. Начало разрядки...")

    GPIO.output(CHARGE_PIN, 0)
    
    # Цикл разрядки 
    while voltage > 0.05 * MAX_VOLTAGE:
        voltage = adc.get_sc_voltage() 
        voltage_values.append(voltage)
        time_values.append(time.time() - start_time)

    print("Эксперимент завершен. Сохранение данных...")
    
    # Объединение списков 
    data = np.column_stack((time_values, voltage_values))
    
    # Запись в файл 
    np.savetxt('data.csv',
               data,
               delimiter=',',
               fmt='%.4f',
               header='Время[с],Напряжение[В]',
               comments='',
               encoding='utf-8')
    print("Файл data.csv успешно создан!")

finally:
    # Безопасный выход 
    GPIO.output(CHARGE_PIN, 0)
    GPIO.cleanup()
    adc.deinit() 