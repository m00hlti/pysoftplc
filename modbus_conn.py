from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder, Endian
from enum import Enum

class ModbusRegisterType(Enum):
    COIL                = 1 #  1bit, read-write
    DISCRETE_INPUT      = 2 #  1bit, readonly
    INPUT_REGISTER      = 3 # 16bit, readonly
    HOLDING_REGISTER    = 4 # 16bit, read-write


class Modbus_Conn():
    """
    Simple Wrapper to provide the wanted functionality for MQTTsour
    """
    def __init__(self):
        self.client = None

    def connect_tcp(self, ip: str, port: int = 502) -> bool: 
        # do all the cool connection stuff and reuturn True or False if successful or not
        if self.client is None:
            self.client = ModbusTcpClient(ip, port)
            return True
        else:
            return False        
    
    def connect_rtu(self, port: str) -> bool:
        if self.client is None:
            self.client = ModbusSerialClient(port)
            return True
        else:
            return False
        
    def disconnect(self) -> bool:
        self.client.close()
        return True
    
    def is_connected(self) -> bool:
        if self.client is not None:
            return self.client.is_socket_open()
        else:
            return False
    
    def _read_register(self, register_type: ModbusRegisterType, register: int, count: int =1):
        if register_type == ModbusRegisterType.COIL:
            payload = self.client.read_coils(register, count, slave =1)
        elif register_type == ModbusRegisterType.DISCRETE_INPUT:
            payload = self.client.read_discrete_inputs(register, count, slave =1)
        elif register_type == ModbusRegisterType.HOLDING_REGISTER:
            payload = self.client.read_holding_registers(register, count, slave =1)
        elif register_type == ModbusRegisterType.INPUT_REGISTER:
            payload = self.client.read_input_registers(register, count, slave =1)
        else:
            payload = None
        return payload

    def send_data(self, addr: int, register_type: ModbusRegisterType, data: int) -> bool:
        assert type(data) is int and 0 <= data < 16535
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
        builder.add_16bit_uint(data)
        registers = builder.to_registers()
        self.client.write_registers(addr, registers, slave=1)
        return True  
        
    def get_data(self, addr: int, register_type: ModbusRegisterType) -> (bool, int):
        payload = self._read_register(register_type, addr)
        if register_type == ModbusRegisterType.HOLDING_REGISTER or register_type == ModbusRegisterType.INPUT_REGISTER:
            decoder = BinaryPayloadDecoder.fromRegisters(payload.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        else:
            decoder = BinaryPayloadDecoder.fromCoils(payload.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        dat = decoder.decode_16bit_uint()
        return True, dat
    