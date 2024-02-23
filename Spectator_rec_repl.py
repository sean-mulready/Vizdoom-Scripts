# Script to record,replay and save data of gameplay in Spectator Mode in one run
# UNDER CONSTRUCTION
# for some reason, last episode isn't recorded -> current workaround: buffer-episode
# What Script does so far: according to an for now specified parameter mu probabilities
# for movement are assigned in relation to the side on which the monster spawns.
# Episodes can be played and only Data gathered here is what movement is used
# after playing the defined number of episodes, without having a window visible, the 
# recorded episodes are replayed, data is collected and stored as CSV for further
# processing, before the recorded .lmp-files are deleted to save space

# Update Feb/09/24: mu_vec is now created, blockwise implementation
# and processing afterwards, also started to implement psychopy
# (caution: Psychopy on Python 3.10 ist only installable and working
# in a virtual env and wx Python installed from conda-forge (https://anaconda.org/conda-forge/wxpython), 
# as well as getting the LineBreak.txt and replacing linebreak.py 
# from https://github.com/peircej/psychopy/tree/release/psychopy/tools )


# Update Feb/15/24 : Psychopy instruction screens and black background for episodes implemented

# Update Feb/23/24 : 
# -Instructions are now implemented as .jpg, as there is no single-word-formatting in the text_stims 
# - more Subject-data 
# - began to rearrange columns


# WHAT IS COMING: 
# - more re-arranging the whole dataframe with a more useful order of columns 
# - changing rewards so that if choosing the wrong movement-key
#   (further away) the reward is < -1 




# import important stuff
import vizdoom as vzd
import os 
import csv
import time
import numpy as np
import pandas as pd
from psychopy import core, visual, event


#img-dir for instructions

img_dir = os.getcwd() + "/exp_img/"

# Enter Subject Data
sub_num = '1'           # ongoing numerizing as string
sub_id = 'HECO91M'      # Construct ID as : First 2 letters of birth-location, first 2 letters of mother's first name, last two digits of birth-year, gender in one letter
age = 32                # Age as Integer
gender = 'm'            # gender as string (m = male, f=female, nb = non-binary, o = other)
glasses = True          # as boolean


# Enter experiment configurations (episodes and ticrate = speed and time-resolution)
episodes = 3
ticrate = 50 #number of tics('state-loops') per second, default is 35

# specify number of blocks, make sure it's even
block_num = 2 
if block_num % 2 == 0:
    None
elif block_num %2 != 0:
    block_num = (block_num+1)

# psychopy setup for interface

# window
screen_size = [1920, 1080]
win = visual.Window(
    color='black',
    size=[1920, 1080],
    fullscr=True)

# key to go forward

continue_key = 'space'



# instructions before experiment

instructions = {
    'instructions_1': {'image': os.path.join(img_dir, "instructions1.jpg"), 'image_size': (1.8,1.6)},
    'instructions_2': {'image': os.path.join(img_dir, "instructions2.jpg"), 'image_size': (1.8,1.6)},
    'instructions_3': {'image': os.path.join(img_dir, "instructions3.jpg"), 'image_size': (1.8,1.6)},
    'instructions_4': {'image': os.path.join(img_dir, "instructions4.jpg"), 'image_size': (1.8,1.6)},
    'instructions_5': {'image': os.path.join(img_dir, "instructions5.jpg"), 'image_size': (1.8,1.6)},
    'instructions_6': {'text': f'Ihr Ziel ist es, das Monster so schnell wie möglich zu erschießen. Dazu werden Sie {block_num} Blöcke mit je {episodes} Durchgängen spielen. Sie haben nach jedem Block die Möglichkeit, eine kurze Pause einzulegen wenn Sie möchten, da Sie jeden Block selbst starten. \n\n Bitte LEERTASTE drücken, um fortzufahren'},
    'instructions_7': {'image': os.path.join(img_dir, "instructions7.jpg"), 'image_size': (1.8,1.6)}

}




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



#start with instructions
# Iterate over instructions
# Iterate over instructions
for instruction_key, instruction_data in instructions.items():
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

# a blank black screen for the background. Will close after replay and data-processing is finished
present_text(window_instance = win,
             instr_text= '',
             instructions = False
             )




    # function for choosing if normal or inverted movement in relation to 
    # the parameter mu and the side on which the Cacodemon spawns
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
    game.set_ticrate(ticrate)

    # Initialize the game
    game.init()

    # RECORDING



    # using up elements of shuffled vector
    mu = mu_vec.pop(0)
    # implementing the array for tracking the movement-choices 
    movement_choice_arr = np.full(episodes, np.nan, dtype = np.int32)
    
    # Loop through episodes
    for i in range(episodes):
        
        print("Episode #" + str(i + 1))
        #start the recording
        game.new_episode(f"{sub_id}_block{b+1}_episode{i+1}_rec.lmp")

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
    
    
    game.close()
    

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

    

# REPLAY AND SAVING AS CSV

