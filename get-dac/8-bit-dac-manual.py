import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
bits = [22, 27, 17, 26, 25, 21, 20, 16]
GPIO.setup(bits, GPIO.OUT)
dynamic_range=3.3