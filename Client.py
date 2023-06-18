from pyModbusTCP.client import ModbusClient

client = ModbusClient('192.168.178.102', port=12345)

client.open()