game = vzd.DoomGame()
for b in range(block_num):

    # where to get the .ini-file from
    game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini") 

    # need to reload/respecify the essentials
    game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/basic.cfg")
    # no window needed for replaying and gathering data, saves time
    game.set_window_visible(False)
    # should actually work in every mode but seems safe to use the same as when recording
    game.set_mode(vzd.Mode.ASYNC_SPECTATOR)
    game.init()

    # Define a translation function for the last action
    def translate_action(last_action):
        
        last_action_trnsl = "NA"
        #scenario basic         
        if last_action == [1.0,0.0,0.0]:
            last_action_trnsl = "MOVE_LEFT"
        elif last_action == [0.0,1.0,0.0]:
            last_action_trnsl = "MOVE_RIGHT"
        elif last_action == [0.0,0.0,1.0]:
            last_action_trnsl = "ATTACK"
    
        return last_action_trnsl

        #function to return objects info
    def find_object_data(object_list,object_id):
        for o in object_list:
            if o.id == object_id:
                return o

    # create a temporary csv file
    temp_file = "temp.csv"

    # Open a single CSV file to store all episode data
    output_path = os.getcwd() + f'/data/sub-{sub_num}'

    if not os.path.exists(output_path):
        os.makedirs(output_path)


    episode_filename = f"{output_path}/{sub_num}_block_{b+1}_game_dataframe.csv"
    with open(temp_file, 'w', newline='') as temp_csv: 
        csv_writer = csv.writer(temp_csv)
        columns = ["Sub_num",
                   "Sub_ID",
                   "Age",
                   "Gender",
                   "Glasses",
                   "Episode",
                   "State",
                   "Mu",
                   "Movement",
                   "Tic", 
                   "Health", 
                   "Ammo", 
                   "x_pos", 
                   "y_pos", 
                   "z_pos", 
                   "angle/orientation", 
                   "Action", 
                   "Reward", 
                   "Cumulative_Reward", 
                   "Time"]
        



        #Use a set to keep track of uniqueobject IDs
        unique_object_ids = set()

            

            # create a dictionary to store mapping between object ID and column index
        object_id_to_column_index = {}






        # Loop through episodes
        for i in range(episodes):
            
            # tell to replay 
            game.replay_episode(f"{sub_id}_block{b+1}_episode{i+1}_rec.lmp")
            cumulative_reward = 0  # Initialize cumulative reward
            start_time = time.time()  # Record the start time
            
            
            
            

            while not game.is_episode_finished():

                
                state = game.get_state()
                game.advance_action()
                last_action = game.get_last_action()
                reward = game.get_last_reward()
                last_action_trnsl = translate_action(last_action)  
                
                cumulative_reward += reward  # Update cumulative reward
                current_time = game.get_episode_time()*(1/ticrate)
                
                object_ids = []
                for o in state.objects:
                    if o.name != "DoomPlayer":
                        object_ids.append(o.id)
                unique_object_ids.update(object_ids)

                for object_id in unique_object_ids:
                        if object_id not in object_id_to_column_index:
                            object_id_to_column_index[object_id] = len(columns)
                            columns.extend([f"{object_id}_name",
                                            f"{object_id}_x", 
                                            f"{object_id}_y", 
                                            f"{object_id}_z", 
                                            f"{object_id}_angle"])
                
                # Collect data for each time step within the episode
                row = [sub_num,
                       sub_id,
                       age,
                       gender,
                       glasses,
                       i + 1, 
                       state.number,
                       mu_arr[b],
                       movement_choice_arr[i],
                       game.get_episode_time(), 
                       game.get_game_variable(vzd.GameVariable.HEALTH),
                       game.get_game_variable(vzd.GameVariable.AMMO2), 
                       game.get_game_variable(vzd.GameVariable.POSITION_X),
                       game.get_game_variable(vzd.GameVariable.POSITION_Y), 
                       game.get_game_variable(vzd.GameVariable.POSITION_Z),
                       game.get_game_variable(vzd.GameVariable.ANGLE), 
                       last_action_trnsl, 
                       reward, 
                       cumulative_reward, 
                       current_time
                        
                        ]
                
                for object_id in unique_object_ids:
                    object_data = find_object_data(state.objects,object_id)
                    if object_data is not None:
                        row.extend([
                                object_data.name,
                                object_data.position_x, 
                                object_data.position_y, 
                                object_data.position_z, 
                                object_data.angle])
                    else:
                        row.extend([None, None, None, None, None])
                        
                csv_writer.writerow(row)

                
                
           
             #change the addition according to skipped Tics in the Beginning (first number in Tic-Column)
            row_end = ([""]*len(columns))
            row_end [0:5]= ["Total Reward:", game.get_total_reward(),
                                    "fps:", ((state.number)/(time.time()-start_time))
                                    ]
            csv_writer.writerow(row_end)

            
        
                

        #overwrite original csv with modified first row
        with open(episode_filename,'w',newline='') as output_file:
                csv_writer=csv.writer(output_file)
                csv_writer.writerow(columns)

            

        print("Episode finished!")
        print("Total reward:", game.get_total_reward())
        print("Time:", (time.time() - start_time))
        print("************************")
        

    game.close()

    # Append the contents from temp_file to episode_filename
    with open(episode_filename, 'a', newline='') as final_file:
        with open(temp_file, 'r') as temp_csv:
            temp_csv_reader = csv.reader(temp_csv)
            for row in temp_csv_reader:
                csv_writer = csv.writer(final_file)
                csv_writer.writerow(row)

    # remove the temporary csv and the recording-files after the file with 
    # the modified columns has been written
    os.remove(temp_file)
    for i in range(episodes):
        os.remove(f"{sub_id}_block{b+1}_episode{i+1}_rec.lmp")