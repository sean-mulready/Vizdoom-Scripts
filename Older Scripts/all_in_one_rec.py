# import important stuff
import vizdoom as vzd
import os 
import csv
import time
import numpy as np
import pandas as pd
from psychopy import core, visual, event
import pickle                               # pass on variables needed for replay and processing



#img-dir for instructions

img_dir = os.getcwd() + "/exp_img/"

# Enter Subject Data
sub_num = '1'           # ongoing numerizing as string
sub_id = 'HECO91M'      # Construct ID as : First 2 letters of birth-location, first 2 letters of mother's first name, last two digits of birth-year, gender in one letter
age = 32                # Age as Integer
gender = 'm'            # gender as string (m = male, f=female, nb = non-binary, o = other)
glasses = True          # as boolean


# Enter experiment configurations (episodes and ticrate = speed and time-resolution)
ep_basic = 1
ticrate_basic = 50 #number of tics('state-loops') per second, default is 35

# specify number of blocks, make sure it's even
block_num = 1 
if block_num % 2 == 0:
    None
elif block_num %2 != 0:
    block_num = (block_num+1)

# psychopy setup for interface


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




# mu-vector and shuffle

mu_vec = int(block_num/2)*[0,1]
np.random.shuffle(mu_vec)



#start with greeting instructions
# window
screen_size = [1920, 1080]
win = visual.Window(
    color='black',
    size=[1920, 1080],
    fullscr=True)

# key to go forward

continue_key = 'space'


# greeting instructions before experiment

instructions_greeting = {
    'greeting 1': {'image': os.path.join(img_dir, "instructions_greeting1.jpg"), 'image_size': (1.8,1.6)},
    'greeting 2': {'image': os.path.join(img_dir, "instructions_greeting2.jpg"), 'image_size': (1.8,1.6)},
    'greeting 3': {'image': os.path.join(img_dir, "instructions_greeting3.jpg"), 'image_size': (1.8,1.6)},
    'greeting 4': {'image': os.path.join(img_dir, "instructions_greeting4.jpg"), 'image_size': (1.8,1.6)}
}
# Iterate over instructions
for instruction_key, instruction_data in instructions_greeting.items():
    image_size = instruction_data.get('image_size')  # Get image size if specified
    # Check if the instruction has text or not
    if 'text' in instruction_data:
        present_text(win, 
                     instr_text=instruction_data['text'], 
                     image=instruction_data.get('image'),
                     instructions=True,
                     continue_key=continue_key,
                     image_size=image_size,  # Pass image size to present_text function
                     )
    else:
        present_text(win, 
                     image=instruction_data.get('image'),
                     instructions=True,
                     continue_key=continue_key,
                     image_size=image_size,  # Pass image size to present_text function
                     )

# a blank black screen for the background. 
present_text(window_instance = win,
             instr_text= '',
             instructions = False
             )




##### Basic instructions
#needs to be worked on!!!!!!########################################
instructions_basic = {
    'begin_1': {'image': os.path.join(img_dir, "instructions_begin1.jpg"), 'image_size': (1.8,1.6)},
    'basic_goal': {'image': os.path.join(img_dir, "instructions_basic_goal.jpg"), 'image_size': (1.8,1.6)},
    'basic_control': {'image': os.path.join(img_dir, "instructions_basic_control.jpg"), 'image_size': (1.8,1.6)},
    'basic_inversion': {'image': os.path.join(img_dir, "instructions_basic_inversion.jpg"), 'image_size': (1.8,1.6)},
    'basic_important_note': {'image': os.path.join(img_dir, "instructions_basic_important_note.jpg"), 'image_size': (1.8,1.6)},
    'basic_ep_info': {'text': f'Erschießen Sie so schnell wie möglich die Kreatur! Sie werden {block_num} Blöcke mit je {ep_basic} Durchgängen spielen. \n\n Bitte LEERTASTE drücken, um fortzufahren'}
    

}

