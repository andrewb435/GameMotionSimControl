# Copyright © 2024 Andrew Baum
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from utils.DataFrame import DataFrame
from utils.RemapValue import remapValue


class DriverSMC3:
	def __init__(self, outputScaler: DataFrame):
		self.driverMin = 0
		self.driverMax = 1023
		self.bitDepth = 10
		self.frameTime = 10  # ms
		self.axisNames = ["A", "B", "C"]

		# Data that needs to be fed from the AxisHandlers
		self.outputScaler = outputScaler

		# Axis mix enablers
		# TODO: This needs to be loaded from somewhere
		self.axisMixEnable = DataFrame()
		self.axisMixEnable.pitch = True
		self.axisMixEnable.roll = True
		self.axisMixEnable.yaw = False
		self.axisMixEnable.surge = True
		self.axisMixEnable.sway = True
		self.axisMixEnable.heave = True

	def getOutputCommand(self, commandFrames: [float], axisCount: int):
		denormalizedCommandFrame: [float] = [0.0] * axisCount
		for i in range(axisCount):
			denormalizedCommandFrame[i] = remapValue(commandFrames[i], -1.0, 1.0, self.driverMin, self.driverMax)
			denormalizedCommandFrame[i] = self.clampValue(denormalizedCommandFrame[i])
		commandString = self.formatSums(denormalizedCommandFrame, axisCount)
		return commandString

	def formatSums(self, commandFrames: [float], axisCount: [int]):
		"""
		SMC3 output format is 5 byte commands, starting and ending with []
		[ (axis ident) (upper 8 bits of position) (lower 2 bits of position) ]
			[A19]
			axisident: A
			MSB of position: 0000 0001
			LSB of position: 1111 1111
			Actual commanded position: 511
		:param commandFrames: Unified float values for the axis pose
		:param axisCount: Number axes to process
		"""
		out: chr = []
		if axisCount >= 1:
			byte_msb, byte_lsb = int(commandFrames[0]).to_bytes(2)
			out.append(ord("["))
			out.append(ord("A"))
			out.append(byte_msb)
			out.append(byte_lsb)
			out.append(ord("]"))
		if axisCount >= 2:
			byte_msb, byte_lsb = int(commandFrames[1]).to_bytes(2)
			out.append(ord("["))
			out.append(ord("B"))
			out.append(byte_msb)
			out.append(byte_lsb)
			out.append(ord("]"))
		if axisCount >= 3:
			byte_msb, byte_lsb = int(commandFrames[2]).to_bytes(2)
			out.append(ord("["))
			out.append(ord("C"))
			out.append(byte_msb)
			out.append(byte_lsb)
			out.append(ord("]"))
		command = bytearray(out)
		return command

	def clampValue(self, value):
		out = value
		if value > self.driverMax:
			out = self.driverMax
		if value < self.driverMin:
			out = self.driverMin
		return out
