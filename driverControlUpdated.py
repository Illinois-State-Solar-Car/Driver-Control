#updated driver control board
#last worked on: 3/23/2024
#Mason Myre

#UPDATES:
#Added some commenting
#Changed some variable names for the purposes of code clarity
#Introduced elif statements in favor of if statements to increase energy efficiency and speed
#Fixed the delay in message building and sending
    #Original way: build message -> wait -> send message
    #New way:      build message -> send message -> wait


import board
import busio
from analogio import AnalogIn
from time import sleep
import struct
import digitalio
from adafruit_mcp2515       import MCP2515 as CAN
from adafruit_mcp2515.canio import RemoteTransmissionRequest, Message, Match, Timer
import math
import time


# Initalize the SPI bus on the RP2040
# NOTE: Theses pins constant for all CAN-Pico Boards... DO NOT TOUCH
cs = digitalio.DigitalInOut(board.GP9)
cs.switch_to_output()
spi = busio.SPI(board.GP2, board.GP3, board.GP4)

#digital reverse init
reverse = digitalio.DigitalInOut(board.GP22)
reverse.pull= digitalio.Pull.UP

#Maximum RPM value
maxRPM = 0

#digital forward init
forward = digitalio.DigitalInOut(board.GP21)
forward.pull = digitalio.Pull.UP

#digital regen init
regen = digitalio.DigitalInOut(board.GP7)
regen.pull= digitalio.Pull.UP

#Analog value from the pedal
pedalPotentiometer = AnalogIn(board.A2)
potPercent = 0

#The node id we are sending to the Motor Controller
NODE_ID = 0x501

#Initialize the CAN object, baudrate 500k, cpu clock
mcp = CAN(spi, cs, baudrate = 500000, crystal_freq = 16000000, silent = False)


while True:
    
    
   #grab pot value
    potPercent = (pedalPotentiometer.value/63500)
    if potPercent < .05 :
        potPercent = 0
    
    #model function to describe acceleration
    #power function turns the linear potentiometer values into an exponential graph similar to gas cars
    thrust = (pow(potPercent,1.75))*.9
   
    #since we are doing pullups, we use the 'not' to determine which 'gear' is selected
    
    #forward selected
    if not forward.value:
        maxRPM = 1000
        maxRPMPercent = thrust
    
    #regen selected
    elif not regen.value :
        maxRPMPercent = thrust*.4
        maxRPM = 0
    
    #reverse selected   
    elif not reverse.value :
        maxRPMPercent= thrust
        maxRPM= - 1000

    #neutral select
    elif  forward.value and  reverse.value:
        maxRPMPercent = 0
        maxRPM = 0
       
    #print(potPercent)
    #print (maxRPM)
   
    #sleep(.1)

    #Constructor for the Message object(packing two floats(%,maxrpm))
    message = Message(id=0x501, data=struct.pack('<ff',maxRPM,maxRPMPercent), extended=False)
    
    #send the message
    send_success = mcp.send(message)

    
    #wait a little bit until we send another message
    while time.monotonic_ns() - last_send < 100000000:
        pass
        

    print("message sent after {}s".format((time.monotonic_ns()-last_send)*10**-9))
    print(send_success)
    
    last_send = time.monotonic_ns()

    #didn't think the commented out code down here was important but lmk if it was
