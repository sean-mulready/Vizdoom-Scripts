# Script to record gameplay in Spectator Mode
# UNDER CONSTRUCTION
# for some reason, last episode isn't recorded -> current workaround: buffer-episode that instantly is terminated

import vizdoom as vzd
import time

# Enter Subject Data
sub_id = "01"




game = vzd.DoomGame()
# where to get the .ini-file from
game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini")

# Choose the scenario config file you wish to watch.
# Don't load two configs because the second will overwrite the first one.
# Multiple config files are okay, but combining these ones doesn't make much sense.

game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/basic.cfg")

# Enables information about all objects present in the current episode/level.
game.set_objects_info_enabled(True)

# Enables information about all sectors (map layout).
game.set_sectors_info_enabled(True)

# Clear all game variables first to unify the variables for all scenarios
game.clear_available_game_variables()

# Add game variables for Health and Ammo
game.add_available_game_variable(vzd.GameVariable.HEALTH)
game.add_available_game_variable(vzd.GameVariable.AMMO2)

# Add Game Variables for the position
pos_x = game.add_available_game_variable(vzd.GameVariable.POSITION_X)
pos_y = game.add_available_game_variable(vzd.GameVariable.POSITION_Y)
pos_z = game.add_available_game_variable(vzd.GameVariable.POSITION_Z)
angle = game.add_available_game_variable(vzd.GameVariable.ANGLE)

# Set screen size
game.set_screen_resolution(vzd.ScreenResolution.RES_1280X960)

# Enables spectator mode so you can play, but your agent is supposed to watch, not you.
game.set_window_visible(True)
game.set_mode(vzd.Mode.SPECTATOR)
game.init()

# Recording
print("\nRECORDING EPISODES")
print("************************\n")

# Specify how many Episodes 
episodes = 10


# Loop through episodes
for i in range(episodes):
    print("Episode #" + str(i + 1))
    game.new_episode(f"{sub_id}_episode{i+1}_rec.lmp")

    while not game.is_episode_finished():
        s = game.get_state()
        game.advance_action()
        # when to stop the episode, default by config-file is 300 tics
        if s.number > 150: 
            break
    print("Episode finished!")
    print("Total reward:", game.get_total_reward())
    print("************************")
    time.sleep(0.5)
game.new_episode(f'buffer.lmp')
while not game.is_episode_finished():
    s = game.get_state()
    if s.number >= 0:
        break

   
game.close()
    

