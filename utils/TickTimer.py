Copyright © 2024 Andrew Baum

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import time


class TickTimer:
	# Interval in milliseconds
	def __init__(self, interval: int):
		self.interval: int = interval * 1000000
		self.tick: int = time.perf_counter_ns()
		self.tock: int = 0
		self.delta: float = 0.0

	def check(self) -> bool:
		self.tock = time.perf_counter_ns()
		if self.tock - self.tick >= self.interval:
			self.delta = (self.tock - self.tick) / 1000000000
			self.tick = self.tock
			return True
		else:
			return False

	# Returns frame delta as a float in fractional seconds since last frame
	def getDelta(self) -> float:
		return self.delta


class DeltaTimer:
	def __init__(self):
		self.tick: int = time.perf_counter_ns()
		self.tock: int = 0
		self.delta: float = 0.0

	def getDelta(self) -> float:
		self.tock = time.perf_counter_ns()
		self.delta = (self.tock - self.tick) / 1000000000
		self.tick = time.perf_counter_ns()
		return self.delta
