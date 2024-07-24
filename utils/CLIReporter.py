from plugins.games.DirtRally2 import GamePlugin
import time


class Reporter:
	def __init__(self, gamePlugin: GamePlugin):
		self.gamePlugin = gamePlugin
		self.lastReport = 0
		self.reportInterval = 1.0

	def printReport(self):
		if (time.time() - self.lastReport > self.reportInterval) and self.gamePlugin.getRxStatus():
			print("~~~!!!~~~")
			for attr, value in self.gamePlugin.data.__dict__.items():
				print(str(attr or "") + ": " + str(value or ""))
