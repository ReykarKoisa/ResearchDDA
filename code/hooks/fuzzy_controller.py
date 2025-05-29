import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

health = ctrl.Antecedent(np.arange(0, 101, 1), "health")

deaths = ctrl.Antecedent(np.arange(0, 11, 1), "deaths")

completion_time = ctrl.Antecedent(np.arange(0, 601, 1), "completion_time")


enemy_damage = ctrl.Consequent(np.arange(0.3, 2.01, 0.01), "enemy_damage")
enemy_health = ctrl.Consequent(np.arange(0.3, 2.01, 0.01), "enemy_health")

health["critical"] = fuzz.trapmf(health.universe, [0, 0, 15, 50])
health["moderate"] = fuzz.trimf(health.universe, [20, 50, 75])
health["optimal"] = fuzz.trapmf(health.universe, [50, 75, 100, 100])


deaths["exceptional"] = fuzz.trapmf(deaths.universe, [0, 0, 1, 2])  
deaths["few"] = fuzz.trimf(deaths.universe, [1, 3, 5])
deaths["moderate"] = fuzz.trimf(deaths.universe, [3, 6, 8])
deaths["many"] = fuzz.trapmf(deaths.universe, [6, 10, 10, 10])


completion_time["exceptional"] = fuzz.trapmf(
    completion_time.universe, [0, 0, 30, 90]
)  
completion_time["fast"] = fuzz.trimf(completion_time.universe, [60, 120, 180])
completion_time["medium"] = fuzz.trimf(completion_time.universe, [150, 300, 450])
completion_time["slow"] = fuzz.trapmf(completion_time.universe, [350, 480, 600, 600])


enemy_damage["major_decrease"] = fuzz.trimf(
    enemy_damage.universe, [0.3, 0.4, 0.55]
)  
enemy_damage["decrease"] = fuzz.trimf(enemy_damage.universe, [0.45, 0.6, 0.75])
enemy_damage["slight_decrease"] = fuzz.trimf(
    enemy_damage.universe, [0.65, 0.8, 0.95]
)
enemy_damage["keep_same"] = fuzz.trimf(enemy_damage.universe, [0.9, 1.0, 1.1])
enemy_damage["slight_increase"] = fuzz.trimf(
    enemy_damage.universe, [1.05, 1.25, 1.4]
)
enemy_damage["increase"] = fuzz.trimf(enemy_damage.universe, [1.3, 1.55, 1.8])
enemy_damage["major_increase"] = fuzz.trimf(
    enemy_damage.universe, [1.7, 1.85, 2.0]
)  

enemy_health["major_decrease"] = fuzz.trimf(
    enemy_health.universe, [0.3, 0.4, 0.55]
)  
enemy_health["decrease"] = fuzz.trimf(enemy_health.universe, [0.45, 0.6, 0.75])
enemy_health["slight_decrease"] = fuzz.trimf(
    enemy_health.universe, [0.65, 0.8, 0.95]
)
enemy_health["keep_same"] = fuzz.trimf(enemy_health.universe, [0.9, 1.0, 1.1])
enemy_health["slight_increase"] = fuzz.trimf(
    enemy_health.universe, [1.05, 1.25, 1.4]
)
enemy_health["increase"] = fuzz.trimf(enemy_health.universe, [1.3, 1.55, 1.8])
enemy_health["major_increase"] = fuzz.trimf(
    enemy_health.universe, [1.7, 1.85, 2.0]
)  


r01_OptH_ExcD_ExcT = ctrl.Rule(
    health["optimal"] & deaths["exceptional"] & completion_time["exceptional"],
    [enemy_damage["major_increase"], enemy_health["major_increase"]],
)
r02_OptH_ExcD_FastT = ctrl.Rule(
    health["optimal"] & deaths["exceptional"] & completion_time["fast"],
    [enemy_damage["increase"], enemy_health["increase"]],
)
r03_OptH_FewD_ExcT = ctrl.Rule(
    health["optimal"] & deaths["few"] & completion_time["exceptional"],
    [enemy_damage["increase"], enemy_health["major_increase"]],
)

