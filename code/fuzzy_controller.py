import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# input is defined here
health = ctrl.Antecedent(np.arange(0, 101, 1), 'health')  
deaths = ctrl.Antecedent(np.arange(0, 11, 1), 'deaths')     
completion_time = ctrl.Antecedent(np.arange(0, 601, 1), 'completion_time')  # in seconds


# Define output variables (enemy adjustment multipliers)
# These multipliers adjust the current enemy stats.
# For example, 0.8 means enemy health/damage becomes 80% of its original value.
enemy_damage = ctrl.Consequent(np.arange(0.5, 1.51, 0.01), 'enemy_damage')  
enemy_health = ctrl.Consequent(np.arange(0.5, 1.51, 0.01), 'enemy_health')    

# Membership Functions for Inputs
# Health: 0 = worst, 100 = best.
health['critical'] = fuzz.trimf(health.universe, [0, 0, 40])
health['moderate'] = fuzz.trimf(health.universe, [30, 50, 70])
health['optimal'] = fuzz.trimf(health.universe, [60, 100, 100])

# Deaths: Assume a range from 0 to 10 deaths per level.
deaths['few'] = fuzz.trimf(deaths.universe, [0, 0, 3])
deaths['moderate'] = fuzz.trimf(deaths.universe, [2, 5, 7])
deaths['many'] = fuzz.trimf(deaths.universe, [6, 10, 10])

# Completion Time (in seconds):
# Fast: less than 2 minutes (<120s)
# Medium: between 2 and 5 minutes (120s to 300s)
# Slow: more than 5 minutes (>300s)
completion_time['fast'] = fuzz.trimf(completion_time.universe, [0, 0, 120])
completion_time['medium'] = fuzz.trimf(completion_time.universe, [120, 210, 300])
completion_time['slow'] = fuzz.trimf(completion_time.universe, [300, 600, 600])


# membership function for output (we need to adjust with play testing)
# Enemy Damage Adjustment multipliers (you can change these values later)
enemy_damage['decrease'] = fuzz.trimf(enemy_damage.universe, [0.5, 0.6, 0.8])
enemy_damage['slight_decrease'] = fuzz.trimf(enemy_damage.universe, [0.75, 0.85, 0.95])
enemy_damage['keep_same'] = fuzz.trimf(enemy_damage.universe, [0.95, 1.0, 1.05])
enemy_damage['increase'] = fuzz.trimf(enemy_damage.universe, [1.05, 1.2, 1.5])


enemy_health['decrease'] = fuzz.trimf(enemy_health.universe, [0.5, 0.7, 0.9])
enemy_health['keep_same'] = fuzz.trimf(enemy_health.universe, [0.95, 1.0, 1.05])
enemy_health['increase'] = fuzz.trimf(enemy_health.universe, [1.1, 1.3, 1.5])


# Rule 1: If Health is Critical AND Deaths are Many, then Decrease Enemy Damage & Enemy Health.
rule1 = ctrl.Rule(health['critical'] & deaths['many'], 
                  consequent=[enemy_damage['decrease'], enemy_health['decrease']])

# Rule 2: If Health is Optimal AND Deaths are Few, then Increase Enemy Damage & Enemy Health.
rule2 = ctrl.Rule(health['optimal'] & deaths['few'],
                  consequent=[enemy_damage['increase'], enemy_health['increase']])

# Rule 3: If Level Completion Time is Fast AND Health is Optimal, then Increase Enemy Health.
rule3 = ctrl.Rule(completion_time['fast'] & health['optimal'], 
                  consequent=enemy_health['increase'])

# Rule 4: If Deaths are Moderate, then Keep Enemy Damage & Health the Same.
rule4 = ctrl.Rule(deaths['moderate'],
                  consequent=[enemy_damage['keep_same'], enemy_health['keep_same']])

# Rule 5: If Health is Critical AND Level Completion Time is Slow, then Decrease Enemy Damage.
rule5 = ctrl.Rule(health['critical'] & completion_time['slow'],
                  consequent=enemy_damage['decrease'])

# Rule 6: If Deaths are Many AND Level Completion Time is Slow, then Decrease Enemy Health.
rule6 = ctrl.Rule(deaths['many'] & completion_time['slow'],
                  consequent=enemy_health['decrease'])

# Rule 7: If Deaths are Few AND Level Completion Time is Fast, then Increase Enemy Damage.
rule7 = ctrl.Rule(deaths['few'] & completion_time['fast'],
                  consequent=enemy_damage['increase'])

# Rule 8: If Health is Moderate AND Deaths are Many, then Slightly Decrease Enemy Damage.
rule8 = ctrl.Rule(health['moderate'] & deaths['many'],
                  consequent=enemy_damage['slight_decrease'])

# Rule 9: If Health is Moderate AND Deaths are Few, then Keep Enemy Damage & Health the Same.
rule9 = ctrl.Rule(health['moderate'] & deaths['few'],
                  consequent=[enemy_damage['keep_same'], enemy_health['keep_same']])


difficulty_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
difficulty_sim = ctrl.ControlSystemSimulation(difficulty_ctrl)


def check_DDA_adjust_difficulty(player_health, player_deaths, level_time_sec):
    """
    Calculate adjustment multipliers for enemy damage and health based on player's level performance.
    
    Parameters:
      - player_health: Player's health at end of level (0-100)
      - player_deaths: Number of deaths in the level (0-10)
      - level_time_sec: Level completion time in seconds
      
    Returns:
      - Tuple (enemy_damage_multiplier, enemy_health_multiplier)
      
    Note: The returned multipliers are applied to enemy attributes.
            (e.g., a multiplier of 0.8 reduces the stat by 20%).
            You can adjust the ranges in the output membership functions as needed.
    """
    difficulty_sim.input['health'] = player_health
    difficulty_sim.input['deaths'] = player_deaths
    difficulty_sim.input['completion_time'] = level_time_sec
    
    # Compute the fuzzy system result
    difficulty_sim.compute()
    
    return difficulty_sim.output['enemy_damage'], difficulty_sim.output['enemy_health']


 
if __name__ == "__main__":
    
    player_health = 35   # pretty low   
    player_deaths = 7  #This guys trash     
    level_time_sec = 360   # slow
    
    damage_multiplier, health_multiplier = check_DDA_adjust_difficulty(
        player_health, player_deaths, level_time_sec
    )
    
    
    print(f"Enemy Damage Multiplier: {damage_multiplier:.2f}")
    print(f"Enemy Health Multiplier: {health_multiplier:.2f}")