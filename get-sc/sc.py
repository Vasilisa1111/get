import time
import numpy as np
import RPi.GPIO as GPIO
import mcp3021_driver

CHARGE_PIN = 17
PHASE_DURATION = 40.0  

# Укажите ваше фактическое напряжение питания АЦП (например, 4.0 В)
dynamic_range = 4.0 

GPIO.setmode(GPIO.BCM)
GPIO.setup(CHARGE_PIN, GPIO.OUT)
adc = mcp3021_driver.MCP3021(dynamic_range)

voltage_values = []
time_values = []

try:
    print(f"--- НАЧАЛО ЭКСПЕРИМЕНТА ---")
    print(f"Фаза 1: Зарядка ({PHASE_DURATION} сек)")
    GPIO.output(CHARGE_PIN, 1)
    
    global_start_time = time.time()
    phase_start = time.time()
    
    while time.time() - phase_start < PHASE_DURATION:
        current_time = time.time() - global_start_time
        try:
            voltage = adc.get_voltage()
            voltage_values.append(voltage)
            time_values.append(current_time)
            
            # Живой вывод напряжения и времени в консоль
            print(f"\rВремя: {current_time:.1f} с | Напряжение: {voltage:.3f} В", end='', flush=True)
            
        except OSError:
            pass
        time.sleep(0.01)
        
    print(f"\n\nФаза 2: Разрядка ({PHASE_DURATION} сек)")
    GPIO.output(CHARGE_PIN, 0)
    
    phase_start = time.time()
    while time.time() - phase_start < PHASE_DURATION:
        current_time = time.time() - global_start_time
        try:
            voltage = adc.get_voltage()
            voltage_values.append(voltage)
            time_values.append(current_time)
            
            # Живой вывод напряжения и времени в консоль
            print(f"\rВремя: {current_time:.1f} с | Напряжение: {voltage:.3f} В", end='', flush=True)
            
        except OSError:
            pass
        time.sleep(0.01)

    print("\n\nЭксперимент завершен. Сохранение данных...")
    data = np.column_stack((time_values, voltage_values))
    np.savetxt('data.csv',
               data,
               delimiter=',',
               fmt='%.4f',
               header='Время[с],Напряжение[В]',
               comments='',
               encoding='utf-8')
    print("Файл data.csv успешно создан!")

finally:
    GPIO.output(CHARGE_PIN, 0)
    GPIO.cleanup()
    adc.deinit()