# Iterate over instructions
for instruction_key, instruction_data in instructions_basic.items():
    image_size = instruction_data.get('image_size')  # Get image size if specified
    # Check if the instruction has text or not
    if 'text' in instruction_data:
        present_text(win, 
                     instr_text=instruction_data['text'], 
                     image=instruction_data.get('image'),
                     instructions=True,
                     continue_key=continue_key,
                     image_size=image_size,  # Pass image size to present_text function
                     )
    else:
        present_text(win, 
                     image=instruction_data.get('image'),
                     instructions=True,
                     continue_key=continue_key,
                     image_size=image_size,  # Pass image size to present_text function
                     )
#win.close()
    # function for choosing if normal or inverted movement in relation to 
    # the parameter mu and the side on which the Cacodemon spawns

# a blank black screen for the background. 
present_text(window_instance = win,
             instr_text= '',
             instructions = False
             )


def movement_probabilities(cacodemon_position, mu):
    prob_norm = 1
    prob_inv = 0
    if mu == 0:
        if cacodemon_position < (-9):
            prob_norm = 0.3
            prob_inv = 0.7
        elif cacodemon_position > 75:
            prob_norm = 0.7
            prob_inv = 0.3
    elif mu == 1:
        if cacodemon_position < (-9):
            prob_norm = 0.7
            prob_inv = 0.3
        elif cacodemon_position > 75:
            prob_norm = 0.3
            prob_inv = 0.7
    return np.random.choice([0,1], p = [prob_norm,prob_inv])


#implementing the array for mu 
mu_arr = np.full(block_num, np.nan, dtype = np.int32)

#playing the game blockwise
for b in range(block_num):
    win = visual.Window(
            color='black',
            size=[1920, 1080],
            fullscr=True)

    present_text(window_instance=win,
                    instr_text=f'Starte Block {b + 1} von {block_num}  \n\n' \
                        'LEERTASTE um zu beginnen ...',
                        continue_key=continue_key)
    
    win.close()
    



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

    # Initialize the game
    game.init()

    # RECORDING



    # using up elements of shuffled vector
    mu = mu_vec.pop(0)
    # implementing the array for tracking the movement-choices 
    movement_choice_arr = np.full(ep_basic, np.nan, dtype = np.int32)
    
    # Loop through episodes
    for i in range(ep_basic):
        
        print("Episode #" + str(i + 1))
        #start the recording
        game.new_episode(f"{sub_id}_b{b+1}_e{i+1}_basic_rec.lmp")

        #to get the state and in the next step the object_info
        #to be able to determine the movement we need to go into 
        #the game (if not...) before going into the game (while not..)
        #as data seems to show, that costs 2 Tics in time with ticrate set to 50

        if not game.is_episode_finished():
        
            state = game.get_state()

            #getting the cacodemon's position for
            #movement-determination
            for o in state.objects:
                if o.name == "Cacodemon":
                    cacodemon_position = o.position_y
                
                    break 

            movement_choice = movement_probabilities(cacodemon_position,mu)
            
            # bind keys according to result of the decision
            if movement_choice == 1:
                game.send_game_command("bind D +moveleft")
                game.send_game_command("bind A +moveright")
            else:
                game.send_game_command("bind A +moveleft")
                game.send_game_command("bind D +moveright")
            
        
        # game will stop at 300 Tics by default
        # which is 6 seconds at a ticrate of 50
        while not game.is_episode_finished():
            state = game.get_state()
            game.advance_action()
            
        print("Episode finished!")
        print("Total reward:", game.get_total_reward())
        print("************************")

        #track movement choices
        movement_choice_arr[i]= movement_choice

        time.sleep(0.5)
        
    # buffer-episode: needed as the last episode isn't recorded
    game.new_episode()

    while not game.is_episode_finished():
        
            state = game.get_state()

            if state.number > 0:
                break

    mu_arr[b] = mu 
    
    # set keys to the original movement
    game.send_game_command("bind A +left")
    game.send_game_command("bind D +right")
    game.close()
    

# window
screen_size = [1920, 1080]
win = visual.Window(
    color='black',
    size=[1920, 1080],
    fullscr=True)

present_text(win, 
             image = os.path.join(img_dir, "instructions_well_done1.jpg"),
             instructions=True,
             continue_key=continue_key,
             image_size=(1.8,1.6),  # Pass image size to present_text function
            )
