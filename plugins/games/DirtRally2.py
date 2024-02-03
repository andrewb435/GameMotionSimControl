Copyright © 2024 Andrew Baum

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import struct
import math
import psutil
from enum import Enum

from utils.DataFrame import DataFrame
from plugins.inputs.ProtocolHandlerUDP import ProtocolHandlerUDP

# byte offset for each data field
# e.g. timeRun is bytes 0-3, totalling 4 bytes
byteOffset = 4

# Total number of data fields in the UDP packet definition under DataPacketStructure
numDataFieldsInPacket = 66


class DataPacketStructure(Enum):
	timeRun = 0
	timeLap = 1
	distance = 2
	progress = 3
	posX = 4
	posY = 5
	posZ = 6
	speedMPS = 7
	velX = 8
	velY = 9
	velZ = 10
	rollX = 11
	rollY = 12
	rollZ = 13
	pitchX = 14
	pitchY = 15
	pitchZ = 16
	posSuspensionRL = 17
	posSuspensionRR = 18
	posSuspensionFL = 19
	posSuspensionFR = 20
	velSuspensionRL = 21
	velSuspensionRR = 22
	velSuspensionFL = 23
	velSuspensionFR = 24
	wheelVelRL = 25
	wheelVelRR = 26
	wheelVelFL = 27
	wheelVelFR = 28
	posThrottle = 29
	posSteering = 30
	posBrake = 31
	posClutch = 32
	curGear = 33
	forceLateral = 34
	forceLongitudinal = 35
	curLap = 36
	engineRPM = 37  # RPM / 10
	unused1 = 38
	unused2 = 39
	unused3 = 40
	unused4 = 41
	unused5 = 42
	unused6 = 43
	unused7 = 44
	unused8 = 45
	unused9 = 46
	unused10 = 47
	unused11 = 48
	unused12 = 49
	unused13 = 50
	tempBrakeRL = 51
	tempBrakeRR = 52
	tempBrakeFL = 53
	tempBrakeFR = 54
	unused18 = 55
	unused19 = 56
	unused20 = 57
	unused21 = 58
	completeLaps = 59
	totalLaps = 60
	totalLenght = 61
	lastLapTime = 62
	maxRPM = 63  # Max RPM / 10
	idleRPM = 64  # Idle RPM / 10
	maxGears = 65


class GamePlugin:
	def __init__(self):
		# State information
		self.statusConnected = False
		self.data = None
		self.socket = ProtocolHandlerUDP()

		# Received information
		self.posX = 0
		self.posY = 0
		self.posZ = 0
		self.velX = 0
		self.velY = 0
		self.velZ = 0
		self.rollX = 0
		self.rollY = 0
		self.rollZ = 0
		self.pitchX = 0
		self.pitchY = 0
		self.pitchZ = 0
		self.forceLat = 0
		self.forceLong = 0

		# Derived information - Internal
		self.unifiedVectorX = 0
		self.unifiedVectorY = 0
		self.unifiedVectorZ = 0
		self.lastHeaveSpeed = 0
		self.heaveSpeed = 0
		self.heaveAccel = 0

		# Configured information
		self.gameMinimums = self.loadGameMinimums()
		self.gameMaximums = self.loadGameMaximums()

	def setupSocket(self):
		self.socket.openUDP("127.0.0.1", 20777)

	def getStatus(self):
		return self.statusConnected

	def update(self):
		self.data = self.socket.getFrame()
		if self.data is not None:
			self.statusConnected = True
			self.parseDataFrame()
		else:
			self.statusConnected = False

	def getDataFrame(self, frameDelta) -> DataFrame:
		dataFrame = DataFrame()
		if self.data is not None:
			# Calculate pitch/yaw/roll angles in radians
			dataFrame.pitch = math.atan2(self.unifiedVectorY, self.pitchY) + (math.pi / 2)  # Rotate pitchY by 90 deg
			dataFrame.roll = math.asin(self.rollY)
			dataFrame.yaw = math.atan2(self.rollX, self.rollZ)

			# Pull sway and surge direct from telemetry
			dataFrame.surge = self.forceLong
			dataFrame.sway = self.forceLat

			# calculate heave
			self.heaveSpeed = (self.unifiedVectorX * self.velX) + \
								(self.unifiedVectorY * self.velY) + \
								(self.unifiedVectorZ * self.velZ)
			self.heaveAccel = (self.heaveSpeed - self.lastHeaveSpeed) / frameDelta
			self.lastHeaveSpeed = self.heaveSpeed

			dataFrame.heave = self.heaveAccel
		else:
			dataFrame.pitch = 0
			dataFrame.roll = 0
			dataFrame.yaw = 0
			dataFrame.surge = 0
			dataFrame.sway = 0
			dataFrame.heave = 0

		return dataFrame

	def parseDataFrame(self):
		self.data = struct.unpack(str(numDataFieldsInPacket) + 'f',
									self.data[
									0:numDataFieldsInPacket * byteOffset
									])

		# parse provided values
		self.posX = self.data[DataPacketStructure.posX.value]
		self.posY = self.data[DataPacketStructure.posY.value]
		self.posZ = self.data[DataPacketStructure.posZ.value]
		self.velX = self.data[DataPacketStructure.velX.value]
		self.velY = self.data[DataPacketStructure.velY.value]
		self.velZ = self.data[DataPacketStructure.velZ.value]
		self.rollX = self.data[DataPacketStructure.rollX.value]
		self.rollY = self.data[DataPacketStructure.rollY.value]
		self.rollZ = self.data[DataPacketStructure.rollZ.value]
		self.pitchX = self.data[DataPacketStructure.pitchX.value]
		self.pitchY = self.data[DataPacketStructure.pitchY.value]
		self.pitchZ = self.data[DataPacketStructure.pitchZ.value]
		self.forceLat = self.data[DataPacketStructure.forceLateral.value]
		self.forceLong = self.data[DataPacketStructure.forceLongitudinal.value]

		# unified vectors from pitch and roll vectors
		self.unifiedVectorX = self.pitchY * self.rollZ - self.pitchZ * self.rollY
		self.unifiedVectorY = self.pitchZ * self.rollX - self.pitchX * self.rollZ
		self.unifiedVectorZ = self.pitchX * self.rollY - self.pitchY * self.rollX

		# test = self.data[DataPacketStructure.maxGears.value]
		# print(test)

	def checkForGame(self):
		processName = 'dirtrally2.exe'
		for proc in psutil.process_iter():
			try:
				if processName.lower() in proc.name().lower():
					self.statusConnected = True
			except Exception as err:
				self.statusConnected = False
				print('Other err:' + str(err))

	def loadGameMinimums(self) -> DataFrame:
		out = DataFrame()
		out.pitch = -15.0
		out.roll = -15.0
		out.yaw = -180.0
		out.surge = -2.0
		out.sway = -2.0
		out.heave = -15.0
		return out

	def loadGameMaximums(self) -> DataFrame:
		out = DataFrame()
		out.pitch = 15.0
		out.roll = 15.0
		out.yaw = 180.0
		out.surge = 2.0
		out.sway = 2.0
		out.heave = 15.0
		return out
