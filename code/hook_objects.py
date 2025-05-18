from hooks.game_stats import GameStats
from hooks.event_timer import EventTimer
from hooks.logger import GameLogger

import os

runtime_game_stats = GameStats()

level_duration = EventTimer()  # This is for the Fuzzy Controller
total_duration = EventTimer()  # This is to get the time in general

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

game_logger = GameLogger(directory=LOG_DIR, base_filename="game")
