# Copyright © 2024 Andrew Baum
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import serial
import serial.tools.list_ports

arduinoVID = [0x2341, 0x2A03]
arduinoUnoPID = [0x0001, 0x0043, 0x0243]

class Style:
	# Font effects
	BOLD = '\033[1m'
	ITALIC = '\033[3m'
	UNDERLINE = '\033[4m'
	# Font Colors
	RED = '\033[31m'
	GREEN = '\033[32m'
	YELLOW = '\033[33m'
	BLUE = '\033[34m'
	MAGENTA = '\033[35m'
	CYAN = '\033[36m'
	# END
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
				input_message += f'{Style.BOLD}{Style.YELLOW}{index + 1}) {"Port " + str(port.device) + " (Arduino Uno),Desc: " + str(port.description) + ", HWID: " + str(port.hwid) + "\n"}{Style.END}'
			else:
				input_message += f'{index + 1}) {"Port " + str(port.device) + ", Desc: " + str(port.description) + ", HWID: " + str(port.hwid) + "\n"}'
		input_message += "Selection: "
		while choice not in map(str, range(1, len(self.portList) + 1)):
			choice = input(input_message)
		print("Selected: " + str(self.portList[int(choice) - 1].device))
		return self.portList[int(choice) - 1].device
