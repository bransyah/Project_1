import dht
import network
import ntptime
import ujson
import utime

from machine import RTC
from machine import Pin
from time import sleep
from third_party import rd_jwt

from umqtt.simple import MQTTClient


# Konstanta-konstanta aplikasi

# WiFi AP Information
AP_SSID = "MMM"
AP_PASSWORD = "12345678"

# Decoded Private Key
PRIVATE_KEY = (29471211465351718858154063155451935159804450451984894558618654542896357793640267550728794801462090229813158102513240077354672338330816662340442835925286450856074840533303115815706297189132550064197105598927295383048995200154400217305898360131128255627143861566706112968555008829637935278011369121716302054527330580325077300863094167336860677633672055120968786835741887431686508827146925679480490687717619760276340079542076848485287283813437617878151679452226027163299463152443175997377272340275012097076347785726197251478859174264695115658095559194950218155142763842510383153719406606581607431580297342443949979485829, 65537, 1529839043671918878731710680300402572800932914806179887520342138867104219203872472154345788097929886351593204827044917270558543952293182252501434728745968015203115911535425790088542701640736306489441891565843094635590302743873987812604577889834724287708369578252501584128418146061434850783445652869048927926221987801651446626087470354206719290776407227532295981927323931713062962216824029941070309870420181903980014406816181162583864728556290207503357752127061291930696200397267374032218264485788962879085018346822598789756152752303382306281017678874159474141547868506351749123482569225944703032226429340040150222337, 174578944576760249506650252451292757466470264603180849140461295779040498317108208279447787506979488483764197325127519362129750402864177237757961695669238372192619120526785715303616836577962286821537283862377824982449575206491062229783499317802795494572747853701092927434966534943271874905075114653889096683973, 168813092190470791749026607147256081492651149491978188961500059282245708370088943791306010740408801645268943892577763910853376233796958768216305351750434914192665053246280966391854092878369251699080094046149627294690321301676491345202402140411446923705047541336987292038209284054344374246349946879357965364673)


#Project ID of IoT Core
PROJECT_ID = "hsc2020-04"
# Location of server
REGION_ID = "asia-east1"
# ID of IoT registry
REGISTRY_ID = "esp_coba"
# ID of this device
DEVICE_ID = "esp32"

# MQTT Information
MQTT_BRIDGE_HOSTNAME = "mqtt.googleapis.com"
MQTT_BRIDGE_PORT = 8883


dht22_obj = dht.DHT22(Pin(4))
led_obj = Pin(23, Pin.OUT)
def suhu_kelembaban():
    # Read temperature from DHT 22
    #
    # Return
    #    * List (temperature, humidity)
    #    * None if failed to read from sensor
    while True:
        try:
            dht22_obj.measure()
            return dht22_obj.temperature(),dht22_obj.humidity()
            sleep(3)
            break
        except:
            return None
def connect():
    # Connect to WiFi
    print("Connecting to WiFi...")
    
    # Activate WiFi Radio
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # If not connected, try tp connect
    if not wlan.isconnected():
        # Connect to AP_SSID using AP_PASSWORD
        wlan.connect(AP_SSID, AP_PASSWORD)
        # Loop until connected
        while not wlan.isconnected():
            pass
    
    # Connected
    print("  Connected:", wlan.ifconfig())


def set_time():
    # Update machine with NTP server
    print("Updating machine time...")

    # Loop until connected to NTP Server
    while True:
        try:
            # Connect to NTP server and set machine time
            ntptime.settime()
            # Success, break out off loop
            break
        except OSError as err:
            # Fail to connect to NTP Server
            print("  Fail to connect to NTP server, retrying (Error: {})....".format(err))
            # Wait before reattempting. Note: Better approach exponential instead of fix wiat time
            utime.sleep(0.5)
    
    # Succeeded in updating machine time
    print("  Time set to:", RTC().datetime())


def on_message(topic, message):
    print((topic,message))


def get_client(jwt):
    #Create our MQTT client.
    #
    # The client_id is a unique string that identifies this device.
    # For Google Cloud IoT Core, it must be in the format below.
    #
    client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(PROJECT_ID, REGION_ID, REGISTRY_ID, DEVICE_ID)
    client = MQTTClient(client_id.encode('utf-8'),
                        server=MQTT_BRIDGE_HOSTNAME,
                        port=MQTT_BRIDGE_PORT,
                        user=b'ignored',
                        password=jwt.encode('utf-8'),
                        ssl=True)
    client.set_callback(on_message)

    try:
        client.connect()
    except Exception as err:
        print(err)
        raise(err)

    return client


def publish(client, payload):
    # Publish an event
    
    # Where to send
    mqtt_topic = '/devices/{}/{}'.format(DEVICE_ID, 'events')
    
    # What to send
    payload = ujson.dumps(payload).encode('utf-8')
    
    # Send    
    client.publish(mqtt_topic.encode('utf-8'),
                   payload,
                   qos=1)
    
    
def subscribe_command2():
    print("Sending command to device")
    client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(PROJECT_ID, REGION_ID, REGISTRY_ID, DEVICE_ID)
    #ukur = f"/devices/{DEVICE_ID}/commands/#"
    command = 'Baca Suhu'
    data = command.encode("utf-8")
    while True:
        dht22_obj.measure()
        temp = dht22_obj.temperature()
        print(temp)
        sleep(3)
    publish(client, temp)
# Connect to Wifi
connect()
# Set machine time to now
set_time()

# Create JWT Token
print("Creating JWT token.")
start_time = utime.time()
jwt = rd_jwt.create_jwt(PRIVATE_KEY, PROJECT_ID)
end_time = utime.time()
print("  Created token in", end_time - start_time, "seconds.")

# Connect to MQTT Server
print("Connecting to MQTT broker...")
start_time = utime.time()
client = get_client(jwt)
end_time = utime.time()
print("  Connected in", end_time - start_time, "seconds.")

# Read from DHT22
#print("Reading from DHT22")
#result1 = suhu_kelembaban()
#print("Suhu dan Kelembaban ", result1)
# Publish a message
#print("Publishing message...")
#if result1 == None:
 # result1 = "Fail to read sensor...."


#publish(client, result1)
# Need to wait because command not blocking
utime.sleep(1)

# Disconnect from client
client.disconnect()
#publish_events()
#publish_state()
#subscribe_config()
#subscribe_command()
#subscribe_command1()
subscribe_command2()
#subscribe_command3()

