from pirc522 import RFID
import RPi.GPIO as GPIO
from time import sleep
import urllib.request
import datetime
import urllib
import json
import time

GPIO.setwarnings(False)

def gpioControl(x):
    GPIO.setmode(GPIO.BOARD)
    #relay1 = 38
    machine = 7

    ledRed = 37 #green led for scan rfid
    ledGreen = 35 #red led for machine on
    #indicator = 31 
    masterCard = 33 #Yellow led for network problem scan Master RFID

    GPIO.setup(machine, GPIO.OUT)

    GPIO.setup(ledRed, GPIO.OUT)
    GPIO.setup(ledGreen, GPIO.OUT)
    #GPIO.setup(indicator, GPIO.OUT)
    GPIO.setup(masterCard, GPIO.OUT)

    #GPIO Initial Condition          
    if x == 1:
        #Initialy Machine is OFF (HIGH signal to relay card means relay is OFF)
        GPIO.output(machine, GPIO.HIGH)
        #Initialy Scan RFID LED is ON
        GPIO.output(ledRed, GPIO.HIGH)
        #scan master card is OFF
        GPIO.output(masterCard, GPIO.LOW)
        #Machine LED is OFF
        GPIO.output(ledGreen, GPIO.LOW)
        #Initialy System is Online indicator is ON
        #GPIO.output(indicator, GPIO.HIGH)
        #Initialy scan master card is OFF
        GPIO.output(masterCard, GPIO.LOW)
       
    #After SCAN RFID   
    elif x == 2:
        #RFID LED is OFF
        GPIO.output(ledRed, GPIO.LOW)
        #Machine LED is ON
        GPIO.output(ledGreen, GPIO.HIGH)
        #Machine is ON (LOW == ON)
        GPIO.output(machine, GPIO.LOW)
        #wait for 60 sec
        time.sleep(60)

    #Initial Scan master Card
    elif x == 4:
        #RFID LED is OFF
        GPIO.output(ledRed, GPIO.LOW)
        #scan master card is ON
        GPIO.output(masterCard, GPIO.LOW)
        #Machine LED is ON
        GPIO.output(ledGreen, GPIO.HIGH)
        #Machine is ON (LOW == ON)
        GPIO.output(machine, GPIO.LOW)
        time.sleep(50)
        
    #Scan master card indicator on after network problem detected  
    elif x == 5:
        #RFID LED is OFF
        GPIO.output(ledRed, GPIO.LOW)
        #scan master card is ON
        GPIO.output(masterCard, GPIO.HIGH)

    #After Time Match (4H cycle)
    elif x == 3:
        #Machine LED is OFF
        GPIO.output(ledGreen, GPIO.LOW)
        #Machine Is OFF (HIGH signal to Realy means OFF)
        GPIO.output(machine, GPIO.HIGH)
        #Scan RFID LED is ON
        GPIO.output(ledRed, GPIO.HIGH)
        #Machine LED is OFF
        GPIO.output(ledGreen, GPIO.LOW)
        #scan master card is OFF
        GPIO.output(masterCard, GPIO.LOW)
    elif x == 6:
        GPIO.output(ledRed, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(ledRed, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(ledRed, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(ledRed, GPIO.HIGH)
        
        
        

gpioControl(1)

rdr = RFID()

#base_url = "https://raspiinvent.com/rfid/"
machine_no = "1"
str1 = ""
myTime = ["1754", "0200", "0300", "0400", "0500", "0600", "0700", "0800", "0900", "1000", "1100", "1200", "1300", "1400", "1500", "1600", "1700", "1800"]
masterRFID = ["18713818333167", "1692417227188", "525424154", "5442145", "5745241564", "574521574", "5452157521", "5421574521", "545215274521"]

def log_in():
    try:
        if str1 in masterRFID and len(str1) > 5:
            print("Master card")
            gpioControl(4)
        elif len(str1) > 5:
            # print(str1)
            request = urllib.request.Request(
                "https://raspiinvent.com/logbook/admin/includes/services/machine-user-log-in.php?rfidno=%s" % (str1)+"&machine_no=%s" % (machine_no))
            json_data = urllib.request.urlopen(request).read()

            result = json.loads(json_data)
            auth = result["name"]

            if auth != "Unauthorised":
                print("Hello %s" % (auth))
                gpioControl(2)

            else:
                print("Unauthorised or Try Again")
                time.sleep(2)
                rdr = RFID()
                scan_rfid()
        else:
            print("Something went wrong scan again")
            gpioControl(6)
            rdr = RFID()
            scan_rfid()
    except:
            print("Network Problem")
            time.sleep(1)
            gpioControl(5)
            rdr = RFID()
            scan_rfid()

def log_out():
    try:
        request = urllib.request.Request(
            "https://raspiinvent.com/logbook/admin/includes/services/machine-user-log-out.php?rfidno=%s" % (str1)+"&machine_no=%s" % (machine_no))
        urllib.request.urlopen(request).read()
    except:
            print("Network Problem")
            rdr = RFID()
            scan_rfid()


def scan_rfid():
    global str1
    global uid
    str1 = ""
    uid = ""
    print("Scan RFID")
    rdr.wait_for_tag()
    (error, tag_type) = rdr.request()
    if not error:
        #print("Tag detected\n")
        (error, uid) = rdr.anticoll()
        if not error:
            print("UID: " + str(uid))
            if not rdr.select_tag(uid):
                if not rdr.card_auth(rdr.auth_a, 10, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], uid):
                    rdr.stop_crypto()
        sleep(0.5)
    rdr.cleanup()
    gpioControl(1)
    for i in uid:
        str1 += str(i)
    print(len(str1))
    log_in()

scan_rfid()

try:
    while True:
        try:
            timenow = datetime.datetime.now().strftime('%H%M')
            if timenow in myTime:
                gpioControl(3)
                log_out()
                rdr=RFID()
                scan_rfid()
            time.sleep(5)
        except:
            print("Network Problem")

except keyboardInterrupt:
    GPIO.cleanup()
