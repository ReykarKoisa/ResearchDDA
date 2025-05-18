import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Define input variables
# Player health at the end of the level (0-100)
health = ctrl.Antecedent(np.arange(0, 101, 1), "health")
# Number of times the player died during the level (0-10)
deaths = ctrl.Antecedent(np.arange(0, 11, 1), "deaths")
# Time taken to complete the level in seconds (0-600)
completion_time = ctrl.Antecedent(np.arange(0, 601, 1), "completion_time")

# Define output variables (enemy adjustment multipliers)
# Wider range for more sensitive adjustments (0.4-1.6 instead of 0.5-1.5)
enemy_damage = ctrl.Consequent(np.arange(0.4, 1.61, 0.01), "enemy_damage")
enemy_health = ctrl.Consequent(np.arange(0.4, 1.61, 0.01), "enemy_health")

# --- Membership Functions for Inputs ---
# Increasing overlap for more sensitivity

# Health: Lower is worse, higher is better.
health["critical"] = fuzz.trimf(health.universe, [0, 25, 60])  # Was [0, 20, 55]
health["moderate"] = fuzz.trimf(health.universe, [30, 60, 85])  # Was [40, 60, 80]
health["optimal"] = fuzz.trimf(health.universe, [60, 85, 100])  # Was [65, 85, 100]

# Deaths: Lower is better, higher is worse.
deaths["few"] = fuzz.trimf(deaths.universe, [0, 1, 5])  # Was [0, 1, 4]
deaths["moderate"] = fuzz.trimf(deaths.universe, [1, 5, 8])  # Was [2, 5, 8]
deaths["many"] = fuzz.trimf(deaths.universe, [5, 10, 10])  # Was [6, 10, 10]

# Completion Time: Lower (faster) is generally better.
completion_time["fast"] = fuzz.trimf(
    completion_time.universe, [0, 90, 240]
)  # Was [0, 90, 210]
completion_time["medium"] = fuzz.trimf(
    completion_time.universe, [150, 300, 450]
)  # Was [180, 300, 420]
completion_time["slow"] = fuzz.trimf(
    completion_time.universe, [300, 480, 600]
)  # Was [360, 480, 600]

# --- Membership Functions for Outputs ---
# More extreme adjustments for clearer difficulty changes

# Enemy Damage Adjustment:
enemy_damage["decrease"] = fuzz.trimf(
    enemy_damage.universe, [0.4, 0.6, 0.85]
)  # Was [0.5, 0.65, 0.85]
enemy_damage["slight_decrease"] = fuzz.trimf(
    enemy_damage.universe, [0.75, 0.85, 0.97]
)  # Was [0.80, 0.90, 0.97]
enemy_damage["keep_same"] = fuzz.trimf(
    enemy_damage.universe, [0.92, 1.0, 1.08]
)  # Was [0.95, 1.0, 1.05]
enemy_damage["slight_increase"] = fuzz.trimf(
    enemy_damage.universe, [1.03, 1.15, 1.25]
)  # New category
enemy_damage["increase"] = fuzz.trimf(
    enemy_damage.universe, [1.15, 1.35, 1.6]
)  # Was [1.03, 1.2, 1.5]

# Enemy Health Adjustment:
enemy_health["decrease"] = fuzz.trimf(
    enemy_health.universe, [0.4, 0.65, 0.9]
)  # Was [0.5, 0.7, 0.92]
enemy_health["slight_decrease"] = fuzz.trimf(
    enemy_health.universe, [0.75, 0.85, 0.97]
)  # New category
enemy_health["keep_same"] = fuzz.trimf(
    enemy_health.universe, [0.92, 1.0, 1.08]
)  # Was [0.95, 1.0, 1.05]
enemy_health["slight_increase"] = fuzz.trimf(
    enemy_health.universe, [1.03, 1.15, 1.25]
)  # New category
enemy_health["increase"] = fuzz.trimf(
    enemy_health.universe, [1.15, 1.35, 1.6]
)  # Was [1.03, 1.25, 1.5]


# --- Fuzzy Rules ---
# More nuanced rules to increase sensitivity

# Rule 1: Player struggling badly (low health, many deaths). Make enemies much easier.
rule1 = ctrl.Rule(
    health["critical"] & deaths["many"],
    consequent=[enemy_damage["decrease"], enemy_health["decrease"]],
)

# Rule 2: Player performing very well (high health, few deaths). Make enemies harder.
rule2 = ctrl.Rule(
    health["optimal"] & deaths["few"],
    consequent=[enemy_damage["increase"], enemy_health["increase"]],
)

# Rule 3: Player finishing quickly with high health. Increase enemy durability.
rule3 = ctrl.Rule(
    completion_time["fast"] & health["optimal"],
    consequent=[enemy_damage["slight_increase"], enemy_health["increase"]],
)

# Rule 4: Player dying moderately often with moderate health. Small adjustment.
rule4 = ctrl.Rule(
    deaths["moderate"] & health["moderate"],
    consequent=[enemy_damage["slight_decrease"], enemy_health["keep_same"]],
)

# Rule 5: Player barely surviving and taking a long time. Reduce enemy threat.
rule5 = ctrl.Rule(
    health["critical"] & completion_time["slow"],
    consequent=[enemy_damage["decrease"], enemy_health["slight_decrease"]],
)

# Rule 6: Player dying a lot and taking a long time. Reduce enemy durability.
rule6 = ctrl.Rule(
    deaths["many"] & completion_time["slow"],
    consequent=[enemy_damage["decrease"], enemy_health["decrease"]],
)

# Rule 7: Player finishing quickly with few deaths (likely skilled). Increase enemy threat.
rule7 = ctrl.Rule(
    deaths["few"] & completion_time["fast"],
    consequent=[enemy_damage["increase"], enemy_health["slight_increase"]],
)

