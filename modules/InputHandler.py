# Copyright © 2024 Andrew Baum
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import time
import math
from plugins.games.DirtRally2 import GamePlugin
from utils.CLIReporter import Reporter
from utils.TickTimer import DeltaTimer
from utils.RemapValue import remapValue
from utils.DataFrame import DataFrame


"""
InputHandler takes the output from the Game Plugin in unitless translations and radian rotations and converts it to
a normalized, unified DataFrame containing a final frame pose, with all axes ranging from -1.0 to 1.0
"""
class InputHandler:
	def __init__(self):
		self.telemetryDebug: bool = False
		self.axisOutputDebug: bool = False
		self.gamePlugin: GamePlugin = GamePlugin()
		self.inputPose: DataFrame = DataFrame()
		self.timeToIdle: float = 4.0	# Time to move from game position to idle position
		self.loopDelta: float = 0
		self.isIdle: bool = True
		self.idleTimePosition: float = 0
		self.idlePose: DataFrame = DataFrame()
		self.idleStartPose: DataFrame = DataFrame()
		self.idleCurrentPose: DataFrame = DataFrame()
		self.outputPose: DataFrame = DataFrame()
		self.ticker: DeltaTimer = DeltaTimer()
		self.reporter: Reporter = Reporter(self.gamePlugin)
		self.configureIdlePose()

		# Minimums for given game
		self.gameMinimums = None
		self.gameMinimumsLoad()

		# Maximums for given game
		self.gameMaximums = None
		self.gameMaximumsLoad()

	def setupPlugin(self):
		self.gamePlugin.setupSocket()

	def gameStatus(self):
		return self.gamePlugin.getRunningStatus()

	def gameRx(self):
		return self.gamePlugin.getRxStatus()

	def update(self):
		self.loopDelta = self.ticker.getDelta()
		self.gamePlugin.update()
		if self.gamePlugin.getRxStatus():
			self.inputPose = self.gamePlugin.getDataFrame(self.loopDelta)
		if self.telemetryDebug:
			self.reporter.printTelemetryReport()
		self.convertRadiansToDegrees()
		# Clamp to gamePlugin minmax
		self.clampScales()
		# Normalize the outputs against the game minmax values
		self.normalizeScales()
		if self.gamePlugin.getRxStatus():
			self.idleStartPose = self.outputPose
			self.isIdle = False
		else:
			self.decayToIdlePose()
		if self.axisOutputDebug:
			self.reporter.printAxisOutputReport(self.outputPose)

	def convertRadiansToDegrees(self):
		self.inputPose.pitch = self.inputPose.pitch * (180 / math.pi)
		self.inputPose.roll = self.inputPose.roll * (180 / math.pi)
		self.inputPose.yaw = self.inputPose.yaw * (180 / math.pi)

	def clampScales(self):
		out = DataFrame()
		out.pitch = self.clampValue(self.inputPose.pitch, self.gameMinimums.pitch, self.gameMaximums.pitch)
		out.roll = self.clampValue(self.inputPose.roll, self.gameMinimums.roll, self.gameMaximums.roll)
		out.yaw = self.clampValue(self.inputPose.yaw, self.gameMinimums.yaw, self.gameMaximums.yaw)
		out.surge = self.clampValue(self.inputPose.surge, self.gameMinimums.surge, self.gameMaximums.surge)
		out.sway = self.clampValue(self.inputPose.sway, self.gameMinimums.sway, self.gameMaximums.sway)
		out.heave = self.clampValue(self.inputPose.heave, self.gameMinimums.heave, self.gameMaximums.heave)
		self.outputPose = out

	def normalizeScales(self):
		out = DataFrame()
		out.pitch = remapValue(self.outputPose.pitch, self.gameMinimums.pitch, self.gameMaximums.pitch, -1.0, 1.0)
		out.roll = remapValue(self.outputPose.roll, self.gameMinimums.roll, self.gameMaximums.roll, -1.0, 1.0)
		out.yaw = remapValue(self.outputPose.yaw, self.gameMinimums.yaw, self.gameMaximums.yaw, -1.0, 1.0)
		out.surge = remapValue(self.outputPose.surge, self.gameMinimums.surge, self.gameMaximums.surge, -1.0, 1.0)
		out.sway = remapValue(self.outputPose.sway, self.gameMinimums.sway, self.gameMaximums.sway, -1.0, 1.0)
		out.heave = remapValue(self.outputPose.heave, self.gameMinimums.heave, self.gameMaximums.heave, -1.0, 1.0)
		self.outputPose = out

	def clampValue(self, value, minimum, maximum) -> float:
		out = value
		if out > maximum:
			out = maximum
		if out < minimum:
			out = minimum
		return out

	def getDataFrame(self):
		return self.outputPose

	def decayToIdlePose(self):
		if self.isIdle is False:
			self.idleTimePosition = 0
			self.isIdle = True
		self.idleTimePosition += self.loopDelta
		if self.idleTimePosition >= self.timeToIdle:
			self.idleTimePosition = self.timeToIdle
		idleRatio = self.idleTimePosition / self.timeToIdle
		out = DataFrame()
		out.roll = self.idleStartPose.roll + (self.idlePose.roll - self.idleStartPose.roll) * idleRatio
		out.pitch = self.idleStartPose.pitch + (self.idlePose.pitch - self.idleStartPose.pitch) * idleRatio
		out.yaw = self.idleStartPose.yaw + (self.idlePose.yaw - self.idleStartPose.yaw) * idleRatio
		out.surge = self.idleStartPose.surge + (self.idlePose.surge - self.idleStartPose.surge) * idleRatio
		out.sway = self.idleStartPose.sway + (self.idlePose.sway - self.idleStartPose.sway) * idleRatio
		out.heave = self.idleStartPose.heave + (self.idlePose.heave - self.idleStartPose.heave) * idleRatio
		self.outputPose = out

	def configureIdlePose(self):
		# TODO: This needs to be set or read from config
		self.idlePose.pitch = 0.5
		self.idlePose.yaw = 0.5
		self.idlePose.roll = 0.5
		self.idlePose.surge = 0.5
		self.idlePose.sway = 0.5
		self.idlePose.heave = 0.5

	def gameSearch(self):
		self.gamePlugin.checkForGame()

	def gameMinimumsLoad(self):
		self.gameMinimums = self.gamePlugin.gameMinimums

	def gameMaximumsLoad(self):
		self.gameMaximums = self.gamePlugin.gameMaximums
