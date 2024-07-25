# Copyright © 2024 Andrew Baum
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from modules.InputHandler import InputHandler
from modules.MotionSystem import MotionSystem
from plugins.outputs.communication.DriverSerial import DriverSerial


def main():
	comHandler = DriverSerial("/dev/ttyACM0")
	inputSystem = InputHandler()
	inputSystem.setupPlugin()
	motionSystem = MotionSystem(2, "SMC3")
	motionSystem.inputMotion(inputSystem.getDataFrame())

	# Debug Stuff
	inputSystem.telemetryDebug = False	# print plugin telemetry data
	inputSystem.axisOutputDebug = False	# print plugin axis output data
	# Debug Stuff

	while True is True:
		if inputSystem.gameStatus() is True:
			inputSystem.update()
			if comHandler.isReady() is True:
				motionSystem.inputMotion(inputSystem.getDataFrame())
				messagebytes = motionSystem.outputCommand()
				comHandler.sendCommand(messagebytes)
		else:
			inputSystem.gameSearch()


if __name__ == "__main__":
	main()
