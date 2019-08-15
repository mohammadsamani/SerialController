from multiprocessing import Queue
import datetime, time, serial

from error import RecordError
import config

# command is expected to be an array
# element 0 is the index of the source, for the source's sake
# element 1 the type of command. "R" for read, "W" for write, and "Q" for query
# element 2 is the command. One command at a time.
def Communicate(device_name, commandQ, responseQ):
	ser = serial.Serial(
		config.conf['Devices'][device_name]['SerialPort'],
		config.conf['Devices'][device_name]['Baudrate'],
		parity=config.conf['Devices'][device_name]['Parity'],
		stopbits=config.conf['Devices'][device_name]['Stopbits'],
		bytesize=config.conf['Devices'][device_name]['Bytesize'],
		)
	while True:
		command = commandQ.get()
		source_id = command[0]		# who ever put the request will use this to identify its response
		cmd_type = command[1]
		cmd = command[2]
		if cmd_type == "R":
			read = SerialRead(device_name, ser, cmd)
			responseQ.put([source_id, read])
		elif cmd_type == "W":
			WriteSerial(device_name, ser, cmd)
			responseQ.put([source_id, "OK"])
		elif cmd_type == "Q":
			read = QuerySerial(device_name, ser, cmd)
			responseQ.put([source_id, read])
		
		time.sleep(config.conf['Devices'][device_name]['MinDelay'])

def WriteSerial(device_name, ser, cmd):
	try:
		cmd = cmd + config.conf['Devices'][device_name]['Terminator']
		ser.write(bytearray(cmd, 'ascii'))
	except Exception as x:
		RecordError("Error during WriteSerial {0}. Device name: {1}. Commands: {2}".format(x, device_name, cmd))

def ReadSerial(device_name, ser):
	try:
		# Read from serial port
		term = config.conf['Devices'][device_name]['Terminator']
		return ser.readline()[:-1*len(term)]
	except Exception as x:
		RecordError("Error during ReadSerial {0}. Device name: {1}.".format(x, device_name))
	
def QuerySerial(device_name, ser, msg):
	WriteSerial(device_name, ser, msg)
	return ReadSerial(device_name, ser)
