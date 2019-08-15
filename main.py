#!/usr/bin/python3
from multiprocessing import Process, Queue
import time

from comm import Communicate
from HTTP_server import http_serve
from logger import log
import config

if __name__ == "__main__":
	processes = []
	commandQs = []
	responseQs = []
	device_names = []
	for device_name in config.conf['Devices']:
		device_names.append(device_name)
		commandQ = Queue()		# This is where the commands are sent
		responseQ = Queue()
		commandQs.append(commandQ)
		responseQs.append(responseQ)
		processes.append(Process(target=Communicate, args=(device_name, commandQ, responseQ, )))
	
	for p in processes:
		p.start()

	p_http = Process(target=http_serve, args=(device_names, commandQs, responseQs, ))
	p_http.start()
	
	
	log(device_names, commandQs, responseQs) # Log in the same process, because now this process has nothing to do.
