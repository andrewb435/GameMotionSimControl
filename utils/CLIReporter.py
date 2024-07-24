from plugins.games.DirtRally2 import GamePlugin
from utils import DataFrame
import time


class Reporter:
	def __init__(self, gamePlugin: GamePlugin):
		self.gamePlugin = gamePlugin
		self.lastReport = 0
		self.reportInterval = 1.0

	def printTelemetryReport(self):
		if (time.time() - self.lastReport > self.reportInterval) and self.gamePlugin.getRxStatus():
			print("~~~!!!~~~")
			for attr, value in self.gamePlugin.data.__dict__.items():
				print(str(attr or "") + ": " + str(value or ""))

	def printAxisOutputReport(self, pose: DataFrame):
		if time.time() - self.lastReport > self.reportInterval:
			for attr, value in pose.__dict__.items():
				print(str(attr or "") + ": " + str(value or ""))
