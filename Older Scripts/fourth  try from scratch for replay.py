# another try from scratch for replay, extracting and merging data 
# plan:
# - get a list of all the lmp-files
# - split name and convert ptp_num, block, episode, etc. from the lmp-file
# - compare the data with the corresponding lines from the game_data.tsv
# - replay the .lmp-files, extract the data and merge it with the game_data.tsv-lines
# - from big to small: first check the ptp_num, then block, then episode
# - ensure, that all data is checked within every loop to ensure every file is found and connected to the right data and not skipped

# import important stuff
import vizdoom as vzd
import os 
import csv
import time
import numpy as np
import re
# Function to extract numbers from filenames
def extract_numbers_from_filename(filename):
    pattern = r'_b|_e|_|\.'
    split_result = re.split(pattern, filename)
    return [int(part) for part in split_result if part.isdigit()]

# Get a list of all .lmp files
lmp_files = [f for f in os.listdir() if f.endswith('.lmp')]

# Function to check if a value is an integer
def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
        
# define function to check, if data is already in the final file

def load_existing_entries(file_path):
    existing_entries = set()  # To store the unique combination of ptp_num, block, episode
    if os.path.exists(file_path):
        with open(file_path, 'r') as final_file:
            final_reader = csv.reader(final_file, delimiter='\t')
            next(final_reader)  # Skip the header row if there is one
            for row in final_reader:
                if len(row) >= 3 and is_int(row[0]) and is_int(row[1]) and is_int(row[2]):
                    existing_entries.add((int(row[0]), int(row[1]), int(row[2])))
                else:
                    print(f"Skipping invalid row in TSV: {row}")
                    continue  # Skip invalid rows
    return existing_entries

# Load existing entries from the final file to avoid duplication
existing_entries = load_existing_entries('preprocessed_data_all.tsv')

# Open the TSV file and compare
with open('game_data.tsv', 'r') as tsvfile:
    tsv_reader = csv.reader(tsvfile, delimiter='\t')
    # Skip the header row
    next(tsv_reader)
    # Loop through each row in the TSV file
    for row in tsv_reader:
        # Extract the first 3 elements of the row and convert them to integers
        tsv_numbers = tuple([int(row[0]), int(row[1]), int(row[2])])

        # Check if this combination is already processed
        if tsv_numbers in existing_entries:
            print(f"Skipping already processed file for ptp_num: {tsv_numbers[0]}, block: {tsv_numbers[1]}, episode: {tsv_numbers[2]}")
            continue  # Skip this row if it was already processed
        
        # Loop over each .lmp file and its associated extracted number list
        for file in lmp_files:
            file_numbers = extract_numbers_from_filename(file)

            file_tuple = tuple(file_numbers)
            
            # Compare the first 3 elements of the extracted list with the row in TSV
            if tsv_numbers != file_tuple:
                pass
            elif tsv_numbers == file_tuple:
                #here I need to insert the code to replay, write it in a tsv and use the row[i]-data in each state

                ptp_num = row[0]
                block_num = row[1]
                episode = row[2]
                balance = row[3]
                movement_choice = row[4]
                movement_choice_words = row[5]
                ticrate_basic = int(row[6])

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
                
                #Start the merging file
                # Check if file exists
                #file_exists = os.path.isfile('preprocessed_data_all.tsv')

                # Open a temp-file to store ingame data and fuse it with columns at the end 
                with open('temp.tsv', 'w', newline='') as tsvfile:
                    csv_writer = csv.writer(tsvfile, delimiter='\t')
                    
                    # If the file doesn't exist, write the header
                #if not file_exists:  #indent removed because hashing out
                    columns = ["Participant",
                                "Block",
                                "Episode",
                                "State",
                                "Balance",
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
                        
                        for object_id in unique_object_ids:
                            if object_id not in object_id_to_column_index:
                                object_id_to_column_index[object_id] = len(columns)
                                columns.extend([f"{object_id}_name",
                                                f"{object_id}_x", 
                                                f"{object_id}_y", 
                                                f"{object_id}_z", 
                                                f"{object_id}_angle"])
                        
                        # Collect data for each time step within the episode
                        row = [ptp_num,
                            block_num,
                            episode, 
                            state.number,
                            balance,
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
                    #row_end = ([""]*len(columns))
                    #row_end [0:5]= ["Total Reward:", game.get_total_reward(),
                                            #"fps:", ((state.number)/(time.time()-start_time))
                                            #]
                    #csv_writer.writerow(row_end)

                    #overwrite original csv with modified first row
                    with open('column_data.tsv','w',newline='') as output_file:
                            csv_writer=csv.writer(output_file, delimiter="\t")
                            csv_writer.writerow(columns)                   

                print("Episode finished!")
                print("Total reward:", game.get_total_reward())
                print("Time:", (time.time() - start_time))
                print("************************")
                    

                game.close()

                # Append the contents from temp_file and column file to final file
                with open('column_data.tsv','r') as column_tsv:
                    column_tsv_reader = csv.reader(column_tsv)
                    with open('temp.tsv', 'r') as temp_tsv:
                        temp_csv_reader = csv.reader(temp_tsv)
                        with open('preprocessed_data_all.tsv', 'a', newline='') as final_file:
                            csv_writer = csv.writer(final_file)
                            for row in column_tsv_reader:
                                csv_writer.writerow(row)
                            for row in temp_csv_reader:
                                csv_writer.writerow(row)

            else:
                print('Error')


os.remove('temp.tsv')
os.remove('column_data.tsv')
