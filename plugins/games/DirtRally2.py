# Copyright © 2024 Andrew Baum
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
	totalTime = 0
	lapTime = 1
	lapDistance = 2
	totalDistance = 3
	positionX = 4
	positionY = 5
	positionZ = 6
	speed = 7
	velocityX = 8
	velocityY = 9
	velocityZ = 10
	rollX = 11
	rollY = 12
	rollZ = 13
	pitchX = 14
	pitchY = 15
	pitchZ = 16
	suspensionPositionBL = 17
	suspensionPositionBR = 18
	suspensionPositionFL = 19
	suspensionPositionFR = 20
	suspensionVelocityBL = 21
	suspensionVelocityBR = 22
	suspensionVelocityFL = 23
	suspensionVelocityFR = 24
	wheelSpeedBL = 25
	wheelSpeedBR = 26
	wheelSpeedFL = 27
	wheelSpeedFR = 28
	positionThrottle = 29
	positionSteering = 30
	positionBrake = 31
	positionClutch = 32
	gearCurrent = 33
	gforceLateral = 34
	gForceLongitudinal = 35
	currentLap = 36
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
	brakeTempBL = 51
	brakeTempBR = 52
	brakeTempFL = 53
	brakeTempFR = 54
	unused18 = 55
	unused19 = 56
	unused20 = 57
	unused21 = 58
	completeLaps = 59
	totalLaps = 60
	lengthOfTrack = 61
	lastLapTime = 62
	maxRPM = 63  # Max RPM / 10
	idleRPM = 64  # Idle RPM / 10
	gearMax = 65


class DataPacketUnpacked:
	totalTime: float = 0.0
	lapTime: float = 0.0
	lapDistance: float = 0.0
	totalDistance: float = 0.0
	positionX: float = 0.0
	positionY: float = 0.0
	positionZ: float = 0.0
	speed: float = 0.0
	velocityX: float = 0.0
	velocityY: float = 0.0
	velocityZ: float = 0.0
	rollX: float = 0.0
	rollY: float = 0.0
	rollZ: float = 0.0
	pitchX: float = 0.0
	pitchY: float = 0.0
	pitchZ: float = 0.0
	suspensionPositionBL: float = 0.0
	suspensionPositionBR: float = 0.0
	suspensionPositionFL: float = 0.0
	suspensionPositionFR: float = 0.0
	suspensionVelocityBL: float = 0.0
	suspensionVelocityBR: float = 0.0
	suspensionVelocityFL: float = 0.0
	suspensionVelocityFR: float = 0.0
	wheelSpeedBL: float = 0.0
	wheelSpeedBR: float = 0.0
	wheelSpeedFL: float = 0.0
	wheelSpeedFR: float = 0.0
	positionThrottle: float = 0.0
	positionSteering: float = 0.0
	positionBrake: float = 0.0
	positionClutch: float = 0.0
	gearCurrent: float = 0.0
	gforceLateral: float = 0.0
	gForceLongitudinal: float = 0.0
	currentLap: float = 0.0
	engineRPM: float = 0.0
	brakeTempBL: float = 0.0
	brakeTempBR: float = 0.0
	brakeTempFL: float = 0.0
	brakeTempFR: float = 0.0
	totalLaps: float = 0.0
	lengthOfTrack: float = 0.0
	engineMaxRPM: float = 0.0
	gearMax: float = 0.0


