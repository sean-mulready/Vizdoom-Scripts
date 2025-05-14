


# import important stuff
import vizdoom as vzd
import os 
import time
import csv
import numpy as np
from psychopy import core, visual, event



##################################### TO FILL OUT BEFORE STARTING THE EXPERIMENT! ######################################################
########################################################################################################################################
# Enter Subject Data
sub_num = '8'                       # ongoing numerizing as string
age = 26                            # Age as Integer in years
sex = 'm'                           # sex as string (m = male, f=female, o = other)
handedness = 'right'                # handedness as left or right (string)
eyesight_correction = True          # as boolean
exp_sequence = 'viz-gab-sym'        # permutation of experiments, ViZDoom = viz, Gabor Patch Discrimination = gab, Symmetric Bandit Task = sym, as string


# Enter experiment configurations (episodes and ticrate = speed and time-resolution)
ep_basic = 5 # number of episodes = number of trials
episode_maxtime = 6 # in seconds, always add one second as the spawning is delayed!
ticrate_basic = 50 #number of tics('state-loops') per second, default is 35
block_num = 6 #number of blocks
training_ep = 2 # number of episodes per movement training
target_name = "Bullseye" #enter the Target Actors name like Bullseye, DoomImp, Cacodemon, etc

########################################################################################################################################
########################################################################################################################################

# specify number of blocks, make sure it's even
if block_num % 2 == 0:
    None
elif block_num %2 != 0:
    block_num = (block_num+1)

# create random list of the two varations 

var_shuffle = int(block_num/2)*[1,2]
np.random.shuffle(var_shuffle)

# File path
filename = 'subjects.tsv'



# Check if file exists
file_exists = os.path.isfile(filename)

# Function to check if sub_num already exists in the file
def check_sub_num_exists(filename, sub_num):
    if file_exists:
        with open(filename, 'r') as tsvfile:
            csv_reader = csv.reader(tsvfile, delimiter='\t')
            for row in csv_reader:
                if row and row[0] == sub_num:
                    return True
    return False

# Check if sub_num is already in the file
if check_sub_num_exists(filename, sub_num):
    raise ValueError(f"Error: sub_num {sub_num} already exists in the file.")
else:
    # Check if file exists
    file_exists = os.path.isfile(filename)
    # Open the file in append mode
    with open(filename, 'a', newline='') as tsvfile:
        csv_writer = csv.writer(tsvfile, delimiter='\t')
    
        # If the file doesn't exist, write the header
        if not file_exists:
            columns = [
                'sub_num',
                'age',
                'sex',
                'handedness',
                'eyesight correction',
                'sequence of experiments'
            ]
            csv_writer.writerow(columns)
        
        # Add the new row of data
        row = [
            sub_num,
            age,
            sex,
            handedness,
            eyesight_correction,
            exp_sequence
        ]
        
        csv_writer.writerow(row)




# psychopy setup for interface