present_text(win, 
             image = os.path.join(img_dir, "instructions_break_offering.jpg"),
             instructions=True,
             continue_key=continue_key,
             image_size=(1.8,1.6),  # Pass image size to present_text function
            )
win.close()

###### PLAY AND RECORD HEALTH GATHERING #####################################################################
#############################################################################################################
#############################################################################################################

# window
screen_size = [1920, 1080]
win = visual.Window(
    color='black',
    size=[1920, 1080],
    fullscr=True)




ep_health = 1
ticrate_health = 30
max_time = 180  # make sure to check the .cfg-file for max tics and ticrate for actual maximum time!

#instructions for health gathering
instructions_health_gathering = {
    'begin_2': {'image': os.path.join(img_dir, "instructions_begin2.jpg"), 'image_size': (1.8,1.6)},
    'health_gathering_goal': {'image': os.path.join(img_dir, "instructions_health_gathering_goal.jpg"), 'image_size': (1.8,1.6)},
    'health_gathering_control': {'image': os.path.join(img_dir, "instructions_health_gathering_control.jpg"), 'image_size': (1.8,1.6)},
    'health_gathering_ep_info': {'text': f'Bleiben Sie so lange wie möglich am Leben!  Dazu werden Sie {ep_health} Durchgänge spielen. Nach maximal {max_time} Sekunden wird ein Durchgang beendet. \n\n Bitte LEERTASTE drücken, um fortzufahren'},
    'health_gathering_ready': {'text': f'Bereit? Durch drücken auf die LEERTASTE beginnt das Spiel.'}
    

}

# Iterate over instructions
for instruction_key, instruction_data in instructions_health_gathering.items():
    image_size = instruction_data.get('image_size')  # Get image size if specified
    # Check if the instruction has text or not
    if 'text' in instruction_data:
        present_text(win, 
                     instr_text=instruction_data['text'], 
                     image=instruction_data.get('image'),
                     instructions=True,
                     continue_key=continue_key,
                     image_size=image_size,  # Pass image size to present_text function
                     )
    else:
        present_text(win, 
                     image=instruction_data.get('image'),
                     instructions=True,
                     continue_key=continue_key,
                     image_size=image_size,  # Pass image size to present_text function
                     )

win.close()

game = vzd.DoomGame()
# where to get the .ini-file from
game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini")


# loading the config file
# Info: Maximum Ticrate currently set to 5.400 (180 Secs)

game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/health_gathering_supreme.cfg")
# Enables information about all objects present in the current episode/level.
game.set_objects_info_enabled(True)

# Enables information about all sectors (map layout).
game.set_sectors_info_enabled(True)

# Clear all game variables first to unify the variables for all scenarios
game.clear_available_game_variables()

# Add game variables for Health and Ammo
game.add_available_game_variable(vzd.GameVariable.HEALTH)

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
game.set_ticrate(ticrate_health)

# Initialize the game
game.init()


# RECORDING

for i in range(ep_health):
    game.new_episode(f"{sub_id}_e{i+1}_health_gathering_rec.lmp")
    while not game.is_episode_finished():
            state = game.get_state()
            game.advance_action()
            
    print("Episode finished!")
    print("Total reward:", game.get_total_reward())
    print("************************")


# buffer-episode: needed as the last episode isn't recorded
game.new_episode()

while not game.is_episode_finished():
        
    state = game.get_state()

    if state.number > 0:
        break

    
    
    
game.close()


##### Interlude and break offering

# window
screen_size = [1920, 1080]
win = visual.Window(
    color='black',
    size=[1920, 1080],
    fullscr=True)

present_text(win, 
             image = os.path.join(img_dir, "instructions_well_done2.jpg"),
             instructions=True,
             continue_key=continue_key,
             image_size=(1.8,1.6),  # Pass image size to present_text function
            )
present_text(win, 
             image = os.path.join(img_dir, "instructions_break_offering.jpg"),
             instructions=True,
             continue_key=continue_key,
             image_size=(1.8,1.6),  # Pass image size to present_text function
            )
win.close()

###### PLAY AND RECORD MY WAY HOME #####################################################
########################################################################################
########################################################################################






ep_home = 1
ticrate_home = 30

# window
screen_size = [1920, 1080]
win = visual.Window(
    color='black',
    size=[1920, 1080],
    fullscr=True)

