# Import important stuff
import vizdoom as vzd
import os
import csv
import time
import re

target_name = "Bullseye"  # for later identification of the right object data

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

# Columns to write if the file does not exist
checking_columns = ['Subject', 'Block', 'Episode']

# Check if the file exists, if not, create it with header
if not os.path.exists('checking_file.tsv'):
    with open('checking_file.tsv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(checking_columns)

# Define function to check if data is already in the final file
def load_existing_entries(file_path):
    existing_entries = set()  # To store the unique combination of sub_num, block, episode
    with open(file_path, 'r') as final_file:
        final_reader = csv.reader(final_file, delimiter='\t')
        next(final_reader, None)  # Skip the header row
        for row in final_reader:
            if len(row) >= 3 and is_int(row[0]) and is_int(row[1]) and is_int(row[2]):
                existing_entries.add((int(row[0]), int(row[1]), int(row[2])))
            else:
                print(f"Skipping invalid row in TSV: {row}")
    return existing_entries

# Load existing entries from the checking file to avoid duplication
existing_entries = load_existing_entries('checking_file.tsv')

# Open the TSV file and compare
with open('game_data.tsv', 'r') as tsvfile:
    tsv_reader = csv.reader(tsvfile, delimiter='\t')
    next(tsv_reader)  # Skip the header row
    
    for row in tsv_reader:
        tsv_numbers = tuple([int(row[0]), int(row[1]), int(row[2])])

        if tsv_numbers in existing_entries:
            print(f"Skipping already processed file for sub_num: {tsv_numbers[0]}, block: {tsv_numbers[1]}, episode: {tsv_numbers[2]}")
            continue

        for file in lmp_files:
            file_numbers = extract_numbers_from_filename(file)
            file_tuple = tuple(file_numbers)

            if tsv_numbers != file_tuple:
                continue

            # Matching file found, process it
            sub_num = row[0]
            block_num = row[1]
            episode = row[2]
            variation = row[3]
            movement_type = row[4]
            movement_type_words = row[5]
            ticrate_basic = int(row[6])

            sub_folder = f"sub_{sub_num}"
            os.makedirs(sub_folder, exist_ok=True)

            block_file = os.path.join(sub_folder, f"block_{block_num}.tsv")
            
            # Write the header only if the block file doesn't exist
            if not os.path.exists(block_file):
                columns = [
                    "Subject", "Block", "Variation", "Episode", "Movement", "State", "Tic", "Time",  
                    "Action", "Player_pos", 
                    "Reward", "Cumulative_Reward", "Target_name", "Target_pos"
                ]
                with open(block_file, 'w', newline='') as block_tsv:
                    csv_writer = csv.writer(block_tsv, delimiter="\t")
                    csv_writer.writerow(columns)

            # Setup and init game
            game = vzd.DoomGame()
            game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini")
            game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/experiment.cfg")
            game.set_window_visible(False)
            game.set_screen_resolution(vzd.ScreenResolution.RES_1280X960)
            game.set_render_hud(False)
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
                else:
                    return None

            def find_object_data(object_list, *names):
                for o in object_list:
                    if o.name in names:
                        return o
                return None


            game.replay_episode(file)
            cumulative_reward = 0
            start_time = time.time()

            with open('temp_file.tsv', 'w', newline='') as temp_file:
                csv_writer = csv.writer(temp_file, delimiter='\t')

                while not game.is_episode_finished():
                    state = game.get_state()
                    game.advance_action()
                    last_action = game.get_last_action()
                    reward = game.get_last_reward()
                    last_action_trnsl = translate_action(last_action)
                    cumulative_reward += reward
                    current_time = game.get_episode_time() * (1 / ticrate_basic)
                    row_out = [
                        sub_num, 
                        block_num,
                        variation, 
                        episode,
                        movement_type, 
                        state.number, 
                        game.get_episode_time(), 
                        current_time,
                        last_action_trnsl,
                        game.get_game_variable(vzd.GameVariable.POSITION_Y),
                        reward, 
                        cumulative_reward
                    ]

                    target = find_object_data(state.objects, "Bullseye", "Dead")
                    if target:
                        row_out.extend([target.name, target.position_y])
                    else:
                        row_out.extend([None, None])

                    csv_writer.writerow(row_out)
                    time.sleep(0.001)

            print(f"Episode finished for sub_num {sub_num}, block {block_num}, episode {episode}")
            print(f"Total reward: {game.get_total_reward()}")
            print(f"Time: {time.time() - start_time}")
            print("************************")

            game.close()

            # Append episode to checking file
            with open('checking_file.tsv','a',newline='') as checking_file:
                csv_writer = csv.writer(checking_file, delimiter='\t')
                csv_writer.writerow([sub_num, block_num, episode])

            # Append data to final block file without headers
            with open('temp_file.tsv', 'r') as temp_tsv:
                temp_csv_reader = csv.reader(temp_tsv, delimiter='\t')
                with open(block_file, 'a', newline='') as final_file:
                    csv_writer = csv.writer(final_file, delimiter='\t')
                    for row in temp_csv_reader:
                        csv_writer.writerow(row)

            os.remove('temp_file.tsv')
