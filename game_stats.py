import json

class GameStats():
	"""Track stastistics for alien invasion."""
	def __init__(self, ai_settings):
		"""Initialize stastistics"""
		self.ai_settings = ai_settings
		
		# High score should never be reset.
		self.high_score = 0

		self.reset_stats()
		#Start Alien Invansion in an active stat.
		#self.game_active = True

		# Start game in an inactive state.
		self.game_active = False

		try:
			with open("high_score.json") as f:
				self.high_score = json.load(f)

		except FileNotFoundError:
			self.high_score = 0






	def reset_stats(self):
		"""Initiakize stastics that can change during game."""
		self.ships_left = self.ai_settings.ship_limit
		self.score = 0
		self.level = 1
	