# This script
# - extracts Data from the Subject file in which information, that the lmp-files
# didn't store is saved to then bring it together 
# when the lmp-files are replayed and data is extracted
# - checks, if files have already been processed and skips them 
# - replays the lmp-files, extracts game data, saves it togehter with the data
# that has been stored in the sub-file, like the variation per block and the movement-choice
# per episode
# - it stores the data blockwise in folders which are created for every Subject
# Need to clean the code: look for unnecessary things




# import important stuff
import vizdoom as vzd
import os 
import csv
import time
import re

# Function to extract numbers from filenames
def extract_numbers_from_filename(filename):
    pattern = r'_b|_e|_|\.'  
    split_result = re.split(pattern, filename)
    return [int(part) for part in split_result if part.isdigit()]

# Function to check if a value is an integer
def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

# Get a list of all .lmp files
lmp_files = [f for f in os.listdir() if f.endswith('.lmp')]

# define function to check, if data is already in the final file
def load_existing_entries(file_path):
    existing_entries = set()  # To store the unique combination of sub_num, block, episode
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

# Columns to write if the file does not exist
checking_columns = ['Subject', 'Block', 'Episode']

# Check if the file exists
if os.path.exists('checking_file.tsv'):
    pass  # Skip if the file exists
else:
    # Create and write to the file if it doesn't exist
    with open('checking_file.tsv', 'w', newline='') as checking_tsv:
        checking_tsv_writer = csv.writer(checking_tsv, delimiter='\t')
        checking_tsv_writer.writerow(checking_columns)

        
# Load existing entries from the final file to avoid duplication
existing_entries = load_existing_entries('checking_file.tsv')

# Open the TSV file and compare
with open('game_data.tsv', 'r') as tsvfile:
    tsv_reader = csv.reader(tsvfile, delimiter='\t')
    next(tsv_reader)  # Skip the header row
    
    for row in tsv_reader:
        # Extract the first 3 elements of the row and convert them to integers
        tsv_numbers = tuple([int(row[0]), int(row[1]), int(row[2])])

        # Skip already processed entries
        if tsv_numbers in existing_entries:
            print(f"Skipping already processed file for sub_num: {tsv_numbers[0]}, block: {tsv_numbers[1]}, episode: {tsv_numbers[2]}")
            continue
        # Loop over each .lmp file and its associated extracted number list
        for file in lmp_files:
            file_numbers = extract_numbers_from_filename(file)

            file_tuple = tuple(file_numbers)
            
            # Compare the first 3 elements of the extracted list with the row in TSV
            if tsv_numbers != file_tuple:
                pass
            elif tsv_numbers == file_tuple:
                #here I need to insert the code to replay, write it in a tsv and use the row[i]-data in each state

                sub_num = row[0]
                block_num = row[1]
                episode = row[2]
                variation = row[3]
                movement_type = row[4]
                movement_type_words = row[5]
                ticrate_basic = int(row[6])

                # Create a folder for each sub_num if it doesn't exist
                sub_folder = f"sub_{sub_num}"
                if not os.path.exists(sub_folder):
                    os.makedirs(sub_folder)

                

                # Check if the block file exists, if not write headers
                #file_exists = os.path.isfile(block_file)
                with open("temp_file.tsv", 'w', newline='') as temp_file:
                    csv_writer = csv.writer(temp_file, delimiter='\t')
                    
                    # If the file doesn't exist, write the header
                    #if not file_exists:
                    columns = [
                            "Subject", "Block", "Episode", "State", "Variation", "Movement", "Tic", 
                            "Time", "Action", "x_pos", "y_pos", "z_pos", "angle/orientation", 
                            "Reward", "Cumulative_Reward", "Health", "Ammo"
                        ]

                    unique_object_ids = set()

                        

                    # create a dictionary to store mapping between object ID and column index
                    object_id_to_column_index = {}


                    

                    # Start the VizDoom game
                    game = vzd.DoomGame()
                    game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini")
                    game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/experiment.cfg")
                    game.set_window_visible(False)
                    game.set_objects_info_enabled(True)
                    game.set_sectors_info_enabled(True)
                    game.set_mode(vzd.Mode.ASYNC_SPECTATOR)
                    game.set_ticrate(ticrate_basic)
                    game.init()

                    def translate_action(last_action):
                        if last_action == [1.0, 0.0, 0.0]:
                            return "MOVE_LEFT"
                        elif last_action == [0.0, 1.0, 0.0]:
                            return "MOVE_RIGHT"
                        elif last_action == [0.0, 0.0, 1.0]:
                            return "ATTACK"
                        return "NA"

                    def find_object_data(object_list, object_id):
                        for o in object_list:
                            if o.id == object_id:
                                return o
                        return None

                    game.replay_episode(file)
                    cumulative_reward = 0  # Initialize cumulative reward
                    start_time = time.time()

                    while not game.is_episode_finished():
                        state = game.get_state()
                        game.advance_action()
                        last_action = game.get_last_action()
                        reward = game.get_last_reward()
                        last_action_trnsl = translate_action(last_action)

                        cumulative_reward += reward
                        current_time = game.get_episode_time() * (1 / ticrate_basic)
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

                        row = [
                            sub_num, 
                            block_num, 
                            episode, 
                            state.number, 
                            variation, 
                            movement_type,
                            game.get_episode_time(), 
                            current_time, last_action_trnsl,
                            game.get_game_variable(vzd.GameVariable.POSITION_X),
                            game.get_game_variable(vzd.GameVariable.POSITION_Y),
                            game.get_game_variable(vzd.GameVariable.POSITION_Z),
                            game.get_game_variable(vzd.GameVariable.ANGLE), 
                            reward, cumulative_reward,
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
                    
                    # write the header lines aka the column names
                    with open('column_data.tsv','w',newline='') as header_file:
                            csv_writer=csv.writer(header_file, delimiter="\t")
                            csv_writer.writerow(columns)  

                print(f"Episode finished for sub_num {sub_num}, block {block_num}, episode {episode}")
                print(f"Total reward: {game.get_total_reward()}")
                print(f"Time: {time.time() - start_time}")
                print("************************")

                checking_rows = [sub_num,block_num,episode]
                with open('checking_file.tsv','a',newline='') as checking_file:
                    csv_writer=csv.writer(checking_file, delimiter ='\t')
                    csv_writer.writerow(checking_rows)

                game.close()

                # Append the contents from temp_file and column file to the final block file for the sub_num
                with open('column_data.tsv','r') as column_tsv:
                    column_tsv_reader = csv.reader(column_tsv)
                    with open('temp_file.tsv', 'r') as temp_tsv:
                        temp_csv_reader = csv.reader(temp_tsv)
                        # Create the final block file in the sub_num folder
                        block_file = os.path.join(sub_folder, f"block_{block_num}.tsv")
                        
                        # Open the final file in append mode to avoid overwriting
                        with open(block_file, 'a', newline='') as final_file:
                            csv_writer = csv.writer(final_file)

                            # First write the column headers
                            for row in column_tsv_reader:
                                csv_writer.writerow(row)

                            # Then write the data from the temp file
                            for row in temp_csv_reader:
                                csv_writer.writerow(row)

                # Remove the temporary files after they have been appended to the final file
                os.remove('temp_file.tsv')
                os.remove('column_data.tsv')
