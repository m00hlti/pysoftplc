from enum import Enum

class ModbusRegisterType(Enum):
    COIL                = 1 #  1bit, read-write
    DISCRETE_INPUT      = 2 #  1bit, readonly
    INPUT_REGISTER      = 3 # 16bit, readonly
    HOLDING_REGISTER    = 4 # 16bit, read-write


class Modbus():
    def __init__(self):
        #inc_data = dict(str, list<str>)
        pass
    
    def connect(self, ip: str) -> bool: 
        # do all the cool connection stuff and reuturn True or False if successful or not
        return True
    
    def send_data(self, addr: int, register_type: ModbusRegisterType, data: int) -> bool:
        # do some cool stuff and send the data, return true if success else false
        return True  
    
    
    def get_data(self, addr: int, register_type: ModbusRegisterType) -> (bool, int):
        # do some cool stuff and check if the addr has some data and return it
        return True, 0