###needs to be worked on!!!!
instructions_my_way_home = {
    'begin_3': {'image': os.path.join(img_dir, "instructions_begin3.jpg"), 'image_size': (1.8,1.6)},
    'my_way_home_goal': {'image': os.path.join(img_dir, "instructions_my_way_home_goal.jpg"), 'image_size': (1.8,1.6)},
    'my_way_home_control': {'image': os.path.join(img_dir, "instructions_my_way_home_control.jpg"), 'image_size': (1.8,1.6)},
    'my_way_home_ep_info': {'text': f'Navigieren Sie durch das Labyrinth, finden Sie das Objekt!  Dazu werden Sie {ep_home} Durchgänge spielen.\n\n Bitte LEERTASTE drücken, um fortzufahren'},
    'my_way_home_ready': {'text': f'Bereit? Durch drücken auf die LEERTASTE beginnt das Spiel.'}

}

# Iterate over instructions
for instruction_key, instruction_data in instructions_my_way_home.items():
    image_size = instruction_data.get('image_size')  # Get image size if specified
    # Check if the instruction has text or not
    if 'text' in instruction_data:
        present_text(win, 
                     instr_text=instruction_data['text'], 
                     image=instruction_data.get('image'),
                     instructions=True,
                     continue_key=continue_key,
                     image_size=image_size,  # Pass image size to present_text function
                     )
    else:
        present_text(win, 
                     image=instruction_data.get('image'),
                     instructions=True,
                     continue_key=continue_key,
                     image_size=image_size,  # Pass image size to present_text function
                     )

win.close()

game = vzd.DoomGame()
    # where to get the .ini-file from
game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini")


# loading the config file
# Info: Maximum Ticrate currently set to 5.400 (180 Secs)
game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/my_way_home.cfg")
# Enables information about all objects present in the current episode/level.
game.set_objects_info_enabled(True)

# Enables information about all sectors (map layout).
game.set_sectors_info_enabled(True)

# Clear all game variables first to unify the variables for all scenarios
game.clear_available_game_variables()

# Add game variables for Health and Ammo
game.add_available_game_variable(vzd.GameVariable.HEALTH)

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
game.set_ticrate(ticrate_home)

# Initialize the game
game.init()


# RECORDING

for i in range(ep_home):
    game.new_episode(f"{sub_id}_e{i+1}_my_way_home_rec.lmp")
    while not game.is_episode_finished():
            state = game.get_state()
            game.advance_action()
            
    print("Episode finished!")
    print("Total reward:", game.get_total_reward())
    print("************************")


# buffer-episode: needed as the last episode isn't recorded
game.new_episode()

while not game.is_episode_finished():
        
    state = game.get_state()

    if state.number > 0:
        break

    
    
    
game.close()

# window
screen_size = [1920, 1080]
win = visual.Window(
    color='black',
    size=[1920, 1080],
    fullscr=True)

##### Interlude and break offering
present_text(win, 
             image = os.path.join(img_dir, "instructions_well_done3.jpg"),
             instructions=True,
             continue_key=continue_key,
             image_size=(1.8,1.6),  # Pass image size to present_text function
            )
present_text(win, 
             image = os.path.join(img_dir, "instructions_break_offering.jpg"),
             instructions=True,
             continue_key=continue_key,
             image_size=(1.8,1.6),  # Pass image size to present_text function
            )
win.close()
###### PLAY AND RECORD TAKE COVER ###############################################################
################################################################################################
#################################################################################################



#### instruction loop!


ep_cover = 4
ticrate_cover = 30


# window
screen_size = [1920, 1080]
win = visual.Window(
    color='black',
    size=[1920, 1080],
    fullscr=True)

##needs to be worked on!!!
instructions_take_cover = {
    'begin_4': {'image': os.path.join(img_dir, "instructions_begin4.jpg"), 'image_size': (1.8,1.6)},
    'take_cover_goal': {'image': os.path.join(img_dir, "instructions_take_cover_goal.jpg"), 'image_size': (1.8,1.6)},
    'take_cover_control': {'image': os.path.join(img_dir, "instructions_take_cover_control.jpg"), 'image_size': (1.8,1.6)},
    'take_cover_ep_info': {'text': f'Weichen Sie den Feuerbällen aus!  Dazu werden Sie {ep_cover} Durchgänge spielen.\n\n Bitte LEERTASTE drücken, um fortzufahren'},
    'take_cover_ready': {'text': f'Bereit? Durch drücken auf die LEERTASTE beginnt das Spiel.'}

}