r04_OptH_ExcD_MedT = ctrl.Rule(
    health["optimal"] & deaths["exceptional"] & completion_time["medium"],
    [enemy_damage["slight_increase"], enemy_health["increase"]],
)
r05_OptH_ExcD_SlowT = ctrl.Rule(
    health["optimal"] & deaths["exceptional"] & completion_time["slow"],
    [enemy_damage["keep_same"], enemy_health["slight_decrease"]],
)
r06_OptH_FewD_FastT = ctrl.Rule(
    health["optimal"] & deaths["few"] & completion_time["fast"],
    [enemy_damage["increase"], enemy_health["increase"]],
)
r07_OptH_FewD_MedT = ctrl.Rule(
    health["optimal"] & deaths["few"] & completion_time["medium"],
    [enemy_damage["slight_increase"], enemy_health["slight_increase"]],
)
r08_OptH_FewD_SlowT = ctrl.Rule(
    health["optimal"] & deaths["few"] & completion_time["slow"],
    [enemy_damage["slight_decrease"], enemy_health["slight_decrease"]],
)

r09_OptH_ModD_ExcT = ctrl.Rule(
    health["optimal"] & deaths["moderate"] & completion_time["exceptional"],
    [enemy_damage["slight_increase"], enemy_health["increase"]],
)
r10_OptH_ModD_FastT = ctrl.Rule(
    health["optimal"] & deaths["moderate"] & completion_time["fast"],
    [enemy_damage["keep_same"], enemy_health["keep_same"]],
)
r11_OptH_ModD_MedT = ctrl.Rule(
    health["optimal"] & deaths["moderate"] & completion_time["medium"],
    [enemy_damage["keep_same"], enemy_health["keep_same"]],
)
r12_OptH_ModD_SlowT = ctrl.Rule(
    health["optimal"] & deaths["moderate"] & completion_time["slow"],
    [enemy_damage["slight_decrease"], enemy_health["decrease"]],
)
r13_OptH_ManyD_ExcT = ctrl.Rule(
    health["optimal"] & deaths["many"] & completion_time["exceptional"],
    [enemy_damage["keep_same"], enemy_health["increase"]],
)
r14_OptH_ManyD_FastT = ctrl.Rule(
    health["optimal"] & deaths["many"] & completion_time["fast"],
    [enemy_damage["slight_decrease"], enemy_health["slight_decrease"]],
)
r15_OptH_ManyD_MedT = ctrl.Rule(
    health["optimal"] & deaths["many"] & completion_time["medium"],
    [enemy_damage["slight_decrease"], enemy_health["decrease"]],
)
r16_OptH_ManyD_SlowT = ctrl.Rule(
    health["optimal"] & deaths["many"] & completion_time["slow"],
    [enemy_damage["decrease"], enemy_health["decrease"]],
)

