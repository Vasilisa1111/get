import RPi.GPIO as GPIO 
import time
GPIO.setmode(GPIO.BCM)
led = 26
GPIO.setup(led, GPIO.OUT)
button = 13
GPIO.setup(button, GPIO.IN)
state = 0
period = 0.2
while True:   
    if GPIO.input(button):  
        state = 1-state 
        GPIO.output(led, state)
        time.sleep(period)