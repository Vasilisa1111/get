import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
led = 26
GPIO.setup(led, GPIO.OUT)
button = 6
GPIO.setup(button, GPIO.IN)
state = 0
period = 0.2
while True: 
    sensor_state = GPIO.input(button)
    GPIO.output(led, not sensor_state)
