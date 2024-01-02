from __future__ import print_function
import vizdoom as vzd
import csv
import time
import numpy as np

# Enter Subject Data
sub_id = "01"

game = vzd.DoomGame()
# where to get the .ini-file from
game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini")

# Choose the scenario config file you wish to watch.
# Don't load two configs because the second will overwrite the first one.
# Multiple config files are okay, but combining these ones doesn't make much sense.

game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/basic.cfg")

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
game.set_mode(vzd.Mode.SPECTATOR)
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
def find_object_data(object_list,object_id,object_name):
    for o in object_list:
        if o.id == object_id and o.name != object_name:
            return o
    return None



# Specify how many Episodes 
episodes = 20

# header for the csv-file
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
               "Time",
               "Object_ID",
               "Object_Name",
               "Object_PosX",
               "Object_PosY",
               "Object_PosZ",
               "Object_Angle",
               "App_Object_ID",
               "App_Object_Name",
               "App_Object_PosX",
               "App_Object_PosY",
               "App_Object_PosZ",
               "App_Object_Angle"
               ]


# Open a single CSV file to store all episode data
episode_filename = sub_id + "_All_Episodes_game_data.csv"
with open(episode_filename,'w', newline='') as starting_file:
    csv_writer = csv.writer(starting_file)
    csv_writer.writerow(columns)
     



#Use a set to keep track of uniqueobject IDs
unique_object_ids = set()

    

# create a dictionary to store mapping between object ID and column index
object_id_to_column_index = {}

#create single column arrays for each variable to later concatenate into a dataframe
Episode_arr = np.full((episodes*151,1), np.nan, dtype = np.int32)
State_arr = np.full((episodes*151,1),np.nan, dtype = np.int32)
Tic_arr = np.full((episodes*151,1), np.nan, dtype = np.int32)
Health_arr = np.full((episodes*151,1),np.nan, dtype = np.int32)
Ammo_arr = np.full((episodes*151,1), np.nan, dtype = np.int32)
xpos_arr = np.full((episodes*151,1), np.nan, dtype = np.float64)
ypos_arr = np.full((episodes*151,1), np.nan, dtype = np.float64)
zpos_arr = np.full((episodes*151,1), np.nan, dtype = np.float64)
angle_arr = np.full((episodes*151,1), np.nan, dtype = np.float64)
Action_arr = np.full((episodes*151,1), np.nan, dtype = np.dtype('U10'))
Reward_arr = np.full((episodes*151,1), np.nan, dtype = np.int32)
CumReward_arr = np.full((episodes*151,1), np.nan, dtype = np.int32)
Time_arr = np.full((episodes*151,1), np.nan, dtype = np.float64)
ObjID_arr = np.full((episodes*151,1),np.nan, dtype = np.int32)
Objname_arr = np.full((episodes*151,1), np.nan, dtype = np.dtype('U10'))
Objx_arr = np.full((episodes*151,1), np.nan, dtype = np.float64)
Objy_arr = np.full((episodes*151,1), np.nan, dtype = np.float64)
Objz_arr = np.full((episodes*151,1), np.nan, dtype = np.float64)
Objang_arr = np.full((episodes*151,1), np.nan, dtype = np.float64)
AppobjID_arr = np.full((episodes*151,1), np.nan, dtype = np.int32)
Appobjname_arr = np.full((episodes*151,1), np.nan, dtype = np.dtype('U12'))
Appobjx_arr = np.full((episodes*151,1), np.nan, dtype = np.float64)
Appobjy_arr = np.full((episodes*151,1), np.nan, dtype = np.float64)
Appobjz_arr = np.full((episodes*151,1), np.nan, dtype = np.float64)
Appobjangle_arr = np.full((episodes*151,1), np.nan, dtype = np.float64)


#starting the index
current_index = 0

