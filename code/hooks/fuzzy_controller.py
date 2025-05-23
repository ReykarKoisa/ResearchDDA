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
#enemy_damage = ctrl.Consequent(np.arange(0.3, 1.81, 0.01), "enemy_damage")
#enemy_health = ctrl.Consequent(np.arange(0.3, 1.81, 0.01), "enemy_health")
enemy_damage = ctrl.Consequent(np.arange(0.3, 1.81, 0.01), "enemy_damage")
enemy_health = ctrl.Consequent(np.arange(0.3, 1.81, 0.01), "enemy_health")

# --- Membership Functions for Inputs ---
# Health: Lower is worse, higher is better.
health["critical"] = fuzz.trapmf(health.universe, [0, 0, 25, 60])
health["moderate"] = fuzz.trimf(health.universe, [30, 60, 85])
health["optimal"] = fuzz.trapmf(health.universe, [60, 85, 100, 100])

# Deaths: Lower is better, higher is worse.
deaths["few"] = fuzz.trapmf(deaths.universe, [0, 0, 1, 5])
deaths["moderate"] = fuzz.trimf(deaths.universe, [1, 5, 8])
deaths["many"] = fuzz.trapmf(deaths.universe, [5, 10, 10, 10])

# Completion Time: Lower (faster) is generally better.
completion_time["fast"] = fuzz.trapmf(completion_time.universe, [0, 0, 45, 150])
completion_time["medium"] = fuzz.trimf(completion_time.universe, [120, 300, 450])
completion_time["slow"] = fuzz.trapmf(completion_time.universe, [300, 480, 600, 600])

# --- Membership Functions for Outputs ---
# Enemy Damage Adjustment:
enemy_damage["decrease"] = fuzz.trimf(enemy_damage.universe, [0.3, 0.5, 0.75])
enemy_damage["slight_decrease"] = fuzz.trimf(enemy_damage.universe, [0.65, 0.8, 0.95])
enemy_damage["keep_same"] = fuzz.trimf(enemy_damage.universe, [0.9, 1.0, 1.1])
enemy_damage["slight_increase"] = fuzz.trimf(enemy_damage.universe, [1.05, 1.25, 1.4])
enemy_damage["increase"] = fuzz.trimf(enemy_damage.universe, [1.3, 1.55, 1.8])

# Enemy Health Adjustment:
enemy_health["decrease"] = fuzz.trimf(enemy_health.universe, [0.3, 0.5, 0.75])
enemy_health["slight_decrease"] = fuzz.trimf(enemy_health.universe, [0.65, 0.8, 0.95])
enemy_health["keep_same"] = fuzz.trimf(enemy_health.universe, [0.9, 1.0, 1.1])
enemy_health["slight_increase"] = fuzz.trimf(enemy_health.universe, [1.05, 1.25, 1.4])
enemy_health["increase"] = fuzz.trimf(enemy_health.universe, [1.3, 1.55, 1.8])

# --- Fuzzy Rules (All 3-variable) ---
# Category I: Player Health is Optimal
# I.A: Optimal Health, Few Deaths
r01_OptH_FewD_FastT = ctrl.Rule(health['optimal'] & deaths['few'] & completion_time['fast'],
                               [enemy_damage['increase'], enemy_health['increase']])
r02_OptH_FewD_MedT = ctrl.Rule(health['optimal'] & deaths['few'] & completion_time['medium'],
                              [enemy_damage['slight_increase'], enemy_health['slight_increase']])
r03_OptH_FewD_SlowT = ctrl.Rule(health['optimal'] & deaths['few'] & completion_time['slow'],
                               [enemy_damage['keep_same'], enemy_health['slight_increase']])
# I.B: Optimal Health, Moderate Deaths
r04_OptH_ModD_FastT = ctrl.Rule(health['optimal'] & deaths['moderate'] & completion_time['fast'],
                               [enemy_damage['slight_increase'], enemy_health['keep_same']])
r05_OptH_ModD_MedT = ctrl.Rule(health['optimal'] & deaths['moderate'] & completion_time['medium'],
                              [enemy_damage['keep_same'], enemy_health['keep_same']])
r06_OptH_ModD_SlowT = ctrl.Rule(health['optimal'] & deaths['moderate'] & completion_time['slow'],
                               [enemy_damage['slight_decrease'], enemy_health['keep_same']])