# Iterate over instructions
for instruction_key, instruction_data in instructions_take_cover.items():
    image_size = instruction_data.get('image_size')  # Get image size if specified
    # Check if the instruction has text or not
    if 'text' in instruction_data:
        present_text(win, 
                     instr_text=instruction_data['text'], 
                     image=instruction_data.get('image'),
                     instructions=True,
                     continue_key=continue_key,
                     image_size=image_size,  # Pass image size to present_text function
                     )
    else:
        present_text(win, 
                     image=instruction_data.get('image'),
                     instructions=True,
                     continue_key=continue_key,
                     image_size=image_size,  # Pass image size to present_text function
                     )

win.close()

game = vzd.DoomGame()
    # where to get the .ini-file from
game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini")


# loading the config file
# Info: Maximum Ticrate currently set to 5.400 (180 Secs)
game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/take_cover.cfg")
# Enables information about all objects present in the current episode/level.
game.set_objects_info_enabled(True)

# Enables information about all sectors (map layout).
game.set_sectors_info_enabled(True)

# Clear all game variables first to unify the variables for all scenarios
game.clear_available_game_variables()

# Add game variables for Health and Ammo
game.add_available_game_variable(vzd.GameVariable.HEALTH)

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
game.set_ticrate(ticrate_cover)

# Initialize the game
game.init()

# Bind A and D to Movement for this scenario 
game.send_game_command("bind A +moveleft")
game.send_game_command("bind D +moveright")

# RECORDING

for i in range(ep_cover):
    game.new_episode(f"{sub_id}_e{i+1}_take_cover_rec.lmp")
    while not game.is_episode_finished():
            state = game.get_state()
            game.advance_action()
            
    print("Episode finished!")
    print("Total reward:", game.get_total_reward())
    print("************************")


# buffer-episode: needed as the last episode isn't recorded
game.new_episode()

while not game.is_episode_finished():
        
    state = game.get_state()

    if state.number > 0:
        break

    
# Bind A and D to original movement 
game.send_game_command("bind A +left")
game.send_game_command("bind D +right")    
    
game.close()
    






win = visual.Window(
            color='black',
            size=[1920, 1080],
            fullscr=True)


present_text(win, 
             image = os.path.join(img_dir, "instructions_well_done4.jpg"),
             instructions=True,
             continue_key=continue_key,
             image_size=(1.8,1.6),  # Pass image size to present_text function
            )
            


present_text(window_instance=win,
                    instr_text='Vielen Dank für Ihre Teilnahme! \n' \
                        'Das Experiment ist nun abgeschlossen. \n' \
                        'Wenn Sie am Ende dazu aufgefordert werden, drücken Sie' \
                            ' ein letztes Mal die LEERTASTE, der Bildschirm wird daraufhin schwarz.'\
                                'Anschließend geben Sie der Versuchsleitung Bescheid. Vielen Dank \n\n'\
                                    'Drücken Sie bitte jetzt die LEERTASTE')

win.close()



# pass on all variables needed for replaying


with open("myfile.pickle", "wb") as outfile: 
    pickle.dump(age, outfile)
    pickle.dump(sub_num, outfile)
    pickle.dump(sub_id, outfile)
    pickle.dump(gender, outfile)
    pickle.dump(glasses, outfile)
    pickle.dump(ep_basic, outfile)
    pickle.dump(ep_health, outfile)
    pickle.dump(ep_home, outfile)
    pickle.dump(ep_cover, outfile)
    pickle.dump(block_num, outfile)
    pickle.dump(ticrate_basic, outfile)
    pickle.dump(ticrate_health, outfile)
    pickle.dump(ticrate_home, outfile)
    pickle.dump(ticrate_cover, outfile)
    pickle.dump(mu_arr, outfile)
    pickle.dump(movement_choice_arr, outfile)
    
    
