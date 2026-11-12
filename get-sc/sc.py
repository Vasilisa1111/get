import time
import numpy as np
import RPi.GPIO as GPIO
import mcp3021_driver

# ==========================================
# НАСТРОЙКИ ЭКСПЕРИМЕНТА (Вводите данные здесь)
# ==========================================
CHARGE_PIN = 14
DYNAMIC_RANGE = 5.1      # Фактическое напряжение на пине питания АЦП (В)
CHECK_INTERVAL = 2.7     # Как часто проверять "полочку" (в секундах)
VOLTAGE_TOLERANCE = 0.015 # Допустимое изменение напряжения на "полочке" (В)
# ==========================================

GPIO.setmode(GPIO.BCM)
GPIO.setup(CHARGE_PIN, GPIO.OUT)
adc = mcp3021_driver.MCP3021(DYNAMIC_RANGE)

time_values = []
voltage_values = []

def safe_read_adc():
    """Считывает АЦП, игнорируя единичные сбои шины I2C (Remote I/O error)"""
    while True:
        try:
            return adc.get_voltage()
        except OSError:
            time.sleep(0.005)

try:
    global_start = time.time()
    
    # --- ФАЗА 1: ЗАРЯДКА ---
    print("--- ФАЗА 1: ЗАРЯДКА ---")
    GPIO.output(CHARGE_PIN, 1)
    
    last_check_time = time.time()
    last_voltage = safe_read_adc()
    
    while True:
        voltage = safe_read_adc()
        current_time = time.time() - global_start
        
        voltage_values.append(voltage)
        time_values.append(current_time)
        print(f"\rВремя: {current_time:.1f} с | Напряжение: {voltage:.3f} В", end='', flush=True)
        
        # Умная остановка: если за CHECK_INTERVAL напряжение выросло меньше чем на VOLTAGE_TOLERANCE
        if time.time() - last_check_time >= CHECK_INTERVAL:
            if abs(voltage - last_voltage) < VOLTAGE_TOLERANCE:
                print(f"\n[!] Конденсатор заряжен (полочка достигнута). Переключение фазы...")
                break
            last_check_time = time.time()
            last_voltage = voltage
            
        time.sleep(0.01) # Защита от перегрузки шины

    # --- ФАЗА 2: РАЗРЯДКА ---
    print("\n--- ФАЗА 2: РАЗРЯДКА ---")
    GPIO.output(CHARGE_PIN, 0)
    
    last_check_time = time.time()
    last_voltage = safe_read_adc()
    
    while True:
        voltage = safe_read_adc()
        current_time = time.time() - global_start
        
        voltage_values.append(voltage)
        time_values.append(current_time)
        print(f"\rВремя: {current_time:.1f} с | Напряжение: {voltage:.3f} В", end='', flush=True)
        
        if time.time() - last_check_time >= CHECK_INTERVAL:
            if abs(voltage - last_voltage) < VOLTAGE_TOLERANCE:
                print(f"\n[!] Конденсатор разряжен.")
                break
            last_check_time = time.time()
            last_voltage = voltage
            
        time.sleep(0.01)

    # --- СОХРАНЕНИЕ ---
    print("\nЭксперимент завершен. Запись в файл...")
    data = np.column_stack((time_values, voltage_values))
    np.savetxt('data.csv',
               data,
               delimiter=',',
               fmt='%.4f',
               header='Время[с],Напряжение[В]',
               comments='',
               encoding='utf-8')
    print("Файл data.csv успешно сохранен!")

finally:
    GPIO.output(CHARGE_PIN, 0)
    GPIO.cleanup()
    adc.deinit()