import time
import numpy as np
import RPi.GPIO as GPIO
import mcp3021_driver

# 1. Теоретические исходные данные цепи
R = 1_000_000  # 1 МОм
C = 10e-6      # 10 мкФ
TAU_TEOR = R * C  # Теоретическая постоянная времени (10 секунд)

CHARGE_PIN = 17
# Укажите измеренное напряжение на пине питания АЦП. 
# Благодаря автокалибровке небольшая погрешность здесь больше не сломает скрипт.
DYNAMIC_RANGE = 4.0 

GPIO.setmode(GPIO.BCM)
GPIO.setup(CHARGE_PIN, GPIO.OUT)
adc = mcp3021_driver.MCP3021(DYNAMIC_RANGE)

time_values = []
voltage_values = []

def safe_read_adc():
    """Считывает АЦП, игнорируя единичные ошибки шины I2C (Remote I/O error)"""
    while True:
        try:
            return adc.get_voltage()
        except OSError:
            time.sleep(0.005)

try:
    print("--- ФАЗА 0: АВТОКАЛИБРОВКА ЦЕПИ ---")
    print(f"Зарядка для определения U_max (ждем 5*tau = {TAU_TEOR * 5:.0f} с)...")
    GPIO.output(CHARGE_PIN, 1)
    time.sleep(TAU_TEOR * 5)  # Гарантированный выход на физическую асимптоту
    U_max = safe_read_adc()
    
    print(f"Разрядка для определения U_min (ждем 5*tau = {TAU_TEOR * 5:.0f} с)...")
    GPIO.output(CHARGE_PIN, 0)
    time.sleep(TAU_TEOR * 5)  # Гарантированный сброс до абсолютного нуля цепи
    U_min = safe_read_adc()
    
    print(f"[!] Калибровка завершена. Фактические пределы: {U_min:.3f} В — {U_max:.3f} В\n")

    # Вычисляем пороги для остановки записи (97% от размаха для заряда, 3% для разряда)
    voltage_range = U_max - U_min
    charge_threshold = U_min + (voltage_range * 0.97)
    discharge_threshold = U_min + (voltage_range * 0.03)


    print("--- ФАЗА 1: СБОР ДАННЫХ (ЗАРЯДКА) ---")
    global_start = time.time()
    GPIO.output(CHARGE_PIN, 1)
    
    voltage = U_min
    while voltage < charge_threshold:
        voltage = safe_read_adc()
        current_time = time.time() - global_start
        
        voltage_values.append(voltage)
        time_values.append(current_time)
        print(f"\rВремя: {current_time:.1f} с | Напряжение: {voltage:.3f} В", end='', flush=True)
        time.sleep(0.01)

    print("\n\n--- ФАЗА 2: СБОР ДАННЫХ (РАЗРЯДКА) ---")
    GPIO.output(CHARGE_PIN, 0)
    
    while voltage > discharge_threshold:
        voltage = safe_read_adc()
        current_time = time.time() - global_start
        
        voltage_values.append(voltage)
        time_values.append(current_time)
        print(f"\rВремя: {current_time:.1f} с | Напряжение: {voltage:.3f} В", end='', flush=True)
        time.sleep(0.01)

    print("\n\nЭксперимент завершен. Запись в файл...")
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