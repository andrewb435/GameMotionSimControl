import serial
import serial.tools.list_ports

arduinoVID = [0x2341, 0x2A03]
arduinoUnoPID = [0x0001, 0x0043, 0x0243]

class Style:
	PURPLE = '\033[95m'
	CYAN = '\033[96m'
	DARKCYAN = '\033[36m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	END = '\033[0m'

class SerialFinder:
	def __init__(self):
		self.portList = None
		self.portSelected = None

	def listPorts(self):
		self.portList = []
		ports = serial.tools.list_ports.comports()
		for port in sorted(ports):
			if port.description != 'n/a':
				self.portList.append(port)
		return self.selectPorts()

	def selectPorts(self):
		choice = ''
		input_message = "Choose motion controller port:\n"
		for index, port in enumerate(self.portList):
			if port.vid in arduinoVID and port.pid in arduinoUnoPID:
				input_message += f'{Style.BOLD}{Style.YELLOW}{index + 1}) {"Port " + str(port.device) + ", (Arduino Uno) Desc: " + str(port.description) + ", HWID: " + str(port.hwid) + "\n"}{Style.END}'
			else:
				input_message += f'{index + 1}) {"Port " + str(port.device) + ", Desc: " + str(port.description) + ", HWID: " + str(port.hwid) + "\n"}'
		input_message += "Selection: "
		while choice not in map(str, range(1, len(self.portList) + 1)):
			choice = input(input_message)
		print("Selected: " + str(self.portList[int(choice) - 1].device))
		return self.portList[int(choice) - 1].device
