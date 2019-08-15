from multiprocessing import Queue
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
import ssl
from io import BytesIO
import json, time, random

class RaspberryPiHTTPServer(ThreadingMixIn, HTTPServer):
	def SetQueues(self, device_names, commandQs, responseQs):
		self.device_names = device_names
		self.commandQs = commandQs
		self.responseQs = responseQs
	

class RaspberryPiHTTPRequestHandler(BaseHTTPRequestHandler):
	def _send_header(self):
		self.send_response(200)
		self.send_header('Content-type','application/json')
		self.send_header('Encoding','utf-8')
		self.send_header('Access-Control-Allow-Origin','*')
		self.end_headers()
	
	def _authenticate(self, password):
		return True #TODO

	def do_GET(self):
		self._send_header()
		self.wfile.write(b'Use POST to send commands.')

	def do_POST(self):		
		content_length = int(self.headers['Content-Length'])
		body = self.rfile.read(content_length).decode('utf-8')
		jsonbody = json.loads(body)
		
		self._send_header()
		
		# Authenticate
		authenticated = False
		if 'password' in jsonbody:
			authenticated = self._authenticate(jsonbody['password'])
		if not authenticated:
			self.wfile.write(bytearray("{\"response\": \"\", \"error\": \"Authentication failure.\"}", 'utf-8'))
			return
		
		# Make sure all the components of the command are present
		if not ('deviceName' in jsonbody and 'command' in jsonbody and 'commandType' in jsonbody):
			self.wfile.write(bytearray("{\"response\": \"\", \"error\": \"You need to provide a deviceName, a command type, and a command.\"}", 'utf-8'))
			return
		
		device_name = jsonbody['deviceName']
		command_type = jsonbody['commandType']
		command = jsonbody['command']
		
		# Make sure the command type is valid
		if not command_type in ['R', 'W', 'Q']:
			self.wfile.write(bytearray("{\"response\": \"\", \"error\": \"Invalid command type.\"}", 'utf-8'))
			return
		
		#Make sure the device name is valid.
		if not device_name in self.server.device_names:
			self.wfile.write(bytearray("{\"response\": \"\", \"error\": \"Invalid device name.\"}", 'utf-8'))
			return
		
		device_index = self.server.device_names.index(device_name)

		# Send the command to the device
		my_id = str(threading.currentThread().ident)
		msg = [my_id, command_type, command]
		self.server.commandQs[device_index].put(msg)

		# Now find the response in the queue of all responses
		response = self.server.responseQs[device_index].get()
		attempts = 0
		while not response[0] == my_id and attempts < 1000:
			# Not a response to my query. Put it back in the queue.
			self.server.responseQs[device_index].put(response)
			# Hope the intended recipient will pick it up quickly
			time.sleep(random.randint(0,100)/1000)
			response = self.server.responseQs[device_index].get()
			attempts += 1
		
		if not response[0] == my_id and attempts >= 1000:
			self.wfile.write(bytearray("{\"response\": \"\", \"error\": \"Some how the query got lost. Blame Mohammad.\"}", 'utf-8'))
			return		
		
		# Everything has worked out at this point, and we're just sending a response back to the web-client.
		#print("Everything is fine ID={0} MSG={1}".format(response[0], response[1]))
		msg = "{\"response\": \"" + response[1] + "\", \"error\": \"\"}"
		print("MSGGGG", msg)
		self.wfile.write(bytearray(msg, 'utf-8'))
		
def http_serve(device_names, commandQs, responseQs):
	httpd = RaspberryPiHTTPServer(('localhost', 8085), RaspberryPiHTTPRequestHandler)
	httpd.SetQueues(device_names, commandQs, responseQs)
	#httpd.socket = ssl.wrap_socket (httpd.socket, 
	#	keyfile="./key.pem",
	#	certfile="./cert.pem",
	#	server_side=True)
	httpd.serve_forever()
