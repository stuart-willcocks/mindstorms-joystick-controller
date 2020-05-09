import socket
import keyboard
import time
import RPi.GPIO as gpio
import atexit
from threading import Thread

def start_tcp_server():
	global s
	global client_socket
	
	try:
		print("closing client_socket")
		client_socket.close()
	except:
		print("client_socket.close() failed")
		
	try:
		print("closing s")
		s.close()
	except:
		print("s.close() failed")
		
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(('0.0.0.0', 50001))
	s.listen(5)
	print("listening...")
	
		
def tick():

	global client_socket
	global s
	global connected
	
	while True:
		
		if (connected):
			print("connected is True")
			gpio.output(LED_CONNECTED, gpio.HIGH)
		else:
			print("connected is False")
			gpio.output(LED_CONNECTED, gpio.LOW)
		time.sleep(0.1)


def exit_handler():
	
	global s
	global client_socket
	
	gpio.output(LED_CONNECTED, gpio.LOW)
	
	try:
		print("closing client_socket")
		client_socket.close()
	except:
		print("client_socket.close() failed")
		
	try:
		print("closing s")
		s.close()
	except:
		print("s.close() failed")
	print("application closing")


SWITCH_FWD = 16
SWITCH_REV = 22
SWITCH_LEFT = 18
SWITCH_RIGHT = 24
LED_CONNECTED = 8
BUFFER_SIZE = 20
HEARTBEAT_RESET = 5

gpio.setmode(gpio.BOARD)
gpio.setup(SWITCH_FWD, gpio.IN)
gpio.setup(SWITCH_REV, gpio.IN)
gpio.setup(SWITCH_LEFT, gpio.IN)
gpio.setup(SWITCH_RIGHT, gpio.IN)
gpio.setup(LED_CONNECTED, gpio.OUT)

s = None
client_socket = None
address = None
tcp_timeout = 5
left_last_value = 0
right_last_value = 0
fwd_last_value = 0
rev_last_value = 0
connected = False

# regsiter exit handler
atexit.register(exit_handler)

# set up server socket
start_tcp_server()

# start timer thread
t1 = Thread(target=tick)
t1.daemon = True
t1.start()

# start receive thread
#t2 = Thread(target=receive_loop)
#t2.daemon = True
#t2.start()

while True:
	
	connected = False
	client_socket, address = s.accept()
	connected = True
	print(f"{address} connected...")
	heartbeat_timer = HEARTBEAT_RESET
	
	while True:
	
		heartbeat_timer = heartbeat_timer - 1
		#print(f"heartbeat {heartbeat_timer}")
		
		if (heartbeat_timer <= 0):
			#print("heartbeat")
			try:
				client_socket.send(bytes(":TICK", "utf-8"))
			except:
				print("could not send heartbeat")
				connected = False
				client_socket.close()
				break
				
			finally:
				heartbeat_timer = HEARTBEAT_RESET

		left_current_value = gpio.input(SWITCH_LEFT)
		right_current_value = gpio.input(SWITCH_RIGHT)
		fwd_current_value = gpio.input(SWITCH_FWD)
		rev_current_value = gpio.input(SWITCH_REV)
	
			
		if (left_last_value != left_current_value):
			
			left_last_value = left_current_value
			if left_current_value == 1:
				client_socket.send(bytes(":LEFT", "utf-8"))
				print("left")
			else:
				client_socket.send(bytes(":STOP", "utf-8"))
				print("stop")
		
		if (right_last_value != right_current_value):		
			
			right_last_value = right_current_value
			if right_current_value == 1:
				client_socket.send(bytes(":RIGHT", "utf-8"))
				print("right")
			else:
				client_socket.send(bytes(":STOP", "utf-8"))
				print("stop")
		
		if (fwd_last_value != fwd_current_value):
				
			fwd_last_value = fwd_current_value
			if fwd_current_value == 1:
				client_socket.send(bytes(":FWD", "utf-8"))
				print("fwd")
			else:
				client_socket.send(bytes(":STOP", "utf-8"))
				print("stop")
		
		if (rev_last_value != rev_current_value):
					
			rev_last_value = rev_current_value
			if rev_current_value == 1:
				client_socket.send(bytes(":REV", "utf-8"))
				print("rev")
			else:
				client_socket.send(bytes(":STOP", "utf-8"))
				print("stop")
				
		time.sleep(0.1)

			
	
