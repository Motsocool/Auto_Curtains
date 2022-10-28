import rp2
import network, urequests, utime, machine
import ubinascii
import socket
import time
from machine import Pin, Timer, RTC
from secrets import secrets
from picozero import pico_temp_sensor, pico_led
from utime import sleep
from time import sleep

led_on_board = Pin("LED", Pin.OUT)
CLOSE = Pin(14, Pin.IN)	# Curtain Status
OPEN = Pin(15, Pin.IN)	# Curtain Status
SIG = Pin(16, Pin.IN)	# Manual Control
EN = Pin(18, Pin.OUT)	# Enable GPIO Pin. Inverted values.
DIR = Pin(19, Pin.OUT)	# Direction GPIO Pin
STEP = Pin(20, Pin.OUT)	# Step GPIO Pin
SPR = 200				# Steps/rotation = 360/1.8 (degrees)
CW = 1					# Used with DIR to determine which way to rotate.
CCW = 0					# Used with DIR to determine which way to rotate.

step_count = SPR*1		# Steps requested. SPR*x x=# of rotations.
delay = 0.01			# Speed of steps per rotation.

#change to your country code as applicable
rp2.country('CA')

#WiFi credentials
ssid = secrets["ssid"]
pw  = secrets["pw"]

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, pw)

# If you need to disable powersaving mode
wlan.config(pm = 0xa11140)

# See the MAC address in the wireless chip OTP
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('mac = ' + mac)

# Other things to query
# print(wlan.config('channel'))
# print(wlan.config('essid'))
# print(wlan.config('txpower'))
    
# Wait for connection with 10 second timeout
timeout = 10
while timeout > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    timeout -= 1
    print('Waiting for connection...')
    time.sleep(1)

        #not my original work
# Define blinking function for onboard LED to indicate error codes    
def blink_onboard_led(num_blinks):
    for i in range(num_blinks):
        led_on_board.on()
        time.sleep(.2)
        led_on_board.off()
        time.sleep(.2)
    
# Handle connection error
# Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth

wlan_status = wlan.status()
blink_onboard_led(wlan_status)

if wlan_status != 3:
    raise RuntimeError('Wi-Fi connection failed')
else:
    print('Connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])
    led_on_board.on()

#WAN ipAddress = 142.165.122.98
ipAddress = status[0]
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

url = "http://worldtimeapi.org/api/timezone/America/Swift_Current" # see http://worldtimeapi.org/timezones
web_query_delay = 60000 # interval time of web JSON query
retry_delay = 5000 # interval time of retry after a failed Web query

rtc = machine.RTC()
# set timer
update_time = utime.ticks_ms() - web_query_delay

# main loop
while True:
    
    # if lose wifi connection, reboot Pico W
    if not wlan.isconnected():
        machine.reset()
    
    # query and get web JSON every web_query_delay ms
    if utime.ticks_ms() - update_time >= web_query_delay:
    
        # HTTP GET data
        response = urequests.get(url)
    
        if response.status_code == 200: # query success
        
            print("JSON response:\n", response.text)
            
            # parse JSON
            parsed = response.json()
            day_of_week_str = str(parsed["day_of_week"])
            day_of_year_str = str(parsed["day_of_year"])
            datetime_str = str(parsed["datetime"])
            year = int(datetime_str[0:4])
            month = int(datetime_str[5:7])
            day = int(datetime_str[8:10])
            hour = int(datetime_str[11:13])
            minute = int(datetime_str[14:16])
            second = int(datetime_str[17:19])
            subsecond = int(round(int(datetime_str[20:26]) / 10000))
        
            # update internal RTC
            rtc.datetime((year, month, day, 0, hour, minute, second, subsecond))
            update_time = utime.ticks_ms()
            print("RTC updated\n")
   
        else: # query failed, retry retry_delay ms later
            update_time = utime.ticks_ms() - web_query_delay + retry_delay
    
    # generate formated date/time strings from internal RTC
    date_str = "Date: {1:02d}/{2:02d}/{0:4d}".format(*rtc.datetime())
    time_str = "Time: {4:02d}:{5:02d}:{6:02d}".format(*rtc.datetime())
    day_of_month_str = "Date: {1:02d}/{2:02d}".format(*rtc.datetime())
    
    utime.sleep(0.1)
#    print(hour)	#Test date variables.


EN.value(1)  		# high is stop
DIR.value(1)     # high is CCW looking down on shaft

def Open():
    if OPEN == True:
        EN.value(1)
    if CLOSE == True:
        DIR.value(CW)
        EN.value(0)
        
def Close():
    if CLOSE == True:
        EN.value(1)
    if OPEN == True:
        DIR.value(CCW)
        EN.value(0)
    
def Holidays():
    day_of_month_str == 01/01 or 02/21 or 04/15 or 05/23 or 07/01 or 08/01 or 09/05 or 10/10 or 12/25

def Weekday():
    for d in range(0, 5, 1):
        if Holiday == True:
            return False
        if day_of_month_str == [d]
        
def Weekend():
    for e in range(7, 0, -1):
        if day_of_month_str = [e]:
            if Holiday == True:
                return False
            if Weekday == True:
                return False
            if Weekday == False:
                return True
    
def Late_Months():
    month = 01 or 02 or 03 or 11 or 12:
        return True
    
def Early_Months():
    for m in range(03, 10, 1):
        if month = [m]:
            return True

def Sunrise():
    if Weekday == True:
        if Late_Months == True:		# Sunrise is at or before 8A.M. these months.
            if hour == 08
        if Early_Months == True:	# Sunrise is at or before 6A.M. these months.
            if hour == 06:
                return True
    if Weekend == True:
        if hour == 09:
            return True
    if Holidays == True:
        if hour == 09:
            return True
            
def Sunset():
    if hour == 21:
        return True
        
while True:
    try:
        if SIG == True:
            if OPEN == True:
                DIR.value(CCW)
                EN.value(0)
            if CLOSE == True:
                DIR.value(CW)
                EN.value(0)
        if Sunrise == True:
            Open()
        if Sunset == True:
            Close()