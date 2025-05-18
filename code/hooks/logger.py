import logging
import os
import glob


class GameLogger:
    def __init__(self, directory: str = "logs", base_filename: str = "game"):
        """
        Initialize the GameLogger.
        Automatically determines the next participant number based on existing log files
        in `directory` following the pattern `{base_filename}_participant_*.log`,
        then creates a new log file for that participant and logs the turn start.
        """
        # Determine existing participant files
        pattern = os.path.join(directory, f"{base_filename}_participant_*.log")
        existing = glob.glob(pattern)
        # Next participant number is count + 1
        self.current_participant = len(existing) + 1
        # Create filename for this participant
        filename = os.path.join(
            directory, f"{base_filename}_participant_{self.current_participant}.log"
        )
        # Configure logger
        logging.basicConfig(
            filename=filename,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger(f"GameLogger_P{self.current_participant}")
        # Log the start of this participant's turn
        self.log_turn_start()

    def log_turn_start(self):
        """Log the start of the current participant's turn."""
        self.logger.info(f"Event: TurnStart | Participant: {self.current_participant}")

    def log_death(
        self,
        health: float,
        deaths: int,
        time_taken: float,
        health_mult: float,
        damage_mult: float,
    ):
        """Log a death event for the current participant with game metrics."""
        self.logger.info(
            f"Event: Death | Participant: {self.current_participant} | "
            f"Health: {health} | Deaths: {deaths} | TimeTaken: {time_taken} | "
            f"HealthMult: {health_mult} | DamageMult: {damage_mult}"
        )

    def log_level_complete(
        self,
        health: float,
        deaths: int,
        time_taken: float,
        health_mult: float,
        damage_mult: float,
    ):
        """Log a level completion event for the current participant."""
        self.logger.info(
            f"Event: LevelComplete | Participant: {self.current_participant} | "
            f"Health: {health} | Deaths: {deaths} | TimeTaken: {time_taken} | "
            f"HealthMult: {health_mult} | DamageMult: {damage_mult}"
        )

    def log_total_duration(self, total_duration: float):
        """Log the total duration of the game session for the current participant."""
        self.logger.info(f"Total_duration: {total_duration}")


# Example usage:
# logger = GameLogger(directory='logs', base_filename='game')
# # Automatically creates 'logs/game_participant_1.log' or next available
# logger.log_death(level=1, health=100, deaths=1, time_taken=35.7,
#                  health_mult=80, damage_mult=15)
# logger.log_level_complete(level=1, health=75, deaths=1,
#                           time_taken=47.2, health_mult=60,
#                           damage_mult=18)
# logger.log_total_duration(120.5)

# For a second run, it'll create 'logs/game_participant_2.log' automatically.
