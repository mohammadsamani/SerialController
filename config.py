import serial
conf = {
	"ReloadPeriod":			60,
	"Devices": {
		"BFLD400_Lakeshore730": {
			# Lakeshore communication settings
			"Terminator":	"\r\n",
			"SerialPort":	"/dev/ttyUSB0",
			"Baudrate":		9600,
			"Parity":		serial.PARITY_ODD,
			"Stopbits":		serial.STOPBITS_TWO,
			"Bytesize":		serial.SEVENBITS,
			"MinDelay":		0.5,				# Lakeshore requires that 50ms is minimum time between consecutive data transfers.
			"LogPeriod":	30.0,				# seconds, negative number means never.
			"LogItems":	{
				"50k_plate_tmp":		"RDGK? 1",
				"4k_plate_tmp":			"RDGK? 2",
				"magnet_main_tmp":		"RDGK? 3",
				"magnet_persist_tmp":	"RDGK? 4",
				"still_tmp":			"RDGK? 5",
				"mixch_tmp":			"RDGK? 6"
			}
		}
	},
	"PasswordHash":		"CryoH4ll",
	"Logging": {
		"SleepInLoop":		1,
		"mysql": {
			"host":			"phys-dots-15.physik.unibas.ch",
			"user":			"logger",
			"password":		"$$$$$$",
			"database":		"logs"
		}
	}
}
