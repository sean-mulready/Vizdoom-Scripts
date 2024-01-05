

from __future__ import print_function
import vizdoom as vzd
import csv
import time
import os
import pandas as pd 





# Enter Subject Data
sub_id = "01"

game = vzd.DoomGame()

# where to get the .ini-file from
game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini")

# Choose the scenario config file you wish to watch.
# Don't load two configs because the second will overwrite the first one.
# Multiple config files are okay, but combining these ones doesn't make much sense.

game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/basic.cfg")
#game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/deadly_corridor.cfg")
#game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/take_cover.cfg")

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
game.set_render_hud(False)

# Enables spectator mode so you can play, but your agent is supposed to watch, not you.
game.set_window_visible(True)
game.set_mode(vzd.Mode.SPECTATOR)
game.init()


# Specify how many Episodes 
episodes = 3

# Define a translation function for the last action
def translate_action(last_action):
    
    
    last_action_trnsl = "NA"

    #scenario deadly corridor
    last_action_trnsl = "NA"
    if last_action == [1.0,0.0,0.0,0.0,0.0,0.0,0.0]:
        last_action_trnsl = "MOVE_LEFT"
    elif last_action == [0.0,1.0,0.0,0.0,0.0,0.0,0.0]:
        last_action_trnsl = "MOVE_RIGHT"
    elif last_action == [0.0,0.0,1.0,0.0,0.0,0.0,0.0]:
        last_action_trnsl = "ATTACK"
    elif last_action == [0.0,0.0,0.0,1.0,0.0,0.0,0.0]:
        last_action_trnsl = "MOVE_FORWARD"
    elif last_action == [0.0,0.0,0.0,0.0,1.0,0.0,0.0]:
        last_action_trnsl = "MOVE_BACKWARD"
    elif last_action == [0.0,0.0,0.0,0.0,0.0,1.0,0.0]:
        last_action_trnsl = "TURN_LEFT"
    elif last_action == [0.0,0.0,0.0,0.0,0.0,0.0,1.0]:
        last_action_trnsl = "TURN_RIGHT"
            
    #scenario basic
               
    elif last_action == [1.0,0.0,0.0]:
                last_action_trnsl = "MOVE_LEFT"
    elif last_action == [0.0,1.0,0.0]:
        last_action_trnsl = "MOVE_RIGHT"
    elif last_action == [0.0,0.0,1.0]:
        last_action_trnsl = "ATTACK"

    # Scenario "take_cover"
    if last_action == [1.0, 0.0]:
        last_action_trnsl = "MOVE_LEFT"
    elif last_action == [0.0, 1.0]:
        last_action_trnsl = "MOVE_RIGHT"
    
    return last_action_trnsl

def find_object_data(object_list,object_id):
    for o in object_list:
        if o.id == object_id:
            return o
    return None

# create a temporary csv file
temp_file = "temp.csv"

# Open a single CSV file to store all episode data
episode_filename = sub_id + "_All_Episodes_game_data.csv"
with open(temp_file, 'w', newline='') as temp_csv: 
    csv_writer = csv.writer(temp_csv)
    columns = ["Episode",
               "State",
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

    for i in range(episodes):
        print("Episode #" + str(i + 1))
        game.new_episode()
        
        cumulative_reward = 0  # Initialize cumulative reward
        start_time = time.time()  # Record the start time
        while not game.is_episode_finished():
            state = game.get_state()
            game.advance_action()
            last_action = game.get_last_action()
            reward = game.get_last_reward()
            last_action_trnsl = translate_action(last_action)  # Define your translate_action function
            cumulative_reward += reward  # Update cumulative reward
            current_time = time.time() - start_time

            # Collect the IDs of all objects in the current state
            object_ids = []
            for o in state.objects:
                # if there is a problem with layout, comment out the next line, 
                # it is meant to not have the players' positions twice
                if o.name != "DoomPlayer":
                   object_ids.append(o.id)
                   print(o.name)
            
            unique_object_ids.update(object_ids)
            
            
            
            # Dynamically generate the columns based on object ids
            
            for object_id in unique_object_ids:
                if object_id not in object_id_to_column_index:
                    object_id_to_column_index[object_id] = len(columns)
                    columns.extend([f"{object_id}_name",
                                    f"{object_id}_x", 
                                    f"{object_id}_y", 
                                    f"{object_id}_z", 
                                    f"{object_id}_angle"])

            

            row = [i + 1, 
                   state.number,
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
                   current_time]

            # Add object information to the row for each object in the current state
            for object_id in unique_object_ids:
                object_data = find_object_data(state.objects, object_id)
                if object_data is not None:
                    row.extend([object_data.name,
                                object_data.position_x, 
                                object_data.position_y, 
                                object_data.position_z, 
                                object_data.angle])
                else:
                    row.extend([None,None,None,None,None])

            #write all data of within the episode
            
            csv_writer.writerow(row)
        

        

        # Write a row at the end of the episode with the total reward for this episode
        row_end = ([""]*len(columns))
        row_end [0:5]= ["Total Reward:", game.get_total_reward(),
                            "Time:", (time.time() - start_time),
                            "fps:", ((state.number)/(time.time()-start_time))]
        csv_writer.writerow(row_end)

        


        
    
    #overwrite original csv with modified first row
    with open(episode_filename,'w',newline='') as output_file:
        csv_writer=csv.writer(output_file)
        csv_writer.writerow(columns)

            
    
    


    print("Episode finished!")
    print("Total reward:", game.get_total_reward())
    print("Time:", (time.time() - start_time))
    print("************************")
    time.sleep(2.0)

game.close()

# Append the contents from temp_file to episode_filename
with open(episode_filename, 'a', newline='') as final_file:
    with open(temp_file, 'r') as temp_csv:
        temp_csv_reader = csv.reader(temp_csv)
        for row in temp_csv_reader:
            csv_writer = csv.writer(final_file)
            csv_writer.writerow(row)

# remove the temporary file after the file with the modified columns has been written
os.remove(temp_file)