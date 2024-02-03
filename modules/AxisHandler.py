Copyright © 2024 Andrew Baum

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from utils.DataFrame import DataFrame
"""
AxisHanlder takes the idealized normalized complete pose frame in and returns a single float representing the
axis-specific representation of the pose
"""


class AxisHandler:
	def __init__(self):
		self.inverts = DataFrame()
		self.axisPose = DataFrame()

	def loadInverts(self, invertFrame: DataFrame):
		self.inverts = invertFrame

	def motionOutputInverts(self, dataFrame: DataFrame) -> DataFrame:
		output = DataFrame()
		output.pitch = (dataFrame.pitch * -1) if self.inverts.pitch else dataFrame.pitch
		output.roll = (dataFrame.roll * -1) if self.inverts.roll else dataFrame.roll
		output.yaw = (dataFrame.yaw * -1) if self.inverts.yaw else dataFrame.yaw
		output.surge = (dataFrame.surge * -1) if self.inverts.surge else dataFrame.surge
		output.sway = (dataFrame.sway * -1) if self.inverts.sway else dataFrame.sway
		output.heave = (dataFrame.heave * -1) if self.inverts.heave else dataFrame.heave
		return output

	def motionAxisOutput(self, dataFrame: DataFrame) -> float:
		"""
		Takes in an idealized output pose and adds axis-specific modifications such as inversions
		:param dataFrame: Idealized output pose of motion sim to be converted to axis specific pose
		:return: axis commanded position in range of -1.0 to 1.0
		"""
		self.axisPose = self.motionOutputInverts(dataFrame)
		integratedOutput: float = (
			self.axisPose.pitch
			+ self.axisPose.roll
			+ self.axisPose.yaw
			+ self.axisPose.surge
			+ self.axisPose.sway
			+ self.axisPose.heave
		)
		return integratedOutput