# I.C: Optimal Health, Many Deaths
r07_OptH_ManyD_FastT = ctrl.Rule(health['optimal'] & deaths['many'] & completion_time['fast'],
                                [enemy_damage['keep_same'], enemy_health['slight_decrease']])
r08_OptH_ManyD_MedT = ctrl.Rule(health['optimal'] & deaths['many'] & completion_time['medium'],
                               [enemy_damage['slight_decrease'], enemy_health['slight_decrease']])
r09_OptH_ManyD_SlowT = ctrl.Rule(health['optimal'] & deaths['many'] & completion_time['slow'],
                                [enemy_damage['decrease'], enemy_health['decrease']])

# Category II: Player Health is Moderate
# II.A: Moderate Health, Few Deaths
r10_ModH_FewD_FastT = ctrl.Rule(health['moderate'] & deaths['few'] & completion_time['fast'],
                               [enemy_damage['slight_increase'], enemy_health['slight_increase']])
r11_ModH_FewD_MedT = ctrl.Rule(health['moderate'] & deaths['few'] & completion_time['medium'],
                               [enemy_damage['keep_same'], enemy_health['slight_increase']])
r12_ModH_FewD_SlowT = ctrl.Rule(health['moderate'] & deaths['few'] & completion_time['slow'],
                               [enemy_damage['slight_decrease'], enemy_health['keep_same']])
# II.B: Moderate Health, Moderate Deaths
r13_ModH_ModD_FastT = ctrl.Rule(health['moderate'] & deaths['moderate'] & completion_time['fast'],
                               [enemy_damage['keep_same'], enemy_health['keep_same']])
r14_ModH_ModD_MedT = ctrl.Rule(health['moderate'] & deaths['moderate'] & completion_time['medium'],
                               [enemy_damage['keep_same'], enemy_health['keep_same']])
r15_ModH_ModD_SlowT = ctrl.Rule(health['moderate'] & deaths['moderate'] & completion_time['slow'],
                               [enemy_damage['slight_decrease'], enemy_health['slight_decrease']])
# II.C: Moderate Health, Many Deaths
r16_ModH_ManyD_FastT = ctrl.Rule(health['moderate'] & deaths['many'] & completion_time['fast'],
                                [enemy_damage['slight_decrease'], enemy_health['decrease']])
r17_ModH_ManyD_MedT = ctrl.Rule(health['moderate'] & deaths['many'] & completion_time['medium'],
                                [enemy_damage['decrease'], enemy_health['decrease']])
r18_ModH_ManyD_SlowT = ctrl.Rule(health['moderate'] & deaths['many'] & completion_time['slow'],
                                [enemy_damage['decrease'], enemy_health['decrease']])

# Category III: Player Health is Critical
# III.A: Critical Health, Few Deaths
r19_CritH_FewD_FastT = ctrl.Rule(health['critical'] & deaths['few'] & completion_time['fast'],
                                [enemy_damage['decrease'], enemy_health['slight_decrease']])
r20_CritH_FewD_MedT = ctrl.Rule(health['critical'] & deaths['few'] & completion_time['medium'],
                               [enemy_damage['decrease'], enemy_health['decrease']])
r21_CritH_FewD_SlowT = ctrl.Rule(health['critical'] & deaths['few'] & completion_time['slow'],
                                [enemy_damage['decrease'], enemy_health['decrease']])
# III.B: Critical Health, Moderate Deaths
r22_CritH_ModD_FastT = ctrl.Rule(health['critical'] & deaths['moderate'] & completion_time['fast'],
                                [enemy_damage['decrease'], enemy_health['decrease']])
r23_CritH_ModD_MedT = ctrl.Rule(health['critical'] & deaths['moderate'] & completion_time['medium'],
                                [enemy_damage['decrease'], enemy_health['decrease']])
r24_CritH_ModD_SlowT = ctrl.Rule(health['critical'] & deaths['moderate'] & completion_time['slow'],
                                [enemy_damage['decrease'], enemy_health['decrease']])
# III.C: Critical Health, Many Deaths
r25_CritH_ManyD_FastT = ctrl.Rule(health['critical'] & deaths['many'] & completion_time['fast'],
                                [enemy_damage['decrease'], enemy_health['decrease']])
r26_CritH_ManyD_MedT = ctrl.Rule(health['critical'] & deaths['many'] & completion_time['medium'],
                                [enemy_damage['decrease'], enemy_health['decrease']])
r27_CritH_ManyD_SlowT = ctrl.Rule(health['critical'] & deaths['many'] & completion_time['slow'],
                                [enemy_damage['decrease'], enemy_health['decrease']])