r17_ModH_ExcD_ExcT = ctrl.Rule(
    health["moderate"] & deaths["exceptional"] & completion_time["exceptional"],
    [enemy_damage["increase"], enemy_health["increase"]],
)
r18_ModH_ExcD_FastT = ctrl.Rule(
    health["moderate"] & deaths["exceptional"] & completion_time["fast"],
    [enemy_damage["slight_increase"], enemy_health["slight_increase"]],
)
r19_ModH_FewD_ExcT = ctrl.Rule(
    health["moderate"] & deaths["few"] & completion_time["exceptional"],
    [enemy_damage["slight_increase"], enemy_health["increase"]],
)
r20_ModH_ExcD_MedT = ctrl.Rule(
    health["moderate"] & deaths["exceptional"] & completion_time["medium"],
    [enemy_damage["keep_same"], enemy_health["slight_increase"]],
)
r21_ModH_ExcD_SlowT = ctrl.Rule(
    health["moderate"] & deaths["exceptional"] & completion_time["slow"],
    [enemy_damage["slight_decrease"], enemy_health["slight_decrease"]],
)
r22_ModH_FewD_FastT = ctrl.Rule(
    health["moderate"] & deaths["few"] & completion_time["fast"],
    [enemy_damage["keep_same"], enemy_health["keep_same"]],
)
r23_ModH_FewD_MedT = ctrl.Rule(
    health["moderate"] & deaths["few"] & completion_time["medium"],
    [enemy_damage["keep_same"], enemy_health["keep_same"]],
)
r24_ModH_FewD_SlowT = ctrl.Rule(
    health["moderate"] & deaths["few"] & completion_time["slow"],
    [enemy_damage["decrease"], enemy_health["slight_decrease"]],
)
r25_ModH_ModD_ExcT = ctrl.Rule(
    health["moderate"] & deaths["moderate"] & completion_time["exceptional"],
    [enemy_damage["slight_increase"], enemy_health["increase"]],
)
r26_ModH_ModD_FastT = ctrl.Rule(
    health["moderate"] & deaths["moderate"] & completion_time["fast"],
    [enemy_damage["keep_same"], enemy_health["keep_same"]],
)
r27_ModH_ModD_MedT = ctrl.Rule(
    health["moderate"] & deaths["moderate"] & completion_time["medium"],
    [enemy_damage["slight_decrease"], enemy_health["slight_decrease"]],
)
r28_ModH_ModD_SlowT = ctrl.Rule(
    health["moderate"] & deaths["moderate"] & completion_time["slow"],
    [enemy_damage["decrease"], enemy_health["decrease"]],
)
r29_ModH_ManyD_ExcT = ctrl.Rule(
    health["moderate"] & deaths["many"] & completion_time["exceptional"],
    [enemy_damage["decrease"], enemy_health["keep_same"]],
)
r30_ModH_ManyD_FastT = ctrl.Rule(
    health["moderate"] & deaths["many"] & completion_time["fast"],
    [enemy_damage["decrease"], enemy_health["decrease"]],
)
r31_ModH_ManyD_MedT = ctrl.Rule(
    health["moderate"] & deaths["many"] & completion_time["medium"],
    [enemy_damage["decrease"], enemy_health["decrease"]],
)
r32_ModH_ManyD_SlowT = ctrl.Rule(
    health["moderate"] & deaths["many"] & completion_time["slow"],
    [enemy_damage["major_decrease"], enemy_health["decrease"]],
)


r33_CritH_ExcD_ExcT = ctrl.Rule(
    health["critical"] & deaths["exceptional"] & completion_time["exceptional"],
    [enemy_damage["increase"], enemy_health["increase"]],
)
r34_CritH_ExcD_FastT = ctrl.Rule(
    health["critical"] & deaths["exceptional"] & completion_time["fast"],
    [enemy_damage["slight_increase"], enemy_health["slight_increase"]],
)
r35_CritH_FewD_ExcT = ctrl.Rule(
    health["critical"] & deaths["few"] & completion_time["exceptional"],
    [enemy_damage["increase"], enemy_health["increase"]],
)
r36_CritH_ExcD_MedT = ctrl.Rule(
    health["critical"] & deaths["exceptional"] & completion_time["medium"],
    [enemy_damage["slight_increase"], enemy_health["slight_increase"]],
)
r37_CritH_ExcD_SlowT = ctrl.Rule(
    health["critical"] & deaths["exceptional"] & completion_time["slow"],
    [enemy_damage["slight_decrease"], enemy_health["decrease"]],
)
r38_CritH_FewD_FastT = ctrl.Rule(
    health["critical"] & deaths["few"] & completion_time["fast"],
    [enemy_damage["keep_same"], enemy_health["slight_decrease"]],
)
r39_CritH_FewD_MedT = ctrl.Rule(
    health["critical"] & deaths["few"] & completion_time["medium"],
    [enemy_damage["slight_decrease"], enemy_health["decrease"]],
)
r40_CritH_FewD_SlowT = ctrl.Rule(
    health["critical"] & deaths["few"] & completion_time["slow"],
    [enemy_damage["decrease"], enemy_health["major_decrease"]],
)
r41_CritH_ModD_ExcT = ctrl.Rule(
    health["critical"] & deaths["moderate"] & completion_time["exceptional"],
    [enemy_damage["keep_same"], enemy_health["increase"]],
)
r42_CritH_ModD_FastT = ctrl.Rule(
    health["critical"] & deaths["moderate"] & completion_time["fast"],
    [enemy_damage["decrease"], enemy_health["slight_decrease"]],
)
r43_CritH_ModD_MedT = ctrl.Rule(
    health["critical"] & deaths["moderate"] & completion_time["medium"],
    [enemy_damage["major_decrease"], enemy_health["major_decrease"]],
)
r44_CritH_ModD_SlowT = ctrl.Rule(
    health["critical"] & deaths["moderate"] & completion_time["slow"],
    [enemy_damage["major_decrease"], enemy_health["major_decrease"]],
)
r45_CritH_ManyD_ExcT = ctrl.Rule(
    health["critical"] & deaths["many"] & completion_time["exceptional"],
    [enemy_damage["decrease"], enemy_health["keep_same"]],
)
r46_CritH_ManyD_FastT = ctrl.Rule(
    health["critical"] & deaths["many"] & completion_time["fast"],
    [enemy_damage["decrease"], enemy_health["decrease"]],
)
r47_CritH_ManyD_MedT = ctrl.Rule(
    health["critical"] & deaths["many"] & completion_time["medium"],
    [enemy_damage["major_decrease"], enemy_health["decrease"]],
)
r48_CritH_ManyD_SlowT = ctrl.Rule(
    health["critical"] & deaths["many"] & completion_time["slow"],
    [enemy_damage["major_decrease"], enemy_health["major_decrease"]],
)


