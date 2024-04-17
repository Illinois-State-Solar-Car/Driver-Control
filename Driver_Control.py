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
reverse = digitalio.DigitalInOut(board.GP20)
reverse.pull= digitalio.Pull.UP

#Maximum RPM value
omega =0

#digital forward init
forward = digitalio.DigitalInOut(board.GP19)
forward.pull = digitalio.Pull.UP

#digital regen init
regen = digitalio.DigitalInOut(board.GP7)
regen.pull= digitalio.Pull.UP

#Analog value from the pedal
pot = AnalogIn(board.A0)
potPercent = 0

#The node id we are sending to the Motor Controller
NODE_ID = 0x501

#Initialize the CAN object, baudrate 500k, cpu clock
mcp = CAN(spi, cs, baudrate = 500000, crystal_freq = 16000000, silent = False)

"""
t = Timer(timeout=5)
next_message = None
message_num = 0
tire_diameter = 22
last_send = time.monotonic_ns()
"""


while True:
    
    
   #grab pot value
    potPercent = (pot.value/63500)
    if potPercent < .05 :
        potPercent = 0
    
    #model function to describe acceleration
    thrust = (pow(potPercent,1.75))*.9
   
   
       
    #reverse selected   
    if not reverse.value :
        alpha= thrust
        omega= - 1000


    #forward selected
    if not forward.value:
        omega = 1000
        alpha=potPercent

    #regen selected
    if not regen.value :
        alpha = thrust*.40
        omega = 0

    #neutral select
    if  forward.value and  reverse.value:
        alpha = 0
        omega = 0
       
    #print(potPercent)
    #print (omega)
   
    #sleep(.1)

    #Constructor for the Message object(packing two floats(%,maxrpm))
    message = Message(id=0x501, data=struct.pack('<ff',omega,alpha), extended=False)
    
    #wait a little bit until you send another message
    while time.monotonic_ns() - last_send < 100000000:
        pass
        

    #send the message
    send_success = mcp.send(message)


    print("message sent after {}s".format((time.monotonic_ns()-last_send)*10**-9))
    print(send_success)
    
    last_send = time.monotonic_ns()

    '''
    with mcp.listen(matches = [Match(0x400,mask = 0xFF0)], timeout=0) as listener:
       
       
       
       
        message_count = listener.in_waiting()

       
        if message_count == 0:
           continue

        next_message = listener.receive()
        message_num = 0
        while not next_message is None:
            message_num += 1

             # Check the id to properly unpack it
            #if next_message.id == 0x402:

            #unpack and print the message
               # holder = struct.unpack('<ff',next_message.data)
                #print(holder)

            if next_message.id == 0x403:

                #unpack and print the message
                holder = struct.unpack('<ff',next_message.data)
                rpm = holder[0]
                mph = rpm*tire_diameter*math.pi*(60/63360)
                print(mph)
               
            next_message = listener.receive()
            #if next_message.id == 0x40e:
           
                #holder = struct.unpack('<ff',next_message.data)
                #odometer = holder[0]
                #milesTraveled = 0.000621371*odometer
                #print("Miles = "+((str)milesTraveled))
            #ampHours = holder[1]
            #print("AmpHrs = "+ampHours)
            # Read another message why not... if no messages are avaliable None is returned
            '''
