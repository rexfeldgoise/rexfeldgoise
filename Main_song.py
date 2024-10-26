import time
import network
import uasyncio as asyncio  
from machine import Pin, ADC
from BLE_CEEO import Yell
from mqtt import MQTTClient


pause = False
enable = True
volume = True


def wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('Tufts_Robot', '')
    
    while wlan.ifconfig()[0] == '0.0.0.0':
        print('.', end=' ')
        time.sleep(1)
    
    print(wlan.ifconfig())

def conect_garage_band():

    p = Yell('Rex', verbose=True, type='midi')
    p.connect_up()
    return p

def callback_2(topic, msg):
    command = msg.decode()
    print((topic.decode(), msg.decode()))
    if command == 'start':

        global enable 
        enable = True
    if command == 'stop':
        global enable
        enable = False 

async def main_mqtt():

    mqtt_broker = 'broker.hivemq.com' 
    port = 1883
    topic_sub = 'ME35-24/Rex'
    
    client = MQTTClient('ME35_Rexs', mqtt_broker , port, keepalive=60)
    client.connect()
    client.set_callback(callback_2)
    client.subscribe(topic_sub.encode())
    
    while True:
        client.check_msg()
        await asyncio.sleep(0.01) 


def callback_3(topic, msg):
    command_2 = msg.decode()
    print((topic.decode(), msg.decode()))
    if command_2 == 'Class 3':
        global volume 
        volume = False
    if command_2 == 'Class 4':
        global volume
        volume = True 

async def TM_mqtt():

    mqtt_broker = 'broker.hivemq.com' 
    port = 1883
    topic_sub = 'ME35-24/Rex_2'
    
    client = MQTTClient('ME35_Rexs_2', mqtt_broker , port, keepalive=60)
    client.connect()
    client.set_callback(callback_3)
    client.subscribe(topic_sub.encode())
    
    while True:
        client.check_msg()
        await asyncio.sleep(0.01) 

async def play_song(p):



    NoteOn = 0x90
    NoteOff = 0x80
    velocity = {'off': 0, 'pppp': 8, 'ppp': 20, 'pp': 31, 'p': 42, 'mp': 53,
                'mf': 64, 'f': 80, 'ff': 96, 'fff': 112, 'ffff': 127}


    channel = 0x0F & 0  
    cmd = NoteOn
    timestamp_ms = time.ticks_ms()
    tsM = (timestamp_ms >> 7 & 0b111111) | 0x80
    tsL = 0x80 | (timestamp_ms & 0b1111111)

    c = cmd | channel  

    def play_chord(notes):
        for note in notes:
            payload = bytes([tsM, tsL, c, note, velocity['f']])
            p.send(payload)

    # def play_chord(notes):
    #     for note in notes:
    #         if volume == False:
    #             payload = bytes([tsM, tsL, c, note, velocity['f']])
    #             p.send(payload)
    #         if volume == True:
    #             payload = bytes([tsM, tsL, c, note, velocity['ffff']])
    #             p.send(payload)

    # Sensors setup
    pin_1 = Pin('GPIO10', Pin.IN)
    pin_2 = Pin('GPIO9', Pin.IN)
    pin_3 = Pin('GPIO8', Pin.IN)

    # Chords (C major, F major, G major)
    C_major = [60, 64, 67]  # C, E, G
    F_major = [65, 69, 72]  # F, A, C
    G_major = [67, 71, 74]  # G, B, D

    while True:
        val_1 = pin_1.value()
        val_2 = pin_2.value()
        val_3 = pin_3.value()

        
        if pause == True or enable == False:
            print("in here")
            await asyncio.sleep(0.01)

        else:


            if val_1 == 1:
                print("Sensor 1 detected vibration! Playing C Major.")
                play_chord(C_major)


                pin1 = Pin('GPIO13', Pin.OUT)
                pin1.on()
                await asyncio.sleep(1)
                pin1.off()
                
                await asyncio.sleep(0.01)

            if val_2 == 1:
                print("Sensor 2 detected vibration! Playing F Major.")
                play_chord(F_major)

                pin2 = Pin('GPIO12', Pin.OUT)
                pin2.on()
                await asyncio.sleep(1)
                pin2.off()

                await asyncio.sleep(0.01)

            if val_3 == 1:
                print("Sensor 3 detected vibration! Playing G Major.")
                play_chord(G_major)

                pin3 = Pin('GPIO11', Pin.OUT)
                pin3.on()
                await asyncio.sleep(1)
                pin3.off()

                


                await asyncio.sleep(0.01)

        await asyncio.sleep(0.01)


async def photo_resistor():
 
    photoresistor_pin = ADC(Pin(26))  

    while True:
        light_level = photoresistor_pin.read_u16() 


        if light_level < 40000:
            global pause
            pause = True
        
        else:
            global pause
            pause = False

        
        await asyncio.sleep(0.01) 


async def main():
    wifi()
    p = conect_garage_band()

    asyncio.create_task(play_song(p))
    asyncio.create_task(photo_resistor())
    #asyncio.create_task(TM_mqtt())
    #asyncio.create_task(main_mqtt())
    


    while True:
        await asyncio.sleep(0.01)

    p.disconnect()
asyncio.run(main())

