########################################
# Функции для работы с измерителем на Raspberry Pi Pico 2
#
# Pico подключён к Raspberry Pi по SPI. Перед работой:
#   raspi-gpio set 9 a0
#   raspi-gpio set 10 a0
#   raspi-gpio set 11 a0
#
#   initPico()       - открыть SPI и выбрать Pico, один раз в начале
#   capture()        - дождаться хлопка и вернуть записи двух микрофонов
#   deinitPico()     - закрыть SPI, один раз в конце, в блоке finally
########################################

import time
import RPi.GPIO as GPIO
import spidev
import numpy as np

SPI_CS = 8
spi = spidev.SpiDev()


def initPico():
    spi.open(0, 0)
    spi.mode = 0
    spi.max_speed_hz = 10000
    spi.no_cs = True    # CS управляется вручную

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SPI_CS, GPIO.OUT)

    # Сбросить прошлый обмен и выбрать Pico
    GPIO.output(SPI_CS, 1)
    time.sleep(0.06)
    GPIO.output(SPI_CS, 0)


def deinitPico():
    GPIO.output(SPI_CS, 1)
    GPIO.cleanup()
    spi.close()


def readAnswer():
    # Ответ Pico: "SND2", длина (4 байта), CRC (4 байта), данные
    start = b""
    while start != b"SND2":
        start = (start + bytes(spi.xfer2([0])))[-4:]

    header = bytes(spi.xfer2([0] * 8))
    size = int.from_bytes(header[:4], "little")

    data = bytearray()
    while len(data) < size:
        data.extend(spi.xfer2([0] * min(64, size - len(data))))
    return bytes(data)


def capture(threshold=20, timeoutMs=15000):
    # Команда Pico: ждать хлопка и записать оба микрофона
    spi.xfer2(list(("capture %d %d\n" % (threshold, timeoutMs)).encode()))
    print(readAnswer().decode())
    print("Хлопайте!")

    # Pico присылает строку с настройками, затем отсчёты: мик. 0, мик. 1, мик. 0, ...
    answer = readAnswer()
    header, _, payload = answer.partition(b"\n")
    print(header.decode())

    samples = np.frombuffer(payload, dtype="<u2").reshape(-1, 2)
    return samples[:, 0], samples[:, 1]
