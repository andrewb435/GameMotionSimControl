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
		self.poseRaw: DataFrame = DataFrame()
		self.loopDelta: float = 0
		self.isIdle: bool = True
		self.timeToIdle: float = 2.0	# Time to move from game position to idle position
		self.timeIdlePosition: float = 0
		self.poseIdleTarget: DataFrame = DataFrame()
		self.poseIdleStart: DataFrame = DataFrame()
		self.poseIdleCurrent: DataFrame = DataFrame()
		self.poseNormalized: DataFrame = DataFrame()
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
			self.poseRaw = self.gamePlugin.getDataFrame(self.loopDelta)
		if self.telemetryDebug:
			self.reporter.printTelemetryReport()
		self.convertRadiansToDegrees()
		# Clamp to gamePlugin minmax
		poseClamped = self.clampScales(self.poseRaw)
		# Normalize the outputs against the game minmax values
		self.poseNormalized = self.normalizeScales(poseClamped)
		if self.gamePlugin.getRxStatus():
			self.poseIdleStart = self.poseNormalized
			if self.isIdle:
				self.isIdle = False
				self.timeIdlePosition = 0
		else:
			self.decayToIdlePose()
		if self.axisOutputDebug:
			self.reporter.printAxisOutputReport(self.poseNormalized)

	def convertRadiansToDegrees(self):
		self.poseRaw.pitch = self.poseRaw.pitch * (180 / math.pi)
		self.poseRaw.roll = self.poseRaw.roll * (180 / math.pi)
		self.poseRaw.yaw = self.poseRaw.yaw * (180 / math.pi)

	def clampScales(self, pose_in: DataFrame) -> DataFrame:
		out = DataFrame()
		out.pitch = self.clampValue(pose_in.pitch, self.gameMinimums.pitch, self.gameMaximums.pitch)
		out.roll = self.clampValue(pose_in.roll, self.gameMinimums.roll, self.gameMaximums.roll)
		out.yaw = self.clampValue(pose_in.yaw, self.gameMinimums.yaw, self.gameMaximums.yaw)
		out.surge = self.clampValue(pose_in.surge, self.gameMinimums.surge, self.gameMaximums.surge)
		out.sway = self.clampValue(pose_in.sway, self.gameMinimums.sway, self.gameMaximums.sway)
		out.heave = self.clampValue(pose_in.heave, self.gameMinimums.heave, self.gameMaximums.heave)
		return out

	def normalizeScales(self, pose_in: DataFrame) -> DataFrame:
		out = DataFrame()
		out.pitch = remapValue(pose_in.pitch, self.gameMinimums.pitch, self.gameMaximums.pitch, -1.0, 1.0)
		out.roll = remapValue(pose_in.roll, self.gameMinimums.roll, self.gameMaximums.roll, -1.0, 1.0)
		out.yaw = remapValue(pose_in.yaw, self.gameMinimums.yaw, self.gameMaximums.yaw, -1.0, 1.0)
		out.surge = remapValue(pose_in.surge, self.gameMinimums.surge, self.gameMaximums.surge, -1.0, 1.0)
		out.sway = remapValue(pose_in.sway, self.gameMinimums.sway, self.gameMaximums.sway, -1.0, 1.0)
		out.heave = remapValue(pose_in.heave, self.gameMinimums.heave, self.gameMaximums.heave, -1.0, 1.0)
		return out

	def clampValue(self, value, minimum, maximum) -> float:
		out = value
		if out > maximum:
			out = maximum
		if out < minimum:
			out = minimum
		return out

	def getDataFrame(self):
		return self.poseNormalized

	def decayToIdlePose(self):
		if self.isIdle is False:
			self.isIdle = True
		self.timeIdlePosition += self.loopDelta
		if self.timeIdlePosition >= self.timeToIdle:
			self.timeIdlePosition = self.timeToIdle
		idleRatio = self.timeIdlePosition / self.timeToIdle
		out = DataFrame()
		out.pitch = self.poseIdleStart.pitch + (self.poseIdleTarget.pitch - self.poseIdleStart.pitch) * idleRatio
		out.roll = self.poseIdleStart.roll + (self.poseIdleTarget.roll - self.poseIdleStart.roll) * idleRatio
		out.yaw = self.poseIdleStart.yaw + (self.poseIdleTarget.yaw - self.poseIdleStart.yaw) * idleRatio
		out.surge = self.poseIdleStart.surge + (self.poseIdleTarget.surge - self.poseIdleStart.surge) * idleRatio
		out.sway = self.poseIdleStart.sway + (self.poseIdleTarget.sway - self.poseIdleStart.sway) * idleRatio
		out.heave = self.poseIdleStart.heave + (self.poseIdleTarget.heave - self.poseIdleStart.heave) * idleRatio
		self.poseNormalized = out

	def configureIdlePose(self):
		# TODO: This needs to be set or read from config
		self.poseIdleTarget.pitch = 0.0
		self.poseIdleTarget.yaw = 0.0
		self.poseIdleTarget.roll = 0.0
		self.poseIdleTarget.surge = 0.0
		self.poseIdleTarget.sway = 0.0
		self.poseIdleTarget.heave = 0.0

	def gameSearch(self):
		self.gamePlugin.checkForGame()

	def gameMinimumsLoad(self):
		self.gameMinimums = self.gamePlugin.gameMinimums

	def gameMaximumsLoad(self):
		self.gameMaximums = self.gamePlugin.gameMaximums