difficulty_ctrl = ctrl.ControlSystem(
    [
        r01_OptH_ExcD_ExcT,
        r02_OptH_ExcD_FastT,
        r03_OptH_FewD_ExcT,
        r04_OptH_ExcD_MedT,
        r05_OptH_ExcD_SlowT,
        r06_OptH_FewD_FastT,
        r07_OptH_FewD_MedT,
        r08_OptH_FewD_SlowT,
        r09_OptH_ModD_ExcT,
        r10_OptH_ModD_FastT,
        r11_OptH_ModD_MedT,
        r12_OptH_ModD_SlowT,
        r13_OptH_ManyD_ExcT,
        r14_OptH_ManyD_FastT,
        r15_OptH_ManyD_MedT,
        r16_OptH_ManyD_SlowT,
        r17_ModH_ExcD_ExcT,
        r18_ModH_ExcD_FastT,
        r19_ModH_FewD_ExcT,
        r20_ModH_ExcD_MedT,
        r21_ModH_ExcD_SlowT,
        r22_ModH_FewD_FastT,
        r23_ModH_FewD_MedT,
        r24_ModH_FewD_SlowT,
        r25_ModH_ModD_ExcT,
        r26_ModH_ModD_FastT,
        r27_ModH_ModD_MedT,
        r28_ModH_ModD_SlowT,
        r29_ModH_ManyD_ExcT,
        r30_ModH_ManyD_FastT,
        r31_ModH_ManyD_MedT,
        r32_ModH_ManyD_SlowT,
        r33_CritH_ExcD_ExcT,
        r34_CritH_ExcD_FastT,
        r35_CritH_FewD_ExcT,
        r36_CritH_ExcD_MedT,
        r37_CritH_ExcD_SlowT,
        r38_CritH_FewD_FastT,
        r39_CritH_FewD_MedT,
        r40_CritH_FewD_SlowT,
        r41_CritH_ModD_ExcT,
        r42_CritH_ModD_FastT,
        r43_CritH_ModD_MedT,
        r44_CritH_ModD_SlowT,
        r45_CritH_ManyD_ExcT,
        r46_CritH_ManyD_FastT,
        r47_CritH_ManyD_MedT,
        r48_CritH_ManyD_SlowT,
    ]
)


