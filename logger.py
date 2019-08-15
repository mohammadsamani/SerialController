import time
import importlib

import db
import config
from error import RecordError

def log(device_names, commandQs, responseQs):
	last_logged = []
	for device_name in config.conf['Devices']:
		last_logged.append(0)
	
	last_reload = time.time()
	while True:
		# Reload the config file every now and then.
		if time.time() - last_reload > config.conf['ReloadPeriod']:
			importlib.reload(config)
			last_reload = time.time()
			
		for device_index, device_name in enumerate(config.conf['Devices']):
			period = config.conf['Devices'][device_name]['LogPeriod'] # Negative period means disable logging.
			if period > 0 and time.time() - last_logged[device_index] > period:
				# This device need to be logged
				log_device(commandQs, responseQs, device_name, device_index)
				last_logged[device_index] = time.time()
		
		time.sleep(config.conf['Logging']['SleepInLoop'])
				
def log_device(commandQs, responseQs, device_name, device_index):
	log_items = config.conf['Devices'][device_name]['LogItems']
	log_values = []
	my_id = 'logger'
	for key in log_items:
		cmd = log_items[key]
		commandQs[device_index].put([my_id, "Q", cmd])
		
		response = responseQs[device_index].get()
		attempts = 0
		while not response[0] == my_id and attempts < 1000:
			# Not a response to my query. Put it back in the queue.
			responseQs[device_index].put(response)
			# Hope the intended recipient will pick it up quickly
			time.sleep(random.randint(0,100)/1000)
			response = responseQs[device_index].get()
			attempts += 1
		
		if not response[0] == my_id and attempts >= 1000:
			RecordError("Did not get a response from device {0} for the command {1} to log {2}.".format(device_name, cmd, key))
		
		log_values.append([key, float(response[1])])
	
	db.record_logs(device_name, log_values)
		
