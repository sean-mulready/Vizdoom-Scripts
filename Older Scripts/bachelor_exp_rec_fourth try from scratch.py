# fourth try from scratch
# idea: Have a ptp.tsv-file where identifiers (number, age, handedness, glasses, gender/sex, ...) are stored
# .lmp-files with only the number, block and episode within the block in the filename
# other things: Storing the arrays for the probabilities (formely mu, need to rename it) and the movement_choice_arrays with the corresponding data (number, block, episode) in 
# maybe yet another tsv file but then need to think about how to write the script for replaying and extracting the data so the right probabilities and movement choices are reffered
# to the correct .lmp-files
# 
# 


# import important stuff
import vizdoom as vzd
import os 
import time
import csv
import numpy as np
from psychopy import core, visual, event

#img-dir for instructions

img_dir = os.getcwd() + "/exp_img/"


# Enter Subject Data
ptp_num = '4'           # ongoing numerizing as string
age = 23                # Age as Integer in years
gender = 'o'            # gender as string (m = male, f=female, nb = non-binary, o = other)
handedness = 'left'     # handedness as left or right (string)
glasses = False          # as boolean



# File path
filename = 'participants.tsv'



# Check if file exists
file_exists = os.path.isfile(filename)

# Function to check if ptp_num already exists in the file
def check_ptp_num_exists(filename, ptp_num):
    if file_exists:
        with open(filename, 'r') as tsvfile:
            csv_reader = csv.reader(tsvfile, delimiter='\t')
            for row in csv_reader:
                if row and row[0] == ptp_num:
                    return True
    return False

# Check if ptp_num is already in the file
if check_ptp_num_exists(filename, ptp_num):
    raise ValueError(f"Error: ptp_num {ptp_num} already exists in the file.")
else:
    # Check if file exists
    file_exists = os.path.isfile(filename)
    # Open the file in append mode
    with open(filename, 'a', newline='') as tsvfile:
        csv_writer = csv.writer(tsvfile, delimiter='\t')
    
        # If the file doesn't exist, write the header
        if not file_exists:
            columns = [
                'ptp_num',
                'age',
                'gender',
                'handedness',
                'glasses'
            ]
            csv_writer.writerow(columns)
        
        # Add the new row of data
        row = [
            ptp_num,
            age,
            gender,
            handedness,
            glasses
        ]
        
        csv_writer.writerow(row)

# Enter experiment configurations (episodes and ticrate = speed and time-resolution)
ep_basic = 30
ticrate_basic = 50 #number of tics('state-loops') per second, default is 35

# specify number of blocks, make sure it's even
block_num = 4
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




# Balance-vector and shuffle
# Balance-vector: either 0 or 1 decides in the end if left or right key is the better option

balance_vec = int(block_num/2)*[0,1]
np.random.shuffle(balance_vec)

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
    'greeting 3': {'image': os.path.join(img_dir, "instructions_greeting_3_bachelor.jpg"), 'image_size': (1.8,1.6)},
    'greeting 4': {'image': os.path.join(img_dir, "instructions_greeting_4_bachelor.jpg"), 'image_size': (1.8,1.6)}
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
    'begin_1': {'image': os.path.join(img_dir, "instructions_begin.jpg"), 'image_size': (1.8,1.6)},
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

# a blank black screen for the background. 
present_text(window_instance = win,
             instr_text= '',
             instructions = False
             )

# deciding the movement probabilities
# for each balance, there is an optimal key, so one key where
# the chance for the necessary movement is higher
# e.g.: If the balance is 0 there's a probability of .7, the movement is
# inverted if the monster spawns on the right side (optimal key A/left)
# and a probability of .7 that the movement is normal 
# if the monster spawns on the left side (optimal key A/left)
# so if the balance for a block of episodes is 0, the optimal key is A/left
# for every episode

def movement_probabilities(cacodemon_position, balance):
    prob_norm = 1
    prob_inv = 0
    if balance == 0:
        if cacodemon_position < (-9): #if the monster spawns on the right side
            prob_norm = 0.3
            prob_inv = 0.7
        elif cacodemon_position > 75: #if the monster spawns on the left side
            prob_norm = 0.7
            prob_inv = 0.3
    elif balance == 1:
        if cacodemon_position < (-9): #if the monster spawns on the right side
            prob_norm = 0.7
            prob_inv = 0.3
        elif cacodemon_position > 75: # if the monster spawns on the left side
            prob_norm = 0.3
            prob_inv = 0.7
    return np.random.choice([0,1], p = [prob_norm,prob_inv])

#implementing the array for storing the actual balances within experiment
balance_arr = np.full(block_num, np.nan, dtype = np.int32)

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
    balance = balance_vec.pop(0)

    # implementing the array for tracking the movement-choices 
    movement_choice_arr = np.full(ep_basic, np.nan, dtype = np.int32)

    # Loop through episodes
    for i in range(ep_basic):
        
        print("Episode #" + str(i + 1))
        #start the recording
        filename = f"{ptp_num}_b{b+1}_e{i+1}_basic_rec.lmp"
        game.new_episode(filename)


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

            movement_choice = movement_probabilities(cacodemon_position,balance)
            
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
    
    balance_arr[b] = balance

    #start the tsv file which stores ptp_num, block, episode, balance and concrete movement choice (maybe another column in words 'normal/inverted') 
    # Check if file exists
    file_exists = os.path.isfile('game_data.tsv')

    # Open the file in append mode
    with open('game_data.tsv', 'a', newline='') as tsvfile:
        csv_writer = csv.writer(tsvfile, delimiter='\t')
        
        # If the file doesn't exist, write the header
        if not file_exists:
            columns = [
                'ptp_num',
                'block',
                'episode',
                'balance',
                'movement choice',
                'movement choice in words',
                'Ticrate(States/second)'
            ]
            csv_writer.writerow(columns)
        
        # define word translation for movement_choice
        def movement_translation(movement_choice):
            if movement_choice == 0:
                output = 'normal'
            elif movement_choice == 1:
                output = 'inverted'
            else:
                output = 'Error'
                
            return output
        # Add the new row of data
        for i in range(ep_basic):
            row = [
                ptp_num,
                (b+1),
                (i+1),
                balance_arr[b],
                movement_choice_arr[i],
                movement_translation(movement_choice_arr[i]),
                ticrate_basic
                
                
            ]
        
            csv_writer.writerow(row)

        
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
                instructions=True,
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
                    instr_text='Vielen Dank für Ihre Teilnahme! \n' \
                        'Das Experiment ist nun abgeschlossen. \n' \
                        'Wenn Sie am Ende dazu aufgefordert werden, drücken Sie' \
                            ' ein letztes Mal die LEERTASTE, der Bildschirm wird daraufhin schwarz.'\
                                'Anschließend geben Sie der Versuchsleitung Bescheid. Vielen Dank \n\n'\
                                    'Drücken Sie bitte jetzt die LEERTASTE')

win.close()
        

