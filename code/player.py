from itertools import cycle
from camera import Camera
from settings import *
import hooks.fuzzy_controller as fuzzy_controller
from hook_objects import level_duration, total_duration, game_logger, runtime_game_stats
import random
import sys
import pygame as pg
from typing import Tuple


class PlayerAttribs:
    def __init__(self):
        self.health = PLAYER_INIT_HEALTH
        self.ammo = PLAYER_INIT_AMMO
        self.weapons = {ID.KNIFE_0: 1, ID.PISTOL_0: 0, ID.RIFLE_0: 0}
        self.weapon_id = ID.KNIFE_0
        self.num_level = 0
        self.damage_mult = 1.0
        self.health_mult = 1.0

    def update(self, player):
        self.health = player.health
        self.ammo = player.ammo
        self.weapons = player.weapons
        self.weapon_id = player.weapon_id


class Player(Camera):
    def __init__(self, eng, position=PLAYER_POS, yaw=0, pitch=0):
        self.app = eng.app
        self.eng = eng
        self.sound = eng.sound
        self.play = eng.sound.play
        super().__init__(position, yaw, pitch)

        # these maps will update when instantiated LevelMap
        self.door_map, self.wall_map, self.item_map = None, None, None

        # DDA multipliers
        self.damage_mult = self.eng.player_attribs.damage_mult
        self.health_mult = self.eng.player_attribs.health_mult

        # attribs
        self.health = self.eng.player_attribs.health
        self.ammo = self.eng.player_attribs.ammo
        #
        self.tile_pos: Tuple[int, int] = None

        # weapon
        self.weapons = self.eng.player_attribs.weapons
        self.weapon_id = self.eng.player_attribs.weapon_id
        self.weapon_cycle = cycle(self.eng.player_attribs.weapons.keys())
        #
        self.is_shot = False
        #
        self.key = None

    def handle_events(self, event):
        if event.type == pg.KEYDOWN:
            # door interaction
            if event.key == KEYS["INTERACT"]:
                self.interact_with_door()

            # switch weapon by keys
            if event.key == KEYS["WEAPON_1"]:
                self.switch_weapon(weapon_id=ID.KNIFE_0)
            elif event.key == KEYS["WEAPON_2"]:
                self.switch_weapon(weapon_id=ID.PISTOL_0)
            elif event.key == KEYS["WEAPON_3"]:
                self.switch_weapon(weapon_id=ID.RIFLE_0)

        # weapon by mouse wheel
        if event.type == pg.MOUSEWHEEL:
            weapon_id = next(self.weapon_cycle)
            if self.weapons[weapon_id]:
                self.switch_weapon(weapon_id=weapon_id)

        # shooting
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.do_shot()

    def update(self):
        self.mouse_control()
        self.keyboard_control()
        super().update()
        #
        self.check_health()
        self.update_tile_position()
        self.pick_up_item()

    def check_health(self):
        if self.health <= 0:
            self.play(self.sound.player_death)
            runtime_game_stats.increment_death()
            runtime_game_stats.set_health(
                0
            )  # Health at the moment of death for DDA calculation

            # Log with the multipliers that were active for THE LIFE THAT JUST ENDED
            game_logger.log_death(
                runtime_game_stats.get_health(),  # This will be 0
                runtime_game_stats.get_deaths(),
                total_duration.get_duration(),
                self.damage_mult,  # Multiplier active during the life that ended
                self.health_mult,  # Multiplier active during the life that ended
            )

            # Calculate new DDA multipliers based on this death's performance
            new_damage_mult, new_health_mult = (
                fuzzy_controller.check_DDA_adjust_difficulty_capped(
                    runtime_game_stats.get_health(),  # Health is 0
                    runtime_game_stats.get_deaths(),  # Current accumulated deaths for this level/session
                    total_duration.get_duration(),  # Time taken for this session
                    self.eng.player_attribs.num_level
                )
            ) if DDA_ON else (1.0, 1.0)

            pg.time.wait(2000)

            # Update the *existing* (persistent) player_attribs in the engine
            # These will be used by the new Player instance created in new_game()
            self.eng.player_attribs.health = (
                PLAYER_INIT_HEALTH  # Reset health for the next life
            )
            self.eng.player_attribs.ammo = (
                PLAYER_INIT_AMMO  # Reset ammo for the next life
            )
            # Note: weapons, num_level are not reset by creating a new PlayerAttribs() anymore.
            # They persist or are handled by level completion logic.

            self.eng.player_attribs.damage_mult = (
                new_damage_mult  # Store the NEWLY calculated multiplier
            )
            self.eng.player_attribs.health_mult = (
                new_health_mult  # Store the NEWLY calculated multiplier
            )

            # Reset runtime_game_stats for the next attempt if DDA considers per-life stats
            # or let them accumulate if DDA considers stats over multiple lives in a level.
            # For simplicity, we assume runtime_game_stats.deaths might accumulate until level complete.
            # runtime_game_stats.time is reset by level_duration.start() in new_game or level_complete

            self.eng.new_game()  # This will create a new Player instance which now reads
            # the updated multipliers from self.eng.player_attribs

    def check_hit_on_npc(self):
        if WEAPON_SETTINGS[self.weapon_id]["miss_probability"] > random.random():
            return None

        if npc_pos := self.eng.ray_casting.run(
            start_pos=self.position,
            direction=self.forward,
            max_dist=WEAPON_SETTINGS[self.weapon_id]["max_dist"],
            npc_to_player_flag=False,
        ):
            npc = self.eng.level_map.npc_map[npc_pos]
            npc.get_damage()

    def switch_weapon(self, weapon_id):
        if self.weapons[weapon_id]:
            self.weapon_instance.weapon_id = self.weapon_id = weapon_id

    def do_shot(self):
        if self.weapon_id == ID.KNIFE_0:
            self.is_shot = True
            self.check_hit_on_npc()
            #
            self.play(self.sound.player_attack[ID.KNIFE_0])

        elif self.ammo:
            consumption = WEAPON_SETTINGS[self.weapon_id]["ammo_consumption"]
            if not self.is_shot and self.ammo >= consumption:
                self.is_shot = True
                self.check_hit_on_npc()
                #
                self.ammo -= consumption
                self.ammo = max(0, self.ammo)
                #
                self.play(self.sound.player_attack[self.weapon_id])

    def update_tile_position(self):
        self.tile_pos = int(self.position.x), int(self.position.z)

    def pick_up_item(self):
        if self.tile_pos not in self.item_map:
            return None

        item = self.item_map[self.tile_pos]
        #
        if item.tex_id == ID.MED_KIT:
            self.health += ITEM_SETTINGS[ID.MED_KIT]["value"]
            self.health = min(self.health, MAX_HEALTH_VALUE)
        #
        elif item.tex_id == ID.AMMO:
            self.ammo += ITEM_SETTINGS[ID.AMMO]["value"]
            self.ammo = min(self.ammo, MAX_AMMO_VALUE)
        #
        elif item.tex_id == ID.PISTOL_ICON:
            if not self.weapons[ID.PISTOL_0]:
                self.weapons[ID.PISTOL_0] = 1
                self.switch_weapon(weapon_id=ID.PISTOL_0)
        #
        elif item.tex_id == ID.RIFLE_ICON:
            if not self.weapons[ID.RIFLE_0]:
                self.weapons[ID.RIFLE_0] = 1
                self.switch_weapon(weapon_id=ID.RIFLE_0)
        #
        elif item.tex_id == ID.KEY:
            self.key = 1
        #
        self.play(self.sound.pick_up[item.tex_id])
        #
        del self.item_map[self.tile_pos]

    def interact_with_door(self):
        pos = self.position + self.forward
        int_pos = int(pos.x), int(pos.z)

        if int_pos not in self.door_map:
            return None

        door = self.door_map[int_pos]
        
        if self.key and door.tex_id == ID.KEY_DOOR:
            #
            door.is_closed = not door.is_closed
            self.play(self.sound.player_missed)
            # next level
            level_duration.stop()
            pg.time.wait(300)

            runtime_game_stats.set_health(self.health)  # Health at level end

            # Log level completion with multipliers active during this level
            game_logger.log_level_complete(
                runtime_game_stats.get_health(),
                runtime_game_stats.get_deaths(),  # Deaths accumulated in this level
                total_duration.get_duration(),
                self.damage_mult,  # Multipliers active for this level
                self.health_mult,
            )
            # level_duration.start() # This will be handled by new_game() implicitly if it's there or needs explicit call

            # Calculate DDA multipliers for the NEXT level
            new_damage_mult, new_health_mult = (
                fuzzy_controller.check_DDA_adjust_difficulty_capped(
                    runtime_game_stats.get_health(),
                    runtime_game_stats.get_deaths(),
                    total_duration.get_duration(),
                    self.eng.player_attribs.num_level
                )
            ) if DDA_ON else (1.0, 1.0)

            # Update player_attribs that will carry over to the new Player instance in new_game()
            self.eng.player_attribs.update(
                player=self
            )  # Saves current health, ammo, weapons, AND existing mults
            self.eng.player_attribs.damage_mult = (
                new_damage_mult  # Overwrite with NEW mults for next level
            )
            self.eng.player_attribs.health_mult = (
                new_health_mult  # Overwrite with NEW mults for next level
            )

            self.eng.player_attribs.num_level += 1  # Increment to signify completion of current level / moving to next

            # Check if the incremented level count means all levels are done
            if self.eng.player_attribs.num_level == NUM_LEVELS:
                # All levels completed
                print("All levels completed! Exiting game.")
                total_duration.stop()
                level_duration.stop()  # Ensure this is also stopped
                game_logger.log_total_duration(total_duration.get_duration())
                pg.quit()
                sys.exit()
            else:
                # Not the last level, continue to the next level
                # Apply modulo for standard level looping if not exiting
                # This ensures num_level wraps around correctly for the next level.
                self.eng.player_attribs.num_level %= NUM_LEVELS
                self.eng.new_game()
                level_duration.start()
        else:

            runtime_game_stats.set_health(self.health)

            new_damage_mult, new_health_mult = (
                fuzzy_controller.check_DDA_adjust_difficulty_capped(
                    runtime_game_stats.get_health(),
                    runtime_game_stats.get_deaths(),
                    total_duration.get_duration(),
                    self.eng.player_attribs.num_level
                )
            ) if DDA_ON else (1.0, 1.0)

            game_logger.log_open_door(
                runtime_game_stats.get_health(),
                runtime_game_stats.get_deaths(),  # Deaths accumulated in this level
                total_duration.get_duration(),
                new_damage_mult,  # Multipliers active for this level
                new_health_mult,
            )

            # Update player_attribs that will carry over to the new Player instance in new_game()
            self.eng.player_attribs.update(
                player=self
            )  # Saves current health, ammo, weapons, AND existing mults
            self.eng.player_attribs.damage_mult = (
                new_damage_mult  # Overwrite with NEW mults for next level
            )
            self.eng.player_attribs.health_mult = (
                new_health_mult  # Overwrite with NEW mults for next level
            )

            self.damage_mult = new_damage_mult
            self.health_mult = new_health_mult

            door.is_moving = True
            self.play(self.sound.open_door)

    def mouse_control(self):
        mouse_dx, mouse_dy = pg.mouse.get_rel()
        if mouse_dx:
            self.rotate_yaw(delta_x=mouse_dx * MOUSE_SENSITIVITY)
        if mouse_dy:
            self.rotate_pitch(delta_y=mouse_dy * MOUSE_SENSITIVITY)

    def keyboard_control(self):
        key_state = pg.key.get_pressed()
        vel = PLAYER_SPEED * self.app.delta_time
        next_step = glm.vec2()
        #
        if key_state[KEYS["FORWARD"]]:
            next_step += self.move_forward(vel)
        if key_state[KEYS["BACK"]]:
            next_step += self.move_back(vel)
        if key_state[KEYS["STRAFE_R"]]:
            next_step += self.move_right(vel)
        if key_state[KEYS["STRAFE_L"]]:
            next_step += self.move_left(vel)
        #
        self.move(next_step=next_step)

    def move(self, next_step):
        if not self.is_collide(dx=next_step[0]):
            self.position.x += next_step[0]

        if not self.is_collide(dz=next_step[1]):
            self.position.z += next_step[1]

    def is_collide(self, dx=0, dz=0):
        int_pos = (
            int(
                self.position.x
                + dx
                + (PLAYER_SIZE if dx > 0 else -PLAYER_SIZE if dx < 0 else 0)
            ),
            int(
                self.position.z
                + dz
                + (PLAYER_SIZE if dz > 0 else -PLAYER_SIZE if dz < 0 else 0)
            ),
        )
        # check doors
        if int_pos in self.door_map:
            return self.door_map[int_pos].is_closed
        # check walls
        return int_pos in self.wall_map