class GamePlugin:
	def __init__(self):
		# State information
		self.timeout = 1.0	# Time in seconds since last packet before game plugin goes inactive
		self.statusRunning = False
		self.statusRxData = False
		self.datagram = None
		self.data = DataPacketUnpacked()
		self.socket = ProtocolHandlerUDP(self.timeout)

		# Derived information - Internal
		self.VectorX = 0
		self.VectorY = 0
		self.VectorZ = 0
		self.lastHeaveSpeed = 0
		self.heaveSpeed = 0
		self.heaveAccel = 0

		# Configured information
		self.gameMinimums = self.loadGameMinimums()
		self.gameMaximums = self.loadGameMaximums()

	def setupSocket(self):
		self.socket.openUDP("127.0.0.1", 20777)

	def getRunningStatus(self):
		return self.statusRunning

	def getRxStatus(self):
		return self.statusRxData

	def update(self):
		self.datagram = self.socket.getFrame()
		if self.datagram is not None:
			self.statusRxData = True
			self.parseDatagram()
		else:
			self.statusRxData = False

	def getDataFrame(self, frameDelta) -> DataFrame:
		dataFrame = DataFrame()
		if self.datagram is not None:
			# Calculate pitch/yaw/roll angles in radians
			dataFrame.pitch = math.atan2(self.VectorY, self.data.pitchY) + (math.pi / 2)  # Rotate pitchY by 90 deg
			dataFrame.roll = math.asin(self.data.rollY)
			dataFrame.yaw = math.atan2(self.data.rollX, self.data.rollZ)

			# Pull sway and surge direct from telemetry
			dataFrame.surge = self.data.gForceLongitudinal
			dataFrame.sway = self.data.gforceLateral

			# calculate heave
			self.heaveSpeed = (self.VectorX * self.data.velocityX) + \
								(self.VectorY * self.data.velocityY) + \
								(self.VectorZ * self.data.velocityZ)
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

	def parseDatagram(self):
		self.datagram = struct.unpack(str(numDataFieldsInPacket) + 'f',
									self.datagram[
									0:numDataFieldsInPacket * byteOffset
									])

		# Motion values
		self.data.positionX = self.datagram[DataPacketStructure.positionX.value]
		self.data.positionY = self.datagram[DataPacketStructure.positionY.value]
		self.data.positionZ = self.datagram[DataPacketStructure.positionZ.value]
		self.data.velocityX = self.datagram[DataPacketStructure.velocityX.value]
		self.data.velocityY = self.datagram[DataPacketStructure.velocityY.value]
		self.data.velocityZ = self.datagram[DataPacketStructure.velocityZ.value]
		self.data.rollX = self.datagram[DataPacketStructure.rollX.value]
		self.data.rollY = self.datagram[DataPacketStructure.rollY.value]
		self.data.rollZ = self.datagram[DataPacketStructure.rollZ.value]
		self.data.pitchX = self.datagram[DataPacketStructure.pitchX.value]
		self.data.pitchY = self.datagram[DataPacketStructure.pitchY.value]
		self.data.pitchZ = self.datagram[DataPacketStructure.pitchZ.value]
		self.data.gforceLateral = self.datagram[DataPacketStructure.gforceLateral.value]
		self.data.gForceLongitudinal = self.datagram[DataPacketStructure.gForceLongitudinal.value]

		# Telemetry Values
		self.data.totalTime = self.datagram[DataPacketStructure.totalTime.value]
		self.data.lapTime = self.datagram[DataPacketStructure.lapTime.value]
		self.data.lapDistance = self.datagram[DataPacketStructure.lapDistance.value]
		self.data.totalDistance = self.datagram[DataPacketStructure.totalDistance.value]
		self.data.speed = self.datagram[DataPacketStructure.speed.value]
		self.data.suspensionPositionBL = self.datagram[DataPacketStructure.suspensionPositionBL.value]
		self.data.suspensionPositionBR = self.datagram[DataPacketStructure.suspensionPositionBR.value]
		self.data.suspensionPositionFL = self.datagram[DataPacketStructure.suspensionPositionFL.value]
		self.data.suspensionPositionFR = self.datagram[DataPacketStructure.suspensionPositionFR.value]
		self.data.suspensionVelocityBL = self.datagram[DataPacketStructure.suspensionVelocityBL.value]
		self.data.suspensionVelocityBR = self.datagram[DataPacketStructure.suspensionVelocityBR.value]
		self.data.suspensionVelocityFL = self.datagram[DataPacketStructure.suspensionVelocityFL.value]
		self.data.suspensionVelocityFR = self.datagram[DataPacketStructure.suspensionVelocityFR.value]
		self.data.wheelSpeedBL = self.datagram[DataPacketStructure.wheelSpeedBL.value]
		self.data.wheelSpeedBR = self.datagram[DataPacketStructure.wheelSpeedBR.value]
		self.data.wheelSpeedFL = self.datagram[DataPacketStructure.wheelSpeedFL.value]
		self.data.wheelSpeedFR = self.datagram[DataPacketStructure.wheelSpeedFR.value]
		self.data.positionThrottle = self.datagram[DataPacketStructure.positionThrottle.value]
		self.data.positionSteering = self.datagram[DataPacketStructure.positionSteering.value]
		self.data.positionBrake = self.datagram[DataPacketStructure.positionBrake.value]
		self.data.positionClutch = self.datagram[DataPacketStructure.positionClutch.value]
		self.data.gearCurrent = self.datagram[DataPacketStructure.gearCurrent.value]
		self.data.currentLap = self.datagram[DataPacketStructure.currentLap.value]
		self.data.engineRPM = self.datagram[DataPacketStructure.engineRPM.value]
		self.data.brakeTempBL = self.datagram[DataPacketStructure.brakeTempBL.value]
		self.data.brakeTempBR = self.datagram[DataPacketStructure.brakeTempBR.value]
		self.data.brakeTempFL = self.datagram[DataPacketStructure.brakeTempFL.value]
		self.data.brakeTempFR = self.datagram[DataPacketStructure.brakeTempFR.value]
		self.data.totalLaps = self.datagram[DataPacketStructure.totalLaps.value]
		self.data.lengthOfTrack = self.datagram[DataPacketStructure.lengthOfTrack.value]
		self.data.engineMaxRPM = self.datagram[DataPacketStructure.maxRPM.value]
		self.data.gearMax = self.datagram[DataPacketStructure.gearMax.value]

		# Unify roll and pitch vectors
		self.VectorX = self.data.pitchY * self.data.rollZ - self.data.pitchZ * self.data.rollY
		self.VectorY = self.data.pitchZ * self.data.rollX - self.data.pitchX * self.data.rollZ
		self.VectorZ = self.data.pitchX * self.data.rollY - self.data.pitchY * self.data.rollX

	def checkForGame(self) -> bool:
		processName = 'dirtrally2.exe'
		for proc in psutil.process_iter():
			try:
				if processName.lower() in proc.name().lower():
					self.statusRunning = True
			except Exception as err:
				self.statusRunning = False
				print('Other err:' + str(err))
		return self.statusRunning

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
