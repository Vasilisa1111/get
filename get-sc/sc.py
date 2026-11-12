import time
import numpy as np
import RPi.GPIO as GPIO
import mcp3021_driver

# ==========================================
CHARGE_PIN = 17
DYNAMIC_RANGE = 4.0      # Измеренное напряжение на пине питания АЦП (В)
TARGET_PERCENT = 0.95    # Академический предел (95% от максимума)
# ==========================================

GPIO.setmode(GPIO.BCM)
GPIO.setup(CHARGE_PIN, GPIO.OUT)
adc = mcp3021_driver.MCP3021(DYNAMIC_RANGE)

time_values = []
voltage_values = []

def safe_read_adc():
    while True:
        try:
            return adc.get_voltage()
        except OSError:
            time.sleep(0.005)

try:
    print("--- ШАГ 1: АНАЛИЗ ФИЗИЧЕСКИХ ПРЕДЕЛОВ ЦЕПИ ---")
    # 1. Быстро находим текущий реальный ноль
    GPIO.output(CHARGE_PIN, 0)
    time.sleep(3.0) # Даем остаткам стечь
    U_min = safe_read_adc()
    
    # 2. Находим реальный максимум по "полочке" (без жестких таймеров)
    GPIO.output(CHARGE_PIN, 1)
    print("Ищем фактический U_max (ждем выхода на полочку)...")
    last_check_time = time.time()
    last_voltage = safe_read_adc()
    U_max = last_voltage
    
    while True:
        voltage = safe_read_adc()
        print(f"\rНапряжение: {voltage:.3f} В", end='', flush=True)
        if time.time() - last_check_time >= 2.0:
            if abs(voltage - last_voltage) < 0.015:
                U_max = voltage
                break
            last_check_time = time.time()
            last_voltage = voltage
        time.sleep(0.01)

    # 3. Вычисляем пороги остановки (95% для заряда, 5% для разряда)
    voltage_range = U_max - U_min
    charge_threshold = U_min + (voltage_range * TARGET_PERCENT)
    discharge_threshold = U_min + (voltage_range * (1.0 - TARGET_PERCENT))
    
    print(f"\n[!] Калибровка: U_min = {U_min:.3f} В, U_max = {U_max:.3f} В")
    print(f"[!] Целевые пороги: Заряд до {charge_threshold:.3f} В, Разряд до {discharge_threshold:.3f} В\n")

    # Сбрасываем конденсатор перед чистым замером
    print("Сброс заряда перед началом эксперимента...")
    GPIO.output(CHARGE_PIN, 0)
    while safe_read_adc() > discharge_threshold:
        time.sleep(0.1)

    print("\n--- ШАГ 2: СБОР ДАННЫХ ---")
    global_start = time.time()
    
    # --- ФАЗА 1: ЗАРЯДКА ---
    print("ФАЗА 1: Зарядка...")
    GPIO.output(CHARGE_PIN, 1)
    voltage = safe_read_adc()
    while voltage < charge_threshold:
        voltage = safe_read_adc()
        current_time = time.time() - global_start
        voltage_values.append(voltage)
        time_values.append(current_time)
        print(f"\rВремя: {current_time:.1f} с | Напряжение: {voltage:.3f} В", end='', flush=True)
        time.sleep(0.01)

    # --- ФАЗА 2: РАЗРЯДКА ---
    print("\nФАЗА 2: Разрядка...")
    GPIO.output(CHARGE_PIN, 0)
    while voltage > discharge_threshold:
        voltage = safe_read_adc()
        current_time = time.time() - global_start
        voltage_values.append(voltage)
        time_values.append(current_time)
        print(f"\rВремя: {current_time:.1f} с | Напряжение: {voltage:.3f} В", end='', flush=True)
        time.sleep(0.01)

    # --- СОХРАНЕНИЕ ---
    print("\nЭксперимент завершен. Запись в файл data.csv...")
    data = np.column_stack((time_values, voltage_values))
    np.savetxt('data.csv',
               data,
               delimiter=',',
               fmt='%.4f',
               header='Время[с],Напряжение[В]',
               comments='',
               encoding='utf-8')
    print("Успешно!")

finally:
    GPIO.output(CHARGE_PIN, 0)
    GPIO.cleanup()
    adc.deinit()