from modbus_conn import Modbus_Conn, ModbusRegisterType
from mqtt_conn import MQTT_Conn
import time
import logging
import sys

#Hint:
#If you want to have more then one file with loops, you may need to add this import
import plc_threading

# Logging Configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log", mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

#Hint:
#Here we create all different MQTT and Modbus Connection objects. Be aware, you may need more then one
mqtt_topic_root = "plc/"
mqtt_conn = MQTT_Conn()
modbus_conn = Modbus_Conn()

#Hint:
#Use Function (it can be more then one) to configure everything before running the loops
#Note the "@plc_threading.plc_init_func()" <-- every function with that "decorator" is used as init
@plc_threading.plc_init_func()
def _plc_init() -> None:
    mqtt_conn.connect(ip="127.0.0.1", port=1883, username="plc", password="plc")    
    mqtt_conn.sub_topic(mqtt_topic_root + "foobar")
    modbus_conn.connect_tcp("127.0.0.1")

#Hint:
#Use Function (it can be more then one) to define your wanted behaviour of the SoftPLC
#Note the "@plc_threading.plc_loop_func(time)" <-- every function with that "decorator" is used as loop. the time notes the loop time you want to run
@plc_threading.plc_loop_func(3)
def _plc_loop() -> None:
    logging.debug("_plc_loop: Did a loop")    
    #time.sleep(5) #this is just a test to see what happens if you loop is longer then the "loop time"

    # get data
    success, dat = modbus_conn.get_data(0,ModbusRegisterType.HOLDING_REGISTER)
    if success:
        mqtt_conn.pub_topic(mqtt_topic_root + "measurement", str(dat))

@plc_threading.plc_loop_func(5)
def _plc_loop2() -> None:
    logging.debug("_plc_loop2: did the other loop")

    # get data
    success, dat = modbus_conn.get_data(1,ModbusRegisterType.HOLDING_REGISTER)
    if success:
        mqtt_conn.pub_topic(mqtt_topic_root + "measurement", str(dat))
        
@plc_threading.plc_loop_func(0)
def _plc_mqttsub() -> None:
    logging.debug("_plc_mqtt_sub: arm the subscribe loop")    
    dat = mqtt_conn.get_data(mqtt_topic_root + "foobar")
    logging.debug("_plc_mqtt_sub: Got trigger with data: " + str(dat))

# Hint:
# Unfortuantely only one get_data is working currently, at least if the payload is important
# @plc_threading.plc_loop_func(0)
# def _plc_mqttsub2() -> None:
#     logging.debug("_plc_mqtt_sub2: arm the subscribe loop")    
#     dat = mqtt_conn.get_data(mqtt_topic_root + "foobar")
#     logging.debug("_plc_mqtt_sub2: Got trigger with data: " + str(dat))


#Hint: don't change things in here :)
if __name__ == "__main__":
    plc_threading.run_init_funcs()
    plc_threading.start_loop_threads()
    plc_threading.finish_loop_threads()
