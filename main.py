import plc_threading
from modbus import Modbus, ModbusRegisterType
from mqtt import MQTT

import time

# Just some objects 
mqtt_conn = MQTT()
modbus_conn = Modbus()


@plc_threading.plc_init_func()
def _plc_init():
    mqtt_conn.connect("127.0.0.1")
    modbus_conn.connect("127.0.0.1")

@plc_threading.plc_loop_func(3)
def _plc_loop():
    print("did a loop")
    time.sleep(5)

    # get data
    success, dat = modbus_conn.get_data(0,ModbusRegisterType.HOLDING_REGISTER)
    if success:
        mqtt_conn.pub_topic("cocytos/measurement", str(dat))

@plc_threading.plc_loop_func(5)
def _plc_loop2():
    print("did the other loop")

    # get data
    success, dat = modbus_conn.get_data(0,ModbusRegisterType.HOLDING_REGISTER)
    if success:
        mqtt_conn.pub_topic("cocytos/measurement", str(dat))

if __name__ == "__main__":
    plc_threading.run_init_funcs()
    plc_threading.start_loop_threads()
    plc_threading.finish_loop_threads()