# Rule 8: Player has moderate health but died many times. Reduce enemy threat.
rule8 = ctrl.Rule(
    health["moderate"] & deaths["many"],
    consequent=[enemy_damage["decrease"], enemy_health["slight_decrease"]],
)

# Rule 9: Player has moderate health and few deaths. Slightly increase difficulty.
rule9 = ctrl.Rule(
    health["moderate"] & deaths["few"],
    consequent=[enemy_damage["slight_increase"], enemy_health["slight_increase"]],
)

# Rule 10: Player has optimal health, but died many times and took a long time.
rule10 = ctrl.Rule(
    health["optimal"] & deaths["many"] & completion_time["slow"],
    consequent=[enemy_damage["decrease"], enemy_health["keep_same"]],
)

# Rule 11: Player has critical health, few deaths, and fast time.
rule11 = ctrl.Rule(
    health["critical"] & deaths["few"] & completion_time["fast"],
    consequent=[enemy_damage["slight_decrease"], enemy_health["keep_same"]],
)

# Rule 12: Player has moderate health, moderate deaths, and medium time - typical average performance
rule12 = ctrl.Rule(
    health["moderate"] & deaths["moderate"] & completion_time["medium"],
    consequent=[enemy_damage["keep_same"], enemy_health["keep_same"]],
)

# Rule 13: Player has optimal health but medium time - good survivability but not rushing
rule13 = ctrl.Rule(
    health["optimal"] & completion_time["medium"],
    consequent=[enemy_damage["slight_increase"], enemy_health["slight_increase"]],
)

# Rule 14: Player has few deaths but slow time - careful but needs encouragement to be faster
rule14 = ctrl.Rule(
    deaths["few"] & completion_time["slow"],
    consequent=[enemy_damage["keep_same"], enemy_health["slight_decrease"]],
)

# Rule 15: Player has critical health but medium time - they're struggling with health management
rule15 = ctrl.Rule(
    health["critical"] & completion_time["medium"],
    consequent=[enemy_damage["decrease"], enemy_health["keep_same"]],
)


# --- Control System Creation and Simulation ---

# Create the control system with all the rules
difficulty_ctrl = ctrl.ControlSystem(
    [
        rule1,
        rule2,
        rule3,
        rule4,
        rule5,
        rule6,
        rule7,
        rule8,
        rule9,
        rule10,
        rule11,
        rule12,
        rule13,
        rule14,
        rule15,
    ]
)

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
        difficulty_sim.input["health"] = np.clip(player_health, 0, 100)
        difficulty_sim.input["deaths"] = np.clip(player_deaths, 0, 10)
        difficulty_sim.input["completion_time"] = np.clip(level_time_sec, 0, 600)

        # Compute the fuzzy system result
        difficulty_sim.compute()

        # Retrieve the defuzzified output values
        # Use .get() with a default value for extra safety
        damage_output = difficulty_sim.output.get("enemy_damage", 1.0)
        health_output = difficulty_sim.output.get("enemy_health", 1.0)

        # Handle potential NaN or Inf values if compute somehow fails silently
        if not np.isfinite(damage_output):
            print(
                f"Warning: Computed damage output is not finite ({damage_output}). Defaulting to 1.0."
            )
            damage_output = 1.0
        if not np.isfinite(health_output):
            print(
                f"Warning: Computed health output is not finite ({health_output}). Defaulting to 1.0."
            )
            health_output = 1.0

        return damage_output, health_output

    except KeyError as e:
        print(
            f"Warning: Could not compute output for {e}. Rules might not cover this input combination."
        )
        print(
            f"Inputs: health={player_health}, deaths={player_deaths}, time={level_time_sec}"
        )
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

    # --- Test Cases ---
    print("=== TESTING DYNAMIC DIFFICULTY ADJUSTMENT ===\n")

    # Original Test Cases
    print("--- Original Test Cases ---")
    run_test("Test Case 1: High Health, Many Deaths, Slow Time", 100, 7, 360)
    run_test("Test Case 2: Moderate Health, Many Deaths, Slow Time", 60, 7, 360)
    run_test(
        "Test Case 3: Skilled Player (High Health, Few Deaths, Fast Time)", 90, 1, 100
    )
    run_test(
        "Test Case 4: Struggling Player (Low Health, Many Deaths, Slow Time)",
        20,
        8,
        450,
    )

    # Additional Test Cases
    print("\n--- Additional Test Cases ---")
    run_test(
        "Test Case 5: Average Player (Mod Health, Mod Deaths, Med Time)", 55, 5, 250
    )
    run_test(
        "Test Case 6: Careful but Slow (Low Health, Few Deaths, Slow Time)", 30, 2, 500
    )
    run_test(
        "Test Case 7: Fast but Reckless (Mod Health, Many Deaths, Fast Time)",
        65,
        9,
        110,
    )
    run_test(
        "Test Case 8: Perfect Run (Optimal Health, Zero Deaths, Fast Time)", 100, 0, 90
    )

    # Edge Cases
    print("\n--- Edge Cases ---")
    run_test("Edge Case 1: Barely Alive (Health=1)", 1, 5, 300)
    run_test("Edge Case 2: Maximum Deaths (Deaths=10)", 50, 10, 300)
    run_test("Edge Case 3: Extremely Fast (Time=30s)", 50, 5, 30)
    run_test("Edge Case 4: Almost Timeout (Time=590s)", 50, 5, 590)

    # Transition Cases
    print("\n--- Transition Cases ---")
    run_test("Transition 1: Critical to Moderate Health", 45, 5, 300)
    run_test("Transition 2: Few to Moderate Deaths", 50, 3, 300)
    run_test("Transition 3: Fast to Medium Time", 50, 5, 195)