# --- Control System Creation ---
# Ensure all new 27 rules are included in the control system
difficulty_ctrl = ctrl.ControlSystem(
    [
        r01_OptH_FewD_FastT, r02_OptH_FewD_MedT, r03_OptH_FewD_SlowT,
        r04_OptH_ModD_FastT, r05_OptH_ModD_MedT, r06_OptH_ModD_SlowT,
        r07_OptH_ManyD_FastT, r08_OptH_ManyD_MedT, r09_OptH_ManyD_SlowT,
        r10_ModH_FewD_FastT, r11_ModH_FewD_MedT, r12_ModH_FewD_SlowT,
        r13_ModH_ModD_FastT, r14_ModH_ModD_MedT, r15_ModH_ModD_SlowT,
        r16_ModH_ManyD_FastT, r17_ModH_ManyD_MedT, r18_ModH_ManyD_SlowT,
        r19_CritH_FewD_FastT, r20_CritH_FewD_MedT, r21_CritH_FewD_SlowT,
        r22_CritH_ModD_FastT, r23_CritH_ModD_MedT, r24_CritH_ModD_SlowT,
        r25_CritH_ManyD_FastT, r26_CritH_ManyD_MedT, r27_CritH_ManyD_SlowT,
    ]
)

def check_DDA_adjust_difficulty(player_health, player_deaths, level_time_sec):
    """
    Calculate adjustment multipliers for enemy damage and health based on player's level performance.
    All rules now consider health, deaths, and completion_time.

    Parameters:
      - player_health (float): Player's health at end of level (0-100).
      - player_deaths (int): Number of deaths in the level (0-10).
      - level_time_sec (float): Level completion time in seconds (e.g., 0-600).

    Returns:
      - tuple (float, float): (enemy_damage_multiplier, enemy_health_multiplier)
    """
    damage_output = 1.0  # Default to 1.0
    health_output = 1.0  # Default to 1.0

    # --- START DIAGNOSTIC PRINTS ---
    print(f"\n--- Fuzzy Calculation Start ---")
    print(f"Received Inputs: Health={player_health}, Deaths={player_deaths}, Time={level_time_sec}")

    clipped_health = np.clip(player_health, 0, 100)
    clipped_deaths = np.clip(player_deaths, 0, 10)
    clipped_time = np.clip(level_time_sec, 0, 600)
    print(f"Clipped Inputs: Health={clipped_health}, Deaths={clipped_deaths}, Time={clipped_time}")
    # --- END DIAGNOSTIC PRINTS ---

    try:
        difficulty_sim = ctrl.ControlSystemSimulation(difficulty_ctrl)
        difficulty_sim.input["health"] = clipped_health
        difficulty_sim.input["deaths"] = clipped_deaths
        difficulty_sim.input["completion_time"] = clipped_time

        difficulty_sim.compute()

        # --- START DIAGNOSTIC PRINTS ---
        print(f"Raw difficulty_sim.output dictionary: {difficulty_sim.output}")
        # --- END DIAGNOSTIC PRINTS ---

        # Retrieve with default, and then check if the key was actually present
        # This helps differentiate between a computed 1.0 and a default 1.0
        raw_damage_val = difficulty_sim.output.get("enemy_damage")
        raw_health_val = difficulty_sim.output.get("enemy_health")

        if raw_damage_val is not None:
            damage_output = raw_damage_val
            print(f"Raw 'enemy_damage' from output: {damage_output}")
        else:
            print(f"Warning: 'enemy_damage' key not found in fuzzy output. Defaulting to 1.0.")
            damage_output = 1.0
        
        if raw_health_val is not None:
            health_output = raw_health_val
            print(f"Raw 'enemy_health' from output: {health_output}")
        else:
            print(f"Warning: 'enemy_health' key not found in fuzzy output. Defaulting to 1.0.")
            health_output = 1.0


        if not np.isfinite(damage_output):
            print(f"Warning: Computed damage output is not finite ({damage_output}). Defaulting to 1.0.")
            damage_output = 1.0
        if not np.isfinite(health_output):
            print(f"Warning: Computed health output is not finite ({health_output}). Defaulting to 1.0.")
            health_output = 1.0
        
        # Ensure multipliers are not zero or negative, which could break game logic
        damage_output = max(0.1, damage_output) # Minimum multiplier of 0.1
        health_output = max(0.1, health_output) # Minimum multiplier of 0.1


    except KeyError as e:
        print(f"Warning: Could not compute output due to KeyError: {e}. Rules might not cover this input combination or output variable name mismatch.")
        print(f"Inputs were: health={clipped_health}, deaths={clipped_deaths}, time={clipped_time}")
        # Keep default 1.0, 1.0
    except Exception as e:
        print(f"An unexpected error occurred during fuzzy computation: {e}")
        # Keep default 1.0, 1.0
    
    # --- START DIAGNOSTIC PRINTS ---
    print(f"Final Multipliers Returned: DamageMult={damage_output:.2f}, HealthMult={health_output:.2f}")
    print(f"--- Fuzzy Calculation End ---\n")
    # --- END DIAGNOSTIC PRINTS ---

    return damage_output, health_output