# presenting the instructions
def present_text(window_instance,
                 instr_text='placeholder',
                 text_size=0.075,
                 instructions=False,
                 break_offering=False,
                 block_start=False,
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
    elif break_offering:
        event.waitKeys(maxWait = 300, keyList=[continue_key])  # break ends latest after 5 mins
    elif block_start:
        event.waitKeys(maxWait = 60, keyList=[continue_key]) #block starts latest after 1 min
    else:
        None






#start with greeting instructions
# window
screen_size = [1920, 1080]
win = visual.Window(
    color='black',
    size=[1920, 1080],
    fullscr=True)

# key to go forward

continue_key = 'space'

#img-dir for instructions

img_dir = os.getcwd() + "/exp_img/"
# greeting instructions before experiment

instructions_greeting = {
    'greeting 1': {'image': os.path.join(img_dir, "instructions_greeting1.jpg"), 'image_size': (1.8,1.6)},
    'greeting 2': {'image': os.path.join(img_dir, "instructions_greeting2.jpg"), 'image_size': (1.8,1.6)},
    'greeting 3': {'image': os.path.join(img_dir, "instructions_greeting_3_bachelor.jpg"), 'image_size': (1.8,1.6)}
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


##### Basic instructions Part 1 ############

instructions_basic_1 = {
    'begin_1': {'image': os.path.join(img_dir, "instructions_begin.jpg"), 'image_size': (1.8,1.6)},
    'basic_goal': {'image': os.path.join(img_dir, "instructions_basic_target.jpg"), 'image_size': (1.8,1.6)},
    'basic_control': {'image': os.path.join(img_dir, "instructions_basic_control.jpg"), 'image_size': (1.8,1.6)},
    'basic_trial_steps': {'image': os.path.join(img_dir, "instructions_basic_trial_steps.jpg"), 'image_size': (1.8,1.6)},
    'basic_trial_start_appearing': {'image': os.path.join(img_dir, "instructions_basic_start_appearing.jpg"), 'image_size': (1.8,1.6)},
    'basic_trial_align': {'image': os.path.join(img_dir, "instructions_basic_align.jpg"), 'image_size': (1.8,1.6)},
    'basic_trial_reward': {'image': os.path.join(img_dir, "instructions_basic_reward.jpg"), 'image_size': (1.8,1.6)},
    'basic_inversion': {'image': os.path.join(img_dir, "instructions_basic_inversion_target.jpg"), 'image_size': (1.8,1.6)},
    'basic_training_start': {'text': f'Um Sie mit der Steuerung vertraut zu machen, werden Sie nun zwei Blöcke mit je 10 Durchläufen spielen. \n' \
                                     f'Der erste Block wird mit normaler Steuerung sein, der zweite Block mit invertierter Steuerung. \n\n' \
                                     f'Bitte LEERTASTE drücken, um fortzufahren'},
    'basic_note_missing_target': {'image': os.path.join(img_dir, "instructions_basic_note_missing_target.jpg"), 'image_size': (1.8,1.6)}
}

# Iterate over instructions 1 until training blocks
for instruction_key, instruction_data in instructions_basic_1.items():
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

#training blocks

#normal movement

#instructions for the normal movement 

win = visual.Window(
        color='black',
        size=[1920, 1080],
        fullscr=True)

present_text(window_instance=win,
                block_start = True,
                instr_text=f'Starte Trainingsblock mit normaler Steuerung  \n\n' \
                    'LEERTASTE um zu beginnen ...',
                    continue_key=continue_key)

win.close()

# start training for normal movement


game = vzd.DoomGame()
# where to get the .ini-file from
game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini")


# loading the config file. Created my own which relates to my own experiment.wad
# with customized map and spwaning ranges for the target
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

# makes the game window visible, as humans do play it
game.set_window_visible(True)
# If the hud (available ammo, health, etc.) is visible
game.set_render_hud(False)
# set an async spectator mode, so the agent (computer) watches and the human get's to play
game.set_mode(vzd.Mode.ASYNC_SPECTATOR) 
#set the ticrate (frames per second = ingame time)
game.set_ticrate(ticrate_basic)



# Initialize the game
game.init()

#normal movement
game.send_game_command("bind A +moveleft")
game.send_game_command("bind D +moveright")


# implement Total Reward of Block:
block_total_reward = 0 
# Loop through episodes
for i in range(training_ep):

    # set the maximum time of the game in tics
    game.set_episode_timeout(episode_maxtime*ticrate_basic)
    
    print("Episode #" + str(i + 1))
    game.new_episode()

    while not game.is_episode_finished():

        state = game.get_state()
        game.advance_action()

        # observing action and time
        last_action = game.get_last_action()
        current_time = game.get_episode_time()  # Get current episode time in tics

        # for the case that target is missed, episode ends latest 0.5 seconds after shooting
        if last_action == [0.0,0.0,1.0]:
            missed_shot = current_time + 25 # set the new time to 25 tics after shooting
            game.set_episode_timeout(missed_shot)

    print("Episode finished!")
    print("Total reward:", game.get_total_reward())
    print("************************")
    # Adding Episode Reward to Block Reward
    EpisodeReward = game.get_total_reward()
    block_total_reward = (block_total_reward + game.get_total_reward())

    if game.is_episode_finished():

        win = visual.Window(
        color='black',
        fullscr=True)
        msg = visual.TextStim(win, text=f"Punkte: {int(EpisodeReward)} \n\n\n" \
                                f"Total: {int(block_total_reward)}")
        msg.draw()
        win.flip()
        core.wait(1)
        win.close()

game.close()

# intersection instructions 

win = visual.Window(
        color='black',
        size=[1920, 1080],
        fullscr=True)

present_text(window_instance=win,
                block_start = True,
                instr_text=f'Sehr gut! Und weiter gehts !  \n\n' \
                    'LEERTASTE um fortzufahren ...',
                    continue_key=continue_key)

win.close()

win = visual.Window(
        color='black',
        size=[1920, 1080],
        fullscr=True)

present_text(window_instance=win,
                block_start = True,
                instr_text=f'Starte Trainingsblock mit invertierter Steuerung  \n\n' \
                    'LEERTASTE um zu beginnen ...',
                    continue_key=continue_key)

win.close()

# start training for inverted movement

game = vzd.DoomGame()
# where to get the .ini-file from
game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini")


# loading the config file. Created my own which relates to my own experiment.wad
# with customized map and spwaning ranges for the target
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

# makes the game window visible, as humans do play it
game.set_window_visible(True)
# If the hud (available ammo, health, etc.) is visible
game.set_render_hud(False)
# set an async spectator mode, so the agent (computer) watches and the human get's to play
game.set_mode(vzd.Mode.ASYNC_SPECTATOR) 
#set the ticrate (frames per second = ingame time)
game.set_ticrate(ticrate_basic)




# Initialize the game
game.init()

#inverted movement
game.send_game_command("bind D +moveleft")
game.send_game_command("bind A +moveright")

# implement Total Reward of Block:
block_total_reward = 0 
# Loop through episodes
for i in range(training_ep):

    # set the maximum time of the game in tics
    game.set_episode_timeout(episode_maxtime*ticrate_basic)
    
    print("Episode #" + str(i + 1))
    game.new_episode()
    

   
    while not game.is_episode_finished():

        state = game.get_state()
        game.advance_action()

        # observing action and time
        last_action = game.get_last_action()
        current_time = game.get_episode_time()  # Get current episode time in tics

        # for the case that target is missed, episode ends latest 0.5 seconds after shooting
        if last_action == [0.0,0.0,1.0]:
            missed_shot = current_time + 25 # set the new time to 25 tics after shooting
            game.set_episode_timeout(missed_shot)
                
    print("Episode finished!")
    print("Total reward:", game.get_total_reward())
    print("************************")

    # Adding Episode Reward to Block Reward
    EpisodeReward = game.get_total_reward()
    block_total_reward = (block_total_reward + game.get_total_reward())

    if game.is_episode_finished():

        win = visual.Window(
        color='black',
        fullscr=True)
        msg = visual.TextStim(win, text=f"Punkte: {int(EpisodeReward)} \n\n\n" \
                                f"Total: {int(block_total_reward)}")
        msg.draw()
        win.flip()
        core.wait(1)
        win.close()

game.close()

# Final instructions before the experiment


instructions_basic_2 = {

    'basic_good_job': {'text': f'Sehr gut! Damit kann das Experiment starten !  \n\n' \
                    'LEERTASTE um fortzufahren ...'},
    'basic_probabilities': {'image': os.path.join(img_dir, "instructions_basic_movement_probabilities.jpg"), 'image_size': (1.8,1.6)},
    'basic_note_missing_target': {'image': os.path.join(img_dir, "instructions_basic_last_notes.jpg"), 'image_size': (1.8,1.6)},
    'basic_ep_info': {'text': f'Schießen Sie so schnell wie möglich auf das Ziel! \n' \
                      f'Sie werden {block_num} Blöcke mit je {ep_basic} Durchgängen spielen. \n' \
                      f'Sie haben ab Erscheinen des Ziels {episode_maxtime-1} Sekunden Zeit und einen Schuss pro Durchlauf \n\n' \
                      f'Bitte LEERTASTE drücken, um fortzufahren'}
   
}


# window
win = visual.Window(
        color='black',
        size=[1920, 1080],
        fullscr=True)

# Iterate over instructions 2 and then start experiment
for instruction_key, instruction_data in instructions_basic_2.items():
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



# deciding the movement probabilities
# for each variation, there is an optimal choice, so one key where
# the chance for the necessary movement is higher
# e.g.: If the variation is 1 there's a probability of .8, the movement is
# inverted if the target spawns on the right side (optimal choice A/left)
# and a probability of .8 that the movement is normal 
# if the target spawns on the left side (optimal choice A/left)
# so if the variation for a block of episodes is 1, the optimal choice is A/left
# for every episode

def movement_probabilities(target_position, variation):
    prob_norm = 1
    prob_inv = 0
    if variation == 1:
        if target_position < (-9): #if the target spawns on the right side
            prob_norm = 0.2
            prob_inv = 0.8
        elif target_position > 75: #if the target spawns on the left side
            prob_norm = 0.8
            prob_inv = 0.2
    elif variation == 2:
        if target_position < (-9): #if the target spawns on the right side
            prob_norm = 0.8
            prob_inv = 0.2
        elif target_position > 75: # if the target spawns on the left side
            prob_norm = 0.2
            prob_inv = 0.8
    return np.random.choice([0,1], p = [prob_norm,prob_inv])



#playing the game blockwise
for b in range(block_num):
    win = visual.Window(
            color='black',
            size=[1920, 1080],
            fullscr=True)

    present_text(window_instance=win,
                 block_start = True,
                    instr_text=f'Starte Block {b + 1} von {block_num}  \n\n' \
                        'LEERTASTE um zu beginnen ...',
                        continue_key=continue_key)
    
    win.close()
    



    game = vzd.DoomGame()
    # where to get the .ini-file from
    game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini")


    # loading the config file. Created my own which relates to my own experiment.wad
    # with customized map and spwaning ranges for the target
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

    # makes the game window visible, as humans do play it
    game.set_window_visible(True)
    # If the hud (available ammo, health, etc.) is visible
    game.set_render_hud(False)
    # set an async spectator mode, so the agent (computer) watches and the human get's to play
    game.set_mode(vzd.Mode.ASYNC_SPECTATOR) 
    #set the ticrate (frames per second = ingame time)
    game.set_ticrate(ticrate_basic)
    

    # Initialize the game
    game.init()

    # RECORDING

    # using randomized variations
    variation = var_shuffle.pop(0)
    print(variation)
    
    # implement Total Reward of Block:
    block_total_reward = 0 
    # Loop through episodes
    for i in range(ep_basic):

        # set the maximum time of the game in tics
        game.set_episode_timeout(episode_maxtime*ticrate_basic)
        
        print("Episode #" + str(i + 1))
        #start the recording
        filename = f"{sub_num}_b{b+1}_e{i+1}_basic_rec.lmp"
        game.new_episode(filename)
        start_time = time.time()

        #to get the state and in the next step the object_info
        #to be able to determine the movement we need to go into 
        #the game (if not...) before going into the game (while not..)
        #as data seems to show, that costs 2 Tics in time with ticrate set to 50
        if not game.is_episode_finished():
            
            #state = game.get_state()
            target_position = 0 #initialize as none

            while target_position == 0 and game.get_episode_time() < 200 :   #breaking after 200 tics latest prevents crashing if target doesn't spawn at all
        
                state = game.get_state()

                #getting the targets' position for
                #movement-determination
            
                for o in state.objects:
                    if o.name == target_name:
                        target_position = o.position_y
                        print(f'target at {target_position}')
                        break
                game.advance_action()
                    
            movement_type = movement_probabilities(target_position,variation)
            
            # bind keys according to result of the decision
            if movement_type == 1:
                game.send_game_command("bind D +moveleft")
                game.send_game_command("bind A +moveright")
            else:
                game.send_game_command("bind A +moveleft")
                game.send_game_command("bind D +moveright")
        
        # Variables for tracking the first action and time of incorrect movement
        first_action = None
        incorrect_action_time = None
        # game will stop after defined maxTime 
        while not game.is_episode_finished():
            state = game.get_state()
            game.advance_action()
            
            # need the following: checking for the first movement action and in relation to side need to stop episode 1 (0.5) second after wrong movement
            last_action = game.get_last_action()
            current_time = game.get_episode_time()  # Get current episode time in tics

            # for the case that target is missed, episode ends latest 0.5 seconds after shooting
            if last_action == [0.0,0.0,1.0]:
                missed_shot = current_time + 25 # set the new time to 25 tics after shooting
                game.set_episode_timeout(missed_shot)

            # Find the first non-default action
            if first_action is None and last_action != ([0.0,0.0,0.0] or [0.0,0.0,1.0]) :
                first_action = last_action
                print(first_action)
                print(target_position)

                # Check if the action is incorrect
                if (target_position >= 75 and first_action == [0.0, 1.0, 0.0]) or (target_position <= -9 and first_action == [1.0, 0.0, 0.0]):
                        incorrect_action_time = current_time + 25  # Stop after 25 more tics so 0.5 seconds
                        game.set_episode_timeout(incorrect_action_time)  # Set new timeout, 

            


        print("Episode finished!")
        print("Total reward:", game.get_total_reward())
        print(f"Time: {time.time() - start_time}")
        print("************************")
        # Adding Episode Reward to Block Reward
        EpisodeReward = game.get_total_reward()
        block_total_reward = (block_total_reward + game.get_total_reward())

        if game.is_episode_finished():

            win = visual.Window(
            color='black',
            fullscr=True)
            msg = visual.TextStim(win, text=f"Punkte: {int(EpisodeReward)} \n\n\n" \
                                  f"Total: {int(block_total_reward)}")
            msg.draw()
            win.flip()
            core.wait(1)
            win.close()

               
        time.sleep(0.1)

        #saving metadata as game_data.tsv
        # make sure, file exists
        file_path = 'game_data.tsv'
        file_exists = os.path.isfile(file_path)

        # check movement type
        if np.isnan(movement_type):
            print(f"Warning: Episode {i+1} in Block {b+1} of {sub_num} doesn't contain valid movement-data. Metadata won't be saved.")
        else:
            with open(file_path, 'a', newline='') as tsvfile:
                csv_writer = csv.writer(tsvfile, delimiter='\t')

                # if file doesn't exist yet, right headers
                if not file_exists:
                    columns = [
                        'sub_num',
                        'block',
                        'episode',
                        'variation',
                        'movement type',
                        'movement type in words',
                        'ticrate(States/second)'
                    ]
                    csv_writer.writerow(columns)

                # translating movement
                def movement_translation(movement_type):
                    if movement_type == 0:
                        return 'normal'
                    elif movement_type == 1:
                        return 'inverted'
                    else:
                        return 'Error'

                row = [
                    sub_num,
                    (b+1),
                    (i+1),
                    variation,
                    movement_type,
                    movement_translation(movement_type),
                    ticrate_basic
                ]
                csv_writer.writerow(row)
                #print(f"Metadaten für Episode {i+1} von Block {b+1} gespeichert.")
    # buffer-episode: needed as the last episode isn't recorded
    game.new_episode()

    while not game.is_episode_finished():
        
            state = game.get_state()

            if state.number > 0:
                break
    
    

    

        
    # set keys to the original movement
    game.send_game_command("bind A +left")
    game.send_game_command("bind D +right")
    game.close()

    if b < (block_num-1):   # python starts indexing with 0, therefore minus 1, no break offering after last block
        win = visual.Window(
        color='black',
        size=[1920, 1080],
        fullscr=True)
        present_text(win, 
                image = os.path.join(img_dir, "instructions_break_offering.jpg"),
                break_offering = True,
                continue_key=continue_key,
                image_size=(1.8,1.6),  # Pass image size to present_text function
                )
    
        win.close()
    else:
        break


# window
screen_size = [1920, 1080]
win = visual.Window(
    color='black',
    size=[1920, 1080],
    fullscr=True)

present_text(window_instance=win,
             instructions = True,
                    instr_text='Vielen Dank für Ihre Teilnahme! \n' \
                        'Das Experiment ist nun abgeschlossen. \n' \
                        'Bitte verlassen Sie nun den Computer und geben der ' \
                        'Versuchsleitung Bescheid. Vielen Dank!'
            )

win.close()