def check_DDA_adjust_difficulty(player_health, player_deaths, level_time_sec):
    """
    Calculate adjustment multipliers for enemy damage and health based on player's level performance.
    Enhanced version with stronger responses to exceptional performance.

    Parameters:
      - player_health (float): Player's health at end of level (0-100).
      - player_deaths (int): Number of deaths in the level (0-10).
      - level_time_sec (float): Level completion time in seconds (e.g., 0-600).

    Returns:
      - tuple (float, float): (enemy_damage_multiplier, enemy_health_multiplier)
    """
    damage_output = 1.0  
    health_output = 1.0  

    # --- START DIAGNOSTIC PRINTS ---
    print(f"\n--- Enhanced Fuzzy Calculation Start ---")
    print(
        f"Received Inputs: Health={player_health}, Deaths={player_deaths}, Time={level_time_sec}"
    )

    clipped_health = np.clip(player_health, 0, 100)
    clipped_deaths = np.clip(player_deaths, 0, 10)
    clipped_time = np.clip(level_time_sec, 0, 600)
    print(
        f"Clipped Inputs: Health={clipped_health}, Deaths={clipped_deaths}, Time={clipped_time}"
    )
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
        raw_damage_val = difficulty_sim.output.get("enemy_damage")
        raw_health_val = difficulty_sim.output.get("enemy_health")

        if raw_damage_val is not None:
            damage_output = raw_damage_val
            print(f"Raw 'enemy_damage' from output: {damage_output}")
        else:
            print(
                f"Warning: 'enemy_damage' key not found in fuzzy output. Defaulting to 1.0."
            )
            damage_output = 1.0

        if raw_health_val is not None:
            health_output = raw_health_val
            print(f"Raw 'enemy_health' from output: {health_output}")
        else:
            print(
                f"Warning: 'enemy_health' key not found in fuzzy output. Defaulting to 1.0."
            )
            health_output = 1.0

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

        
        damage_output = max(0.1, damage_output)  
        health_output = max(0.1, health_output)  

    except KeyError as e:
        print(
            f"Warning: Could not compute output due to KeyError: {e}. Rules might not cover this input combination or output variable name mismatch."
        )
        print(
            f"Inputs were: health={clipped_health}, deaths={clipped_deaths}, time={clipped_time}"
        )
        
    except Exception as e:
        print(f"An unexpected error occurred during fuzzy computation: {e}")
       

    # --- START DIAGNOSTIC PRINTS ---
    print(
        f"Final Multipliers Returned: DamageMult={damage_output:.2f}, HealthMult={health_output:.2f}"
    )
    print(f"--- Enhanced Fuzzy Calculation End ---\n")
    # --- END DIAGNOSTIC PRINTS ---

    return damage_output, health_output

def check_DDA_adjust_difficulty_capped(player_health, player_deaths, level_time_sec,level_number, max_increase=0.25):
    """
    Wrapper that caps the maximum increase from baseline to prevent early spikes.
    """
    damage_mult, health_mult = check_DDA_adjust_difficulty(player_health, player_deaths, level_time_sec)
    
    if level_number < 1:
        if damage_mult > 1.0:
            damage_mult = min(damage_mult, 1.0 + max_increase)
        if health_mult > 1.0:
            health_mult = min(health_mult, 1.0 + max_increase)
    
    return damage_mult, health_mult




# --- Example Usage ---
if __name__ == "__main__":

    def run_test(test_name, health_val, deaths_val, time_val):
        print(f"--- {test_name} ---")
        damage_mult, health_mult = check_DDA_adjust_difficulty(
            health_val, deaths_val, time_val
        )

    print(
        "=== TESTING ENHANCED DYNAMIC DIFFICULTY ADJUSTMENT (Strengthened Fast/Few Rules) ===\n"
    )

    # Test exceptional performance scenarios
    print("=== EXCEPTIONAL PERFORMANCE TESTS ===")
    run_test("EXCEPTIONAL: Optimal Health, 0 Deaths, 15s Time", 100, 0, 15)
    run_test("EXCEPTIONAL: Optimal Health, 1 Death, 25s Time", 95, 1, 25)
    run_test("EXCEPTIONAL: Moderate Health, 0 Deaths, 20s Time", 70, 0, 20)

    print("\n=== HIGH PERFORMANCE TESTS ===")
    run_test("HIGH: Optimal Health, 2 Deaths, 60s Time", 90, 2, 60)
    run_test("HIGH: Optimal Health, 1 Death, 120s Time", 85, 1, 120)

    print("\n=== COMPARISON WITH ORIGINAL SCENARIOS ===")
    run_test("ORIGINAL: Optimal Health, Few Deaths, Fast Time", 100, 1, 60)
    run_test("ORIGINAL: Optimal Health, Few Deaths, Medium Time", 90, 2, 180)

    print("\n=== STRUGGLING PLAYER TESTS ===")
    run_test("STRUGGLING: Critical Health, Many Deaths, Slow Time", 10, 9, 500)
    run_test("STRUGGLING: Critical Health, Moderate Deaths, Medium Time", 20, 6, 300)

    print("\n=== EDGE CASE TESTS ===")
    run_test("EDGE: Perfect Performance", 100, 0, 5)
    run_test("EDGE: Worst Performance", 0, 10, 600)