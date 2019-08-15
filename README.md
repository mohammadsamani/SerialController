# Serial Port Controller

I run this code as a systemd service on a Raspberry Pi that is attached to a Lakeshore thermometer bridge using a USB serial port. What it does is the following:

* It creates a process that sends and receives commands to one or more serial ports. It also accepts commands from other processes through a multiprocessing.Queue object. All of that is in comm.py
* It provides an http interface for external commands. Code is in HTTP_server.py. Details below.
* It can be set up to log various quantities and save them on a MySQL server.

Hopefully to use this in your environment, you would only need to change the config.py file.

## HTTP Server
The HTTP server accepts POST requests. The contents should be JSON-formatted with the following keys:
* _deviceName_ is the name of the device as specified in the config file. In the sample config file "BFLD400_Lakeshore730" would be a possible deviceName.
* _commandType_ is either R, W, or Q, for READ, WRITE, or QUERY.
* _command_ is the body of the command. Do not include the end of line characters in the command. Those are configured in the config.py for each device.

If the command returns something, the HTTP server returns a response and the body will be JSON-formatted with two keys in it.
* _response_ will include the response.
* _error_ will include any errors.