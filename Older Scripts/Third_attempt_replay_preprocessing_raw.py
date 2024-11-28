# this is yet the third attempt to get the data replayed, extracted and sorted maybe afterwards
# idea: Get all the Sub_data in the filename, then extract that data for the csv
# sort the rest in an R-Script

# Testing again -.-

# so this is just the replay and csv-conversion for the basic scenario which is used in my experiment

# import important stuff
import vizdoom as vzd
import os 
import csv
import time
import numpy as np
import pickle
from collections import defaultdict #to sort and group data


# Function to extract block and episode numbers from filenames
def extract_block_and_episode(filename):
    parts = filename.split('_')
    block_part = parts[8]  # e.g., 'b1' from '1_Testsub1_b1_e1_basic_rec.lmp'
    episode_part = parts[9]  # e.g., 'e1' from '1_Testsub1_b1_e1_basic_rec.lmp'
    
    # Extract block number and episode number
    block_num = int(block_part[1:])
    episode_num = int(episode_part[1:])
    
    return block_num, episode_num


lmp_files = [f for f in os.listdir() if f.endswith('.lmp')]

# Step 2: Group files by the first character (sub_num) before the first underscore
file_groups = defaultdict(list)
for file in lmp_files:
    file_groups[file[0]].append(file)

# Step 3: Sort the files within each group by block and episode numbers
sorted_file_groups = {}
for x, files in file_groups.items():
    # Sort files by block number and then by episode number
    sorted_files = sorted(files, key=extract_block_and_episode)
    sorted_file_groups[x] = sorted_files

# Step 4: Sort the file groups by sub_num (keys)
sorted_file_groups = dict(sorted(sorted_file_groups.items()))

# Print sorted file groups
print(sorted_file_groups)



######### REPLAY BASIC AND SAVING AS CSV ###########################
####################################################################
####################################################################
# Step 3: Process each batch (grouped by sub_num)
for sub, files in sorted_file_groups.items():

    for file in files:

        sub_data = file.split('_')
        
    
        age = sub_data[2]
        sub_num = sub_data[0]
        sub_id =  sub_data[1]
        gender = sub_data[3]
        glasses = sub_data[4]
        ep_basic = sub_data[9]
        block_num = sub_data[8]
        ticrate_basic = int(sub_data[5])
        mu = sub_data[6] # mu in filename!
        movement_choice = sub_data[7]  # Movement_choice in filename!
        
        game = vzd.DoomGame()

        # where to get the .ini-file from
        game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini") 

        # need to reload/respecify the essentials
        game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/experiment.cfg")
        # no window needed for replaying and gathering data, saves time
        game.set_window_visible(False)
        # Enables information about all objects present in the current episode/level.
        game.set_objects_info_enabled(True)

        # Enables information about all sectors (map layout).
        game.set_sectors_info_enabled(True)
        # should actually work in every mode but seems safe to use the same as when recording
        game.set_mode(vzd.Mode.ASYNC_SPECTATOR)
        game.set_ticrate(ticrate_basic)
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
            return None

        # create a temporary csv file
        temp_file = "temp.csv"

        # Open a single CSV file to store all episode data
        output_path = os.getcwd() + f'/data/{sub_num}'+ time.strftime("%Y%m%d")

        if not os.path.exists(output_path):
            os.makedirs(output_path)


        sub_filename = f"{output_path}/{sub_num}_basic_game_dataframe.csv"
        # Open the CSV file once per subject
        with open(sub_filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile) 
            
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






            
                
            # tell to replay 
            game.replay_episode(file)
            cumulative_reward = 0  # Initialize cumulative reward
            start_time = time.time()  # Record the start time
            
            
            
            

            while not game.is_episode_finished():

                
                state = game.get_state()
                game.advance_action()
                last_action = game.get_last_action()
                reward = game.get_last_reward()
                last_action_trnsl = translate_action(last_action)  
                
                cumulative_reward += reward  # Update cumulative reward
                current_time = game.get_episode_time()*(1/ticrate_basic)
                
                object_ids = []
                for o in state.objects:
                    if o.name != "DoomPlayer":
                        unique_object_ids.add(o.id)
                        #object_ids.append(o.id)
                #unique_object_ids.update(object_ids)

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
                    ep_basic, 
                    state.number,
                    mu,
                    movement_choice,
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

            
        
                

        
                

        print("Episode finished!")
        print("Total reward:", game.get_total_reward())
        print("Time:", (time.time() - start_time))
        print("************************")
            

    game.close()

    # remove the temporary csv and the recording-files after the file with 
    # the modified columns has been written
    os.remove(temp_file)
    #for i in range(ep_basic):
        #os.remove(f"{sub_id}_b{b+1}_e{i+1}_basic_rec.lmp")




