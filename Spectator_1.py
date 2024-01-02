from __future__ import print_function
from time import sleep
import vizdoom as vzd
import csv
import time






# enter Subject Data
sub_id = "01"





    
game = vzd.DoomGame()

game.set_doom_config_path("/home/seanm/vizdoom_config/_vizdoom.ini")

# Choose scenario config file you wish to watch.
# Don't load two configs cause the second will overwrite the first one.
# Multiple config files are ok but combining these ones doesn't make much sense.
game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/basic.cfg")
#game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/simpler_basic.cfg")
#game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/rocket_basic.cfg")
#game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/deadly_corridor.cfg")
#game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/basic2.cfg")
#game.load_config("/home/seanm/.local/lib/python3.10/site-packages/vizdoom/scenarios/take_cover.cfg")


# Enables information about all objects present in the current episode/level.
game.set_objects_info_enabled(True)

# Enables information about all sectors (map layout).
game.set_sectors_info_enabled(True)


#clear all game variables first to unify the variables for all scenarios
game.clear_available_game_variables()

#add game variables for Health and Ammo

game.add_available_game_variable(vzd.GameVariable.HEALTH)
game.add_available_game_variable(vzd.GameVariable.AMMO2)



#add Game Variables for the position
pos_x=game.add_available_game_variable(vzd.GameVariable.POSITION_X)
pos_y=game.add_available_game_variable(vzd.GameVariable.POSITION_Y)
pos_z=game.add_available_game_variable(vzd.GameVariable.POSITION_Z)
angle=game.add_available_game_variable(vzd.GameVariable.ANGLE)





# Set screen size, will be displayed on the main display if multiple monitors are working
game.set_screen_resolution(vzd.ScreenResolution.RES_1280X960)

# Enables spectator mode, so you can play. Sounds strange, but it is the agent who is supposed to watch not you.
game.set_window_visible(True)
game.set_mode(vzd.Mode.SPECTATOR)

game.init()


episodes = 10

# Open a single CSV file to store all episode data
episode_filename = sub_id + "_All_Episodes_game_data.csv"
with open(episode_filename, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    columns=            ["Episode", 
                         "State", 
                         "Health", 
                         "Ammo", 
                         "x_pos", 
                         "y_pos", 
                         "z_pos", 
                         "angle/orientation", 
                         "Action", 
                         "Reward", 
                         "Cumulative Reward", 
                         "Time",
                         "Object ID",
                         "Object Name",
                         "Object Position x",
                         "Object Position y",
                         "Object Position z",
                         "Object Angle"]
    
    csv_writer.writerow(columns)

    for i in range(episodes):
        print("Episode #" + str(i + 1))
        game.new_episode()

        cumulative_reward = 0  # Initialize cumulative reward
        
       

        start_time = time.time() #Record the start time

        while not game.is_episode_finished():
            state = game.get_state()

            game.advance_action()
            last_action = game.get_last_action()
            reward = game.get_last_reward()
             # translate actions into words according to scenario
            
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
            
           #scenario take cover 
                
            elif last_action == [1.0,0.0]:
                last_action_trnsl = "MOVE_LEFT"
            elif last_action == [0.0,1.0]:
                last_action_trnsl = "MOVE_RIGHT"
           

            
            cumulative_reward += reward  # Update cumulative reward
            current_time = time.time()-start_time
            
            
          

            
            
            for o in state.objects:
                
                if o.name != "DoomPLayer":

                    print("Object id: ", o.id, "Object name: ", o.name)
                    #print(
                        #"Object position: x:",
                        #o.position_x,
                        #", y:",
                        #o.position_y,
                        #", z:",
                        #o.position_z,
                       # ", orientation:",
                        #o.angle


                #)
            
           
            csv_writer.writerow([i + 1, 
                                 state.number, 
                                 game.get_game_variable(vzd.GameVariable.HEALTH),
                                 game.get_game_variable(vzd.GameVariable.AMMO2),
                                 game.get_game_variable(vzd.GameVariable.POSITION_X),
                                 game.get_game_variable(vzd.GameVariable.POSITION_Y),
                                 game.get_game_variable(vzd.GameVariable.POSITION_Z),
                                 game.get_game_variable(vzd.GameVariable.ANGLE), 
                                 last_action_trnsl, 
                                 reward, 
                                 cumulative_reward, 
                                 current_time,  
                                o.id,
                                o.name,
                                o.position_x,
                                o.position_y,
                                o.position_z,
                                o.angle])

        # Write a row at the end of the episode with the total reward for this episode
        row_end = ([""]*len(columns))
        row_end [-6:]= ["Total Reward:", game.get_total_reward(),
                            "Time:", (time.time() - start_time),
                            "fps:", ((state.number)/(time.time()-start_time))]
        csv_writer.writerow(row_end)
        print("Episode finished!")
        print("Total reward:", game.get_total_reward())
        print("Time:", (time.time()-start_time))
        print("fps", ((state.number)/(time.time()-start_time)))
        print("************************")
        sleep(2.0)

game.close()