# replay and analyse data
# UNDER CONSTRUCTION




import vizdoom as vzd
import os 

game = vzd.DoomGame()

#find a way to 'import' episodes number and other data from recording script??

episodes = 4
sub_id = "01"
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
game.set_mode(vzd.Mode.PLAYER)
game.init()


for i in range(episodes):

    # Replays episodes stored in given file. Sending game command will interrupt playback.
    game.replay_episode(f"{sub_id}_episode{i+1}_rec.lmp")

    while not game.is_episode_finished():
        s = game.get_state()

        # Use advance_action instead of make_action.
        game.advance_action()

        r = game.get_last_reward()
        # game.get_last_action is not supported and don't work for replay at the moment.

        print(f"State #{s.number}")
        print("Game variables:", s.game_variables[0])
        print("Reward:", r)
        print("=====================")

    print("Episode", i, "finished.")
    print("total reward:", game.get_total_reward())
    print("************************")

game.close()

# Delete recordings (*.lmp files).

for i in range(episodes):
    os.remove(f"{sub_id}_episode{i+1}_rec.lmp")