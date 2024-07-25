# Copyright © 2024 Andrew Baum
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import serial
import time
from utils.TickTimer import TickTimer
from plugins.outputs.communication.DriverSerialComfinder import SerialFinder


class DriverSerial:
	def __init__(self):
		self.updateMs: int = 10
		self.port = None
		self.baud = 500000
		self.timer = TickTimer(self.updateMs)	# 10ms = 100Hz updates
		self.connection = None
		self.ready = True
		self.finder = SerialFinder()

	def selectSerial(self):
		self.port = self.finder.listPorts()
		if self.port is not None:
			self.initSerial()

	def initSerial(self):
		try:
			self.connection = serial.Serial(self.port, self.baud, timeout=1)
		except serial.SerialException as err:
			self.connection = None
			print(err)

	def isReady(self) -> bool:
		if self.timer.check():
			self.ready = True
			return True
		else:
			return False

	def sendCommand(self, command):
		if self.ready is True:
			self.ready = False
			if self.connection:
				if self.connection.in_waiting > 0:
					serial_out = self.connection.read_until()
					print(serial_out)
			if self.connection:
				if not self.connection.is_open:
					self.initSerial()
				if self.connection.is_open:
					try:
						self.connection.write(command)
					except Exception as err:
						self.connection.close()
						self.connection = None
						print(err)
			else:
				print('Retrying port ' + str(self.port) + ' at ' + str(self.baud) + ' baud')
				time.sleep(.25)
				self.initSerial()
