import serial
import serial.tools.list_ports


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
			input_message += f'{index + 1}) {"Port " + str(port) + ", Desc: " + str(port.description) + ", HWID: " + str(port.hwid) + "\n"}'
		input_message += "Selection: "
		while choice not in map(str, range(1, len(self.portList) + 1)):
			choice = input(input_message)
		print("Selected: " + str(self.portList[int(choice) - 1].device))
		return self.portList[int(choice) - 1].device
