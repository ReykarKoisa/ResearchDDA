# level_handler.py
from settings import *
from map import LEVEL_1_MAP,LEVEL_2_MAP

class LevelHandler:
    def __init__(self, game):
        self.game = game
        self.levels = [
            {"map": LEVEL_1_MAP, "enemy_count": 10, "player_pos": (1.5, 1.5)},  # Basic Level
            {"map": LEVEL_2_MAP, "enemy_count": 15, "player_pos": (2.5, 2.5)},
        ]
        self.current_level = 0

    def load_level(self):
        level_data = self.levels[self.current_level]
        # Load the correct level map
  # ✅ Set map reference at runtime, not during init
        self.game.map.mini_map = level_data["map"]  
        self.game.map.world_map = {}  
        self.game.map.get_map()  
        self.game.object_handler.npc_list = []  
        self.game.object_handler.npc_positions = set()  
        self.game.object_handler.spawn_npc_custom(level_data["enemy_count"])
        self.game.player.x, self.game.player.y = level_data["player_pos"]

    def next_level(self):
        self.current_level = (self.current_level + 1) % len(self.levels)
        self.load_level()

    def restart_level(self):
        self.load_level()
