# import important stuff
import vizdoom as vzd
import os 
import csv
import time
import numpy as np


# Enter Subject Data
sub_num = '1'           # ongoing numerizing as string
sub_id = 'HECO91M'      # Construct ID as : First 2 letters of birth-location, first 2 letters of mother's first name, last two digits of birth-year, gender in one letter
age = 32                # Age as Integer
gender = 'm'            # gender as string (m = male, f=female, nb = non-binary, o = other)
glasses = True          # as boolean


episodes = 2
ticrate = 30
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
game.set_render_hud(True)
game.set_mode(vzd.Mode.ASYNC_SPECTATOR)
game.set_ticrate(ticrate)

# Initialize the game
game.init()


# RECORDING

for i in range(episodes):
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
    


# REPLAY AND SAVING AS CSV

game = vzd.DoomGame()

# where to get the .ini-file from
game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini") 

# need to reload/respecify the essentials
game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/my_way_home.cfg")
# no window needed for replaying and gathering data, saves time
game.set_window_visible(False)
# Enables information about all objects present in the current episode/level.
game.set_objects_info_enabled(True)

# Enables information about all sectors (map layout).
game.set_sectors_info_enabled(True)
# should actually work in every mode but seems safe to use the same as when recording
game.set_mode(vzd.Mode.ASYNC_SPECTATOR)
game.init()

# Define a translation function for the last action
def translate_action(last_action):
    action_space = np.identity(5)
    last_action_trnsl = "NA"
    #scenario basic         
    if np.array_equal(last_action, action_space[0]):
        last_action_trnsl = "TURN_LEFT"
    elif np.array_equal(last_action, action_space[1]):
        last_action_trnsl = "TURN_RIGHT"
    elif np.array_equal(last_action, action_space[2]):
        last_action_trnsl = "MOVE_FORWARD"
    elif np.array_equal(last_action, action_space[3]):
        last_action_trnsl = "MOVE_LEFT"
    elif np.array_equal(last_action, action_space[4]):
        last_action_trnsl = "MOVE_RIGHT"
    return last_action_trnsl

        #function to return objects info
def find_object_data(object_list,object_id):
    for o in object_list:
        if o.id == object_id:
            return o
    return None


# create a temporary csv file
temp_file = "temp.csv"

# Open a single CSV file to store all episode data
output_path = os.getcwd() + f'/data/sub-{sub_num}'

if not os.path.exists(output_path):
    os.makedirs(output_path)


episode_filename = f"{output_path}/{sub_num}_my_way_home_game_dataframe.csv"
with open(temp_file, 'w', newline='') as temp_csv: 
    csv_writer = csv.writer(temp_csv)
    columns = ["Sub_num",
                "Sub_ID",
                "Age",
                "Gender",
                "Glasses",
                "Episode",
                "State",
                "Tic", 
                "Time",
                "Action",
                "x_pos", 
                "y_pos", 
                "z_pos", 
                "angle/orientation",  
                "Reward", 
                "Cumulative_Reward",
                "Health", 
                "Ammo"]
    



    #Use a set to keep track of uniqueobject IDs. Set means uniqueness is enforced
    unique_object_ids = set()

        

    # create a dictionary to store mapping between object ID and column index
    object_id_to_column_index = {}

    # Loop through episodes
    for i in range(episodes):
        
        # tell to replay 
        game.replay_episode(f"{sub_id}_e{i+1}_my_way_home_rec.lmp")
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
            
            #object_ids = []  # probably uneccessary
            for o in state.objects:
                if o.name != "DoomPlayer":
                    unique_object_ids.add(o.id)
                    #object_ids.append(o.id) #prob uneccessary
            #unique_object_ids.update(object_ids) #prob uneccessary

            # this code defines the current column-number as the specific value for the key of the object_id
            # in the referred dictionary (id to column index) to then add to that so 
            # that for each new object 5 new columns are added
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
                    game.get_episode_time(),
                    current_time,
                    last_action_trnsl, 
                    game.get_game_variable(vzd.GameVariable.POSITION_X),
                    game.get_game_variable(vzd.GameVariable.POSITION_Y), 
                    game.get_game_variable(vzd.GameVariable.POSITION_Z),
                    game.get_game_variable(vzd.GameVariable.ANGLE),  
                    reward, 
                    cumulative_reward, 
                    game.get_game_variable(vzd.GameVariable.HEALTH),
                    game.get_game_variable(vzd.GameVariable.AMMO2)
                    
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
with open(temp_file, 'r') as temp_csv:
    temp_csv_reader = csv.reader(temp_csv)
    with open(episode_filename, 'a', newline='') as final_file:
        csv_writer = csv.writer(final_file)
        for row in temp_csv_reader:
            csv_writer.writerow(row)

# remove the temporary csv and the recording-files after the file with 
# the modified columns has been written
os.remove(temp_file)
for i in range(episodes):
    os.remove(f"{sub_id}_e{i+1}_my_way_home_rec.lmp")
