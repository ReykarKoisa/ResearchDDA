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

# Rule 10: Player has optimal health, but died many times and took a long time.
# Good defense but struggles offensively over time? Slightly decrease damage, keep health same.
rule10 = ctrl.Rule(health['optimal'] & deaths['many'] & completion_time['slow'],
                   consequent=[enemy_damage['slight_decrease'], enemy_health['keep_same']])

# --- Rule 11: Player has critical health, few deaths, and fast time. ---
# This covers the edge case where the player is fast and efficient but vulnerable.
# Keep enemy health the same, let Rule 7 increase damage slightly due to speed/few deaths.
rule11 = ctrl.Rule(health['critical'] & deaths['few'] & completion_time['fast'],
                   consequent=enemy_health['keep_same'])


# --- Control System Creation and Simulation ---

# Create the control system with all the rules
# *Added rule11 to the list*
difficulty_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11])

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
        # Clip inputs to ensure they are within the defined universe ranges
        difficulty_sim.input['health'] = np.clip(player_health, 0, 100)
        difficulty_sim.input['deaths'] = np.clip(player_deaths, 0, 10)
        difficulty_sim.input['completion_time'] = np.clip(level_time_sec, 0, 600)

        # Compute the fuzzy system result
        difficulty_sim.compute()

        # Retrieve the defuzzified output values
        # Use .get() with a default value for extra safety
        damage_output = difficulty_sim.output.get('enemy_damage', 1.0)
        health_output = difficulty_sim.output.get('enemy_health', 1.0)

        # Handle potential NaN or Inf values if compute somehow fails silently
        if not np.isfinite(damage_output):
            print(f"Warning: Computed damage output is not finite ({damage_output}). Defaulting to 1.0.")
            damage_output = 1.0
        if not np.isfinite(health_output):
            print(f"Warning: Computed health output is not finite ({health_output}). Defaulting to 1.0.")
            health_output = 1.0

        return damage_output, health_output

    except KeyError as e:
        # This block should ideally not be hit now with the added rule, but kept as a safeguard
        print(f"Warning: Could not compute output for {e}. Rules might not cover this input combination.")
        print(f"Inputs: health={player_health}, deaths={player_deaths}, time={level_time_sec}")
        # Return default multipliers (no change) if a key is missing
        return 1.0, 1.0
    except Exception as e:
        print(f"An unexpected error occurred during fuzzy computation: {e}")
        # Return default multipliers for other unexpected errors
        return 1.0, 1.0


# --- Example Usage ---
if __name__ == "__main__":

    # Define a helper function for running and printing tests
    def run_test(test_name, health_val, deaths_val, time_val):
        print(f"--- {test_name} ---")
        damage_mult, health_mult = check_DDA_adjust_difficulty(
            health_val, deaths_val, time_val
        )
        print(f"Inputs: Health={health_val}, Deaths={deaths_val}, Time={time_val}s")
        print(f"Output: Enemy Damage Multiplier: {damage_mult:.2f}")
        print(f"Output: Enemy Health Multiplier: {health_mult:.2f}\n")

    # --- Original Test Cases ---
    print("--- Original Test Cases ---")
    run_test("Test Case 1: Problematic (High Health, Many Deaths, Slow Time)", 100, 7, 360)
    run_test("Test Case 2: Original Working (Mod Health, Many Deaths, Slow Time)", 60, 7, 360)
    run_test("Test Case 3: Skilled Player (High Health, Few Deaths, Fast Time)", 90, 1, 100)
    run_test("Test Case 4: Struggling Player (Low Health, Many Deaths, Slow Time)", 20, 8, 450)

    # --- Additional Test Cases ---
    print("--- Additional Test Cases ---")
    run_test("Test Case 5: Average Player (Mod Health, Mod Deaths, Med Time)", 55, 5, 250)
    run_test("Test Case 6: Careful but Slow (Low Health, Few Deaths, Slow Time)", 30, 2, 500)
    run_test("Test Case 7: Fast but Reckless (Mod Health, Many Deaths, Fast Time)", 65, 9, 110)
    run_test("Test Case 8: Perfect Run (Optimal Health, Zero Deaths, Fast Time)", 100, 0, 90)
    run_test("Test Case 9: Near Death, Many Deaths, Medium Time", 5, 10, 280)
    run_test("Test Case 10: Boundary Low (Min Values)", 0, 0, 0)
    run_test("Test Case 11: Boundary High (Max Values)", 100, 10, 600)
    run_test("Test Case 12: Moderate Health, Few Deaths, Slow Time", 50, 2, 400)

    # --- Edge Case / Boundary / Transition Tests ---
    print("\n--- Edge Case / Boundary / Transition Tests ---")
    # Health Boundaries/Transitions
    run_test("Edge Case 13: Health exactly at Critical/Moderate boundary", 30, 5, 200) # Health=30
    run_test("Edge Case 14: Health exactly at Moderate peak", 50, 5, 200) # Health=50
    run_test("Edge Case 15: Health exactly at Moderate/Optimal boundary", 70, 5, 200) # Health=70
    run_test("Edge Case 16: Health just inside Optimal", 61, 5, 200) # Health=61

    # Deaths Boundaries/Transitions
    run_test("Edge Case 17: Deaths exactly at Few/Moderate boundary", 2, 80, 200) # Deaths=2
    run_test("Edge Case 18: Deaths exactly at Moderate peak", 5, 80, 200) # Deaths=5
    run_test("Edge Case 19: Deaths exactly at Moderate/Many boundary", 7, 80, 200) # Deaths=7
    run_test("Edge Case 20: Deaths just inside Many", 6, 80, 200) # Deaths=6 (Note: trimf makes 6 = 0 for moderate, 1 for many)

    # Time Boundaries/Transitions
    run_test("Edge Case 21: Time exactly at Fast/Medium boundary", 50, 5, 120) # Time=120
    run_test("Edge Case 22: Time exactly at Medium peak", 50, 5, 210) # Time=210
    run_test("Edge Case 23: Time exactly at Medium/Slow boundary", 50, 5, 300) # Time=300
    run_test("Edge Case 24: Time just inside Slow", 50, 5, 301) # Time=301

    # Combinations potentially stressing rules
    run_test("Edge Case 25: Optimal Health, Moderate Deaths, Fast Time", 90, 5, 100)
    run_test("Edge Case 26: Critical Health, Moderate Deaths, Slow Time", 10, 5, 500)
    run_test("Edge Case 27: Moderate Health, Few Deaths, Fast Time", 50, 1, 100)
    run_test("Edge Case 28: Moderate Health, Many Deaths, Medium Time", 50, 9, 250)
    run_test("Edge Case 29: Optimal Health, Many Deaths, Fast Time", 90, 10, 115) # Should trigger decrease? (Rule 10 needs slow time)