# --- Example Usage ---
if __name__ == "__main__":
    def run_test(test_name, health_val, deaths_val, time_val):
        print(f"--- {test_name} ---")
        damage_mult, health_mult = check_DDA_adjust_difficulty(
            health_val, deaths_val, time_val
        )
        # The function now prints its own detailed logs, so we just call it.
        # print(f"Inputs: Health={health_val}, Deaths={deaths_val}, Time={time_val}s")
        # print(f"Output: Enemy Damage Multiplier: {damage_mult:.2f}")
        # print(f"Output: Enemy Health Multiplier: {health_mult:.2f}\n")

    print("=== TESTING DYNAMIC DIFFICULTY ADJUSTMENT (3-Variable Rules) ===\n")

    # Test cases focusing on combinations of all three variables

    # Optimal Health Scenarios
    run_test("Optimal Health, Few Deaths, Fast Time", 100, 1, 60)
    run_test("Optimal Health, Few Deaths, Medium Time", 90, 2, 180)
    run_test("Optimal Health, Few Deaths, Slow Time", 80, 3, 350)

    run_test("Optimal Health, Moderate Deaths, Fast Time", 100, 5, 80)
    run_test("Optimal Health, Moderate Deaths, Medium Time", 90, 6, 200)
    run_test("Optimal Health, Moderate Deaths, Slow Time", 80, 7, 400)

    run_test("Optimal Health, Many Deaths, Fast Time", 100, 9, 100)
    run_test("Optimal Health, Many Deaths, Medium Time", 90, 8, 300)
    run_test("Optimal Health, Many Deaths, Slow Time", 80, 10, 500)

    # Moderate Health Scenarios
    run_test("Moderate Health, Few Deaths, Fast Time", 70, 1, 70)
    run_test("Moderate Health, Few Deaths, Medium Time", 60, 2, 190)
    run_test("Moderate Health, Few Deaths, Slow Time", 50, 3, 360)

    run_test("Moderate Health, Moderate Deaths, Fast Time", 70, 5, 85)
    run_test("Moderate Health, Moderate Deaths, Medium Time", 60, 6, 250)
    run_test("Moderate Health, Moderate Deaths, Slow Time", 50, 7, 420)

    run_test("Moderate Health, Many Deaths, Fast Time", 70, 9, 110)
    run_test("Moderate Health, Many Deaths, Medium Time", 60, 8, 330)
    run_test("Moderate Health, Many Deaths, Slow Time", 50, 10, 550)

    # Critical Health Scenarios (e.g., player died, health input is 0)
    run_test("Critical Health (Death), Few Deaths, Fast Time", 0, 1, 50)
    run_test("Critical Health (Death), Few Deaths, Medium Time", 0, 2, 170)
    run_test("Critical Health (Death), Few Deaths, Slow Time", 0, 3, 320)

    run_test("Critical Health (Death), Moderate Deaths, Fast Time", 0, 5, 70)
    run_test("Critical Health (Death), Moderate Deaths, Medium Time", 0, 6, 220)
    run_test("Critical Health (Death), Moderate Deaths, Slow Time", 0, 7, 400)

    run_test("Critical Health (Death), Many Deaths, Fast Time", 0, 9, 90)
    run_test("Critical Health (Death), Many Deaths, Medium Time", 0, 8, 280)
    run_test("Critical Health (Death), Many Deaths, Slow Time", 0, 10, 500)

    # Test with very low time, which previously might have caused issues
    run_test("Optimal Health, Few Deaths, Very Fast Time", 80, 0, 1.5)
    run_test("Moderate Health, Few Deaths, Very Fast Time", 70, 0, 5)
    run_test("Critical Health, Few Deaths, Very Fast Time", 20, 0, 10)
