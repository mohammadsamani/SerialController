import mysql.connector
import importlib

import config
from error import RecordError

def connect():
	importlib.reload(config)
	return mysql.connector.connect( **config.conf['Logging']['mysql'] )

def record_logs(device_name, log_values):
	try:
		con = connect()
		cursor = con.cursor()
		sql = "INSERT INTO `records`(`sensor_id`, `time`, `value`) VALUES "
		
		for row in log_values:
			sql += "((SELECT `sensor_id` FROM `sensors` WHERE `sensor_name`='{0:s}' AND machine_id=(SELECT machine_id FROM machines WHERE machine_name='{1:s}')),NOW(),{2:f}),".format(row[0], device_name, row[1])
		
		cursor.execute(sql[:-1])
		con.commit()
		cursor.close()
		con.close()
		
	except Exception as x:
		RecordError("Error recording logs into the database. device_name={0} log_values={1} Exception={2}".format(device_name, log_values, x))

if __name__ == "__main__":

	con = mysql.connector.connect( **config.conf['Logging']['mysql'] )
	
	print(con.get_ssl_cipher())