# Loop through episodes
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
        last_action_trnsl = translate_action(last_action)  
        
        cumulative_reward += reward  # Update cumulative reward
        current_time = time.time() - start_time
        object_ids = []
        for o in state.objects:
            object_ids.append(o.id)
        unique_object_ids.update(object_ids)
        
        # Collect data for each time step within the episode so for each array
        Episode_arr[current_index] = i+1
        State_arr[current_index] = state.number
        Tic_arr[current_index] = game.get_episode_time()
        Health_arr[current_index] =  game.get_game_variable(vzd.GameVariable.HEALTH)
        Ammo_arr[current_index] =  game.get_game_variable(vzd.GameVariable.AMMO2)
        xpos_arr[current_index] = game.get_game_variable(vzd.GameVariable.POSITION_X)
        ypos_arr[current_index] =  game.get_game_variable(vzd.GameVariable.POSITION_Y)
        zpos_arr[current_index] = game.get_game_variable(vzd.GameVariable.POSITION_Z)
        angle_arr[current_index] = game.get_game_variable(vzd.GameVariable.ANGLE)
        Action_arr[current_index] =  last_action_trnsl
        Reward_arr[current_index] = reward
        CumReward_arr[current_index] =  cumulative_reward
        Time_arr[current_index] = current_time
        
        
        for object_id in unique_object_ids:
            object_data = find_object_data(state.objects,object_id,"DoomPlayer")
            if object_data is not None and object_data.name == "Cacodemon":

                ObjID_arr[current_index] = object_data.id
                Objname_arr[current_index] =  object_data.name
                Objx_arr[current_index] =     object_data.position_x 
                Objy_arr[current_index] =     object_data.position_y
                Objz_arr[current_index] =     object_data.position_z
                Objang_arr[current_index] =  object_data.angle

            elif object_data is not None:
                AppobjID_arr[current_index] = object_data.id
                Appobjname_arr[current_index] =  object_data.name
                Appobjx_arr[current_index] =   object_data.position_x
                Appobjy_arr[current_index] =  object_data.position_y 
                Appobjz_arr[current_index] =   object_data.position_z
                Appobjangle_arr[current_index] =  object_data.angle
            
            else:
                ObjID_arr[current_index] = 0
                Objname_arr[current_index] =  "None"
                Objx_arr[current_index] =     0
                Objy_arr[current_index] =     0
                Objz_arr[current_index] =    0
                Objang_arr[current_index] =   0
                AppobjID_arr[current_index] = 0
                Appobjname_arr[current_index] =  "None"
                Appobjx_arr[current_index] =     0 
                Appobjy_arr[current_index] =     0
                Appobjz_arr[current_index] =     0
                Appobjangle_arr[current_index] =   0
            
                
                
            

        
        
        current_index += 1 #increment index
    #row_end = ([""]*len(columns))
    #row_end [0:5]= ["Total Reward:", game.get_total_reward(),
                            #"Time:", (time.time() - start_time),
                            #"fps:", ((state.number)/(time.time()-start_time))]
    #episode_data[current_index] = row_end
    #current_index += 1 #increment index
    
  

   
       

    print("Episode finished!")
    print("Total reward:", game.get_total_reward())
    print("Time:", (time.time() - start_time))
    print("************************")
    time.sleep(0.5)


game.close()

all_episode_data =  np.concatenate((Episode_arr,
        State_arr,
        Tic_arr,
        Health_arr,
        Ammo_arr,
        xpos_arr,
        ypos_arr,
        zpos_arr,
        angle_arr,
        Action_arr,
        Reward_arr,
        CumReward_arr,
        Time_arr,
        ObjID_arr,
        Objname_arr,
        Objx_arr,
        Objy_arr,
        Objz_arr,
        Objang_arr,
        AppobjID_arr,
        Appobjname_arr,
        Appobjx_arr,
        Appobjy_arr,
        Appobjz_arr,
        Appobjangle_arr),
        axis=1)
   
        

    # Write episode_data to CSV file after each episode
with open(episode_filename, 'a', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(all_episode_data)

