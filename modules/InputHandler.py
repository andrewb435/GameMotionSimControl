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
		self.telemetryDebug = False
		self.gamePlugin = GamePlugin()
		self.inputPose = DataFrame()
		self.outputPose = DataFrame()
		self.ticker = DeltaTimer()
		self.reporter = Reporter(self.gamePlugin)

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
		self.gamePlugin.update()
		self.inputPose = self.gamePlugin.getDataFrame(self.ticker.getDelta())
		if self.telemetryDebug:
			self.reporter.printReport()
		self.convertRadiansToDegrees()
		# Clamp to gamePlugin minmax
		self.clampScales()
		# Normalize the outputs against the game minmax values
		self.normalizeScales()

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

	def gameSearch(self):
		self.gamePlugin.checkForGame()

	def gameMinimumsLoad(self):
		self.gameMinimums = self.gamePlugin.gameMinimums

	def gameMaximumsLoad(self):
		self.gameMaximums = self.gamePlugin.gameMaximums
