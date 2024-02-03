Copyright © 2024 Andrew Baum

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from utils.DataFrame import DataFrame


class PoseHandler:
	def __init__(self):
		# internal data
		self.scalerData = DataFrame()

		# Mapped target outputs
		self.outputs = DataFrame()
		self.outputs.pitch = 0
		self.outputs.roll = 0
		self.outputs.yaw = 0
		self.outputs.surge = 0
		self.outputs.sway = 0
		self.outputs.heave = 0

	"""
	Takes a DataFrame in with normalized gamedata and scales it to the internal axis scalers to generate a DataFrame
	containing a normalized, scaled output pose
	"""
	def motionInput(self, dataFrame: DataFrame):
		out = DataFrame()
		out.pitch = dataFrame.pitch * self.scalerData.pitch
		out.roll = dataFrame.roll * self.scalerData.roll
		out.yaw = dataFrame.yaw * self.scalerData.yaw
		out.surge = dataFrame.surge * self.scalerData.surge
		out.sway = dataFrame.sway * self.scalerData.sway
		out.heave = dataFrame.heave * self.scalerData.heave
		self.outputs = out

	def motionOutput(self) -> DataFrame:
		return self.outputs

	def configScaler(self, dataFrame: DataFrame):
		self.scalerData = dataFrame
