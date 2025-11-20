from time import sleep


#########################################################################################################################################
                                            # === INITIAL SETTINGS === #
#########################################################################################################################################



## === CHANGE THESE VALUES - USE CORRECT API NAMES === ###

original = "name_of_original_db"            # Name of the original dashboard
dev1 = "dev_1_db"                           # Name of version 1 
dev2 = "dev_2_db"                           # Name of version 2


output = "output_name"                      # Name of merged dashboard, waveVisualisation, and meta masterlabel
app = "app_name"                            # Name of the application to where you want to save the new dashboard

recipe = "recipe_name"
dataflow = "dataflow_name"



sleeptime = 0
        
def break_line():
    print(f"...")
    sleep(sleeptime)
    print(f"...")
    sleep(sleeptime)
    print(f"...")
    sleep(sleeptime)

def success():
    suc = "✅ SUCCESS"
    sleep(sleeptime)
    print(suc)

def start_merge():
    print(f"🔄 Starting the merge process")
    sleep(sleeptime)
    break_line()

def wait_for_it():
    sleep(sleeptime)













