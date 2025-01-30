import vizdoom as vzd
import time
import os 
import time
import csv
import numpy as np
from psychopy import core, visual, event


# presenting the instructions
def present_text(window_instance,
                 instr_text='placeholder',
                 text_size=0.075,
                 instructions=True,
                 text_position=(0., 0.),
                 unit='norm',
                 continue_key='space',
                 image=None,
                 image_size=None):
    
    # Calculate default text position
    default_text_position = (0., 0.)
    
    # Check if only image is provided
    if instr_text == 'placeholder' and image:
        # Draw the image stimulus at the center
        image_position = (0., 0)
        if image_size:
            image_stim = visual.ImageStim(window_instance, image, pos=image_position, size=image_size)
        else:
            image_stim = visual.ImageStim(window_instance, image, pos=image_position, size=(0.5, 0.5))  # Default size
        image_stim.draw()
    
    else:
        # Draw the text stimulus if text is provided
        if instr_text != 'placeholder':
            if image:  # If both text and image are present
                text_position = (0., 0.5)  # Position above the center
            else:
                text_position = default_text_position  # Center position if only text is present
                
            text_stim = visual.TextStim(window_instance, 
                                        height=text_size, 
                                        units=unit, 
                                        pos=text_position,
                                        wrapWidth=1.5
                                    )
            text_stim.setText(instr_text)
            text_stim.draw()

        # Draw the image stimulus if image is provided
        if image:
            image_position = (0, -0.5)  # Position below the center
            if image_size:
                image_stim = visual.ImageStim(window_instance, image, pos=image_position, size=image_size)
            else:
                image_stim = visual.ImageStim(window_instance, image, pos=image_position, size=(0.5, 0.5))  # Default size
            image_stim.draw()
    
    window_instance.flip()
    
    if instructions:
        event.waitKeys(keyList=[continue_key])
    else:
        core.wait(0.01)




ep_basic = 3
ticrate_basic = 50
episode_maxtime = 3

game = vzd.DoomGame()
    # where to get the .ini-file from
game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini")


# loading the config file. Created my own which relates to my own experiment.wad
# with customized map and spwaning ranges for the cacodemon
game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/experiment.cfg")

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
game.set_render_hud(False)
game.set_mode(vzd.Mode.ASYNC_SPECTATOR)
game.set_ticrate(ticrate_basic)
 # set the maximum time of the game in tics
game.set_episode_timeout(episode_maxtime*ticrate_basic)
game.set_console_enabled(True)
# Initialize the game
game.init()
# Loop through episodes
for i in range(ep_basic):
    
    print("Episode #" + str(i + 1))
    #start the recording
    
    game.new_episode()


    #to get the state and in the next step the object_info
    #to be able to determine the movement we need to go into 
    #the game (if not...) before going into the game (while not..)
    #as data seems to show, that costs 2 Tics in time with ticrate set to 50

    
    while not game.is_episode_finished():
        state = game.get_state()
        game.advance_action()
    
     
    print("Episode finished!")
    print("Total reward:", game.get_total_reward())
    print("************************")
    EpisodeReward = game.get_total_reward()
    EpisodeTime = (game.get_episode_time() * (1/ticrate_basic))

    if game.is_episode_finished():

        # Pause and show PsychoPy reward
        reward = game.get_total_reward()
        print(f"Reward: {reward}")
        

        # PsychoPy reward display logic here
        # For example:
        win = visual.Window()
        msg = visual.TextStim(win, text=f"Reward: {reward}")
        msg.draw()
        win.flip()
        core.wait(2)
        win.close()

        
   
# buffer-episode: needed as the last episode isn't recorded
game.new_episode()

while not game.is_episode_finished():
    
        state = game.get_state()

        if state.number > 0:
            break