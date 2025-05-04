import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Define input variables
# Player health at the end of the level (0-100)
health = ctrl.Antecedent(np.arange(0, 101, 1), 'health')
# Number of times the player died during the level (0-10)
deaths = ctrl.Antecedent(np.arange(0, 11, 1), 'deaths')
# Time taken to complete the level in seconds (0-600)
completion_time = ctrl.Antecedent(np.arange(0, 601, 1), 'completion_time')

# Define output variables (enemy adjustment multipliers)
# Multiplier for enemy damage (0.5 = 50%, 1.0 = 100%, 1.5 = 150%)
enemy_damage = ctrl.Consequent(np.arange(0.5, 1.51, 0.01), 'enemy_damage')
# Multiplier for enemy health (0.5 = 50%, 1.0 = 100%, 1.5 = 150%)
enemy_health = ctrl.Consequent(np.arange(0.5, 1.51, 0.01), 'enemy_health')

# --- Membership Functions for Inputs ---

# Health: Lower is worse, higher is better.
# Critical: Low health remaining.
health['critical'] = fuzz.trimf(health.universe, [0, 0, 40])
# Moderate: Medium health remaining.
health['moderate'] = fuzz.trimf(health.universe, [30, 50, 70])
# Optimal: High health remaining.
health['optimal'] = fuzz.trimf(health.universe, [60, 100, 100])

# Deaths: Lower is better, higher is worse.
# Few: Player died very few times or not at all.
deaths['few'] = fuzz.trimf(deaths.universe, [0, 0, 3])
# Moderate: Player died a moderate number of times.
deaths['moderate'] = fuzz.trimf(deaths.universe, [2, 5, 7])
# Many: Player died many times.
deaths['many'] = fuzz.trimf(deaths.universe, [6, 10, 10])

# Completion Time: Lower (faster) is generally better.
# Fast: Completed the level quickly (< 2 minutes).
completion_time['fast'] = fuzz.trimf(completion_time.universe, [0, 0, 120])
# Medium: Completed the level in a moderate amount of time (2-5 minutes).
completion_time['medium'] = fuzz.trimf(completion_time.universe, [120, 210, 300])
# Slow: Took a long time to complete the level (> 5 minutes).
completion_time['slow'] = fuzz.trimf(completion_time.universe, [300, 600, 600])

# --- Membership Functions for Outputs ---
# Define how much to adjust enemy stats based on performance.

# Enemy Damage Adjustment:
# Decrease: Significantly reduce enemy damage (easier).
enemy_damage['decrease'] = fuzz.trimf(enemy_damage.universe, [0.5, 0.6, 0.8])
# Slight Decrease: Slightly reduce enemy damage.
enemy_damage['slight_decrease'] = fuzz.trimf(enemy_damage.universe, [0.75, 0.85, 0.95])
# Keep Same: No change to enemy damage.
enemy_damage['keep_same'] = fuzz.trimf(enemy_damage.universe, [0.95, 1.0, 1.05])
# Increase: Increase enemy damage (harder).
enemy_damage['increase'] = fuzz.trimf(enemy_damage.universe, [1.05, 1.2, 1.5])

# Enemy Health Adjustment:
# Decrease: Significantly reduce enemy health (easier).
enemy_health['decrease'] = fuzz.trimf(enemy_health.universe, [0.5, 0.7, 0.9])
# Keep Same: No change to enemy health.
enemy_health['keep_same'] = fuzz.trimf(enemy_health.universe, [0.95, 1.0, 1.05])
# Increase: Increase enemy health (harder).
enemy_health['increase'] = fuzz.trimf(enemy_health.universe, [1.1, 1.3, 1.5])


# --- Fuzzy Rules ---
# Define the logic connecting inputs to outputs.

# Rule 1: Player struggling badly (low health, many deaths). Make enemies much easier.
rule1 = ctrl.Rule(health['critical'] & deaths['many'],
                  consequent=[enemy_damage['decrease'], enemy_health['decrease']])

# Rule 2: Player performing very well (high health, few deaths). Make enemies harder.
rule2 = ctrl.Rule(health['optimal'] & deaths['few'],
                  consequent=[enemy_damage['increase'], enemy_health['increase']])

# Rule 3: Player finishing quickly with high health. Increase enemy durability.
rule3 = ctrl.Rule(completion_time['fast'] & health['optimal'],
                  consequent=enemy_health['increase'])

# Rule 4: Player dying moderately often. Maintain current difficulty.
rule4 = ctrl.Rule(deaths['moderate'],
                  consequent=[enemy_damage['keep_same'], enemy_health['keep_same']])

# Rule 5: Player barely surviving and taking a long time. Reduce enemy threat.
rule5 = ctrl.Rule(health['critical'] & completion_time['slow'],
                  consequent=enemy_damage['decrease'])

# Rule 6: Player dying a lot and taking a long time. Reduce enemy durability.
rule6 = ctrl.Rule(deaths['many'] & completion_time['slow'],
                  consequent=enemy_health['decrease'])

# Rule 7: Player finishing quickly with few deaths (likely skilled). Increase enemy threat.
rule7 = ctrl.Rule(deaths['few'] & completion_time['fast'],
                  consequent=enemy_damage['increase'])

# Rule 8: Player has moderate health but died many times. Slightly reduce enemy threat.
rule8 = ctrl.Rule(health['moderate'] & deaths['many'],
                  consequent=enemy_damage['slight_decrease'])

# Rule 9: Player has moderate health and few deaths. Maintain current difficulty.
rule9 = ctrl.Rule(health['moderate'] & deaths['few'],
                  consequent=[enemy_damage['keep_same'], enemy_health['keep_same']])

# --- Rule 10 (NEW): Player has optimal health, but died many times and took a long time. ---
# This scenario might indicate the player is good defensively but struggles with
# enemy health/damage over prolonged fights. Slightly decrease damage, keep health same.
rule10 = ctrl.Rule(health['optimal'] & deaths['many'] & completion_time['slow'],
                   consequent=[enemy_damage['slight_decrease'], enemy_health['keep_same']])


# --- Control System Creation and Simulation ---

# Create the control system with all the rules
# *Added rule10 to the list*
difficulty_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10])

# Create a simulation instance from the control system
difficulty_sim = ctrl.ControlSystemSimulation(difficulty_ctrl)


def check_DDA_adjust_difficulty(player_health, player_deaths, level_time_sec):
    """
    Calculate adjustment multipliers for enemy damage and health based on player's level performance.

    Parameters:
      - player_health (float): Player's health at end of level (0-100).
      - player_deaths (int): Number of deaths in the level (0-10).
      - level_time_sec (float): Level completion time in seconds (e.g., 0-600).

    Returns:
      - tuple (float, float): (enemy_damage_multiplier, enemy_health_multiplier)
        These multipliers indicate how to adjust the base stats for the next level/encounter.
        e.g., 0.8 means 80% of original stat, 1.2 means 120% of original stat.
        Returns (1.0, 1.0) if computation fails for any reason.
    """
    try:
        # Pass inputs to the ControlSystemSimulation
        difficulty_sim.input['health'] = player_health
        difficulty_sim.input['deaths'] = player_deaths
        difficulty_sim.input['completion_time'] = level_time_sec

        # Compute the fuzzy system result
        difficulty_sim.compute()

        # Retrieve the defuzzified output values
        damage_output = difficulty_sim.output['enemy_damage']
        health_output = difficulty_sim.output['enemy_health']

        return damage_output, health_output

    except KeyError as e:
        print(f"Warning: Could not compute output for {e}. Rules might not cover this input combination.")
        print("Inputs: health={player_health}, deaths={player_deaths}, time={level_time_sec}")
        # Return default multipliers (no change) if a key is missing
        return 1.0, 1.0
    except Exception as e:
        print(f"An unexpected error occurred during fuzzy computation: {e}")
        # Return default multipliers for other unexpected errors
        return 1.0, 1.0


# --- Example Usage ---
if __name__ == "__main__":

    # Test Case 1: The problematic one (High Health, Many Deaths, Slow Time)
    print("--- Test Case 1 ---")
    player_health_1 = 99
    player_deaths_1 = 7
    level_time_sec_1 = 360

    damage_multiplier_1, health_multiplier_1 = check_DDA_adjust_difficulty(
        player_health_1, player_deaths_1, level_time_sec_1
    )

    print(f"Inputs: Health={player_health_1}, Deaths={player_deaths_1}, Time={level_time_sec_1}s")
    print(f"Output: Enemy Damage Multiplier: {damage_multiplier_1:.2f}")
    print(f"Output: Enemy Health Multiplier: {health_multiplier_1:.2f}\n")


    # Test Case 2: Original working case (Moderate Health, Many Deaths, Slow Time)
    print("--- Test Case 2 ---")
    player_health_2 = 60
    player_deaths_2 = 7
    level_time_sec_2 = 360

    damage_multiplier_2, health_multiplier_2 = check_DDA_adjust_difficulty(
        player_health_2, player_deaths_2, level_time_sec_2
    )

    print(f"Inputs: Health={player_health_2}, Deaths={player_deaths_2}, Time={level_time_sec_2}s")
    print(f"Output: Enemy Damage Multiplier: {damage_multiplier_2:.2f}")
    print(f"Output: Enemy Health Multiplier: {health_multiplier_2:.2f}\n")

    # Test Case 3: Skilled player (High Health, Few Deaths, Fast Time)
    print("--- Test Case 3 ---")
    player_health_3 = 90
    player_deaths_3 = 1
    level_time_sec_3 = 100 # Fast

    damage_multiplier_3, health_multiplier_3 = check_DDA_adjust_difficulty(
        player_health_3, player_deaths_3, level_time_sec_3
    )
    print(f"Inputs: Health={player_health_3}, Deaths={player_deaths_3}, Time={level_time_sec_3}s")
    print(f"Output: Enemy Damage Multiplier: {damage_multiplier_3:.2f}")
    print(f"Output: Enemy Health Multiplier: {health_multiplier_3:.2f}\n")

    # Test Case 4: Struggling player (Low Health, Many Deaths, Slow Time)
    print("--- Test Case 4 ---")
    player_health_4 = 20 # Critical
    player_deaths_4 = 8  # Many
    level_time_sec_4 = 450 # Slow

    damage_multiplier_4, health_multiplier_4 = check_DDA_adjust_difficulty(
        player_health_4, player_deaths_4, level_time_sec_4
    )
    print(f"Inputs: Health={player_health_4}, Deaths={player_deaths_4}, Time={level_time_sec_4}s")
    print(f"Output: Enemy Damage Multiplier: {damage_multiplier_4:.2f}")
    print(f"Output: Enemy Health Multiplier: {health_multiplier_4:.2f}\n")
