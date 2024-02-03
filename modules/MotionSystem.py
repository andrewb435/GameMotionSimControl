Copyright © 2024 Andrew Baum

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from modules.AxisHandler import AxisHandler
from modules.PoseHandler import PoseHandler
from utils.DataFrame import DataFrame
from plugins.outputs.controller.DriverSMC3 import DriverSMC3


class MotionSystem:
	"""
	Initialize a MotionSystem containing AxisHandlers that interact with Output Drivers.
	Output drivers provide the formatting and protocol for a given motion sim control board.
	e.g. DriverSMC3 speaks with a control board running the Simulator Motor Controller 3 firmware
	"""
	def __init__(self, axisCount, driverType: str):
		self.poseHandler = PoseHandler()
		self.outputScaler = None
		self.setupDefaultScaler()
		self.axisHandlers = None
		self.initAxisHandlers(axisCount)
		self.loadAxisInverts()
		self.outputDriver = None
		self.initOutputDriver(driverType)

	def setupDefaultScaler(self):
		# TODO: This should be loaded from somewhere probably in the gameplugin
		self.outputScaler = DataFrame()
		self.outputScaler.pitch = 0.25
		self.outputScaler.roll = 0.25
		self.outputScaler.yaw = 0.0
		self.outputScaler.surge = .35
		self.outputScaler.sway = .35
		self.outputScaler.heave = .15
		self.poseHandler.configScaler(self.outputScaler)

	"""
	Destroy and initialize quantity 'axisCount' of new axisHandler objects
	"""
	def initAxisHandlers(self, axisCount: int):
		self.axisHandlers = [AxisHandler()]
		for i in range(axisCount - 1):
			self.axisHandlers.append(AxisHandler())

	def loadAxisInverts(self):
		# TODO: This needs to load from somewhere with methods instead of inappropriate touching
		self.axisHandlers[0].inverts.pitch = True
		self.axisHandlers[1].inverts.pitch = True

		self.axisHandlers[0].inverts.roll = True

		self.axisHandlers[0].inverts.surge = True
		self.axisHandlers[1].inverts.surge = True

		self.axisHandlers[0].inverts.sway = False
		self.axisHandlers[1].inverts.sway = True

	def initOutputDriver(self, driverType):
		if driverType == "SMC3":
			self.outputDriver = DriverSMC3(self.outputScaler)

	"""
	Pass in the InputHander motion data to the MotionSystem.
	Comes in utils.DataFrame format.
	"""
	def inputMotion(self, dataFrame):
		self.poseHandler.motionInput(dataFrame)

	"""
	Uses the outputDriver to assemble a communication packet to pass elsewhere outside (comHandler)
	Packet will be a bytefield
	"""
	def outputCommand(self):
		axisCount = len(self.axisHandlers)
		# Build the command sequence based on axisCount
		commands: [float] = [0.0]
		for i in range(axisCount - 1):
			commands.append(0.0)

		# Fill the command sequence by axis
		for i, axis in enumerate(self.axisHandlers):
			commands[i] = axis.motionAxisOutput(self.poseHandler.outputs)

		# Use the output driver to generate the command string
		out = self.outputDriver.getOutputCommand(commands, axisCount)

		return out
