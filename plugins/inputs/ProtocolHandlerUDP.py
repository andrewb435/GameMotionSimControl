# Copyright © 2024 Andrew Baum
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import socket
import time


class ProtocolHandlerUDP:
	def __init__(self, timeout: float):
		self.timeout = timeout
		self.socket = None
		self.ip = None
		self.port = None
		self.lastPacket = 0.0
		self.data = None

	def openUDP(self, game_ip, game_port):
		# self.socket = networking.open_port(game_ip, game_port)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.settimeout(1.0/60.0)
		try:
			self.socket.bind((game_ip, game_port))
		except Exception as err:
			print('err' + str(err))

	def closeUDP(self):
		self.socket.close()

	def getFrame(self):
		if self.socket is None:
			return None
		if self.socket.recv is not None:
			try:
				self.data, addr = self.socket.recvfrom(1024)  # 1024 byte buffer
				self.lastPacket = time.time()
			except TimeoutError as _:
				if (time.time() - self.lastPacket >= self.timeout) and (self.data is not None):
					print(str(self.timeout) + ' seconds since last packet, clearing data buffer and marking inactive')
					self.data = None
				else:
					pass
		return self.data
