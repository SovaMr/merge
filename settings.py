from time import sleep


#########################################################################################################################################
                                            # === INITIAL SETTINGS === #
#########################################################################################################################################



## === CHANGE THESE VALUES - USE CORRECT API NAMES === ###

original = "Test1_RPP"            # Name of the original dashboard
dev1 = "RPPD"                      # Name of version 1 (when in conflict this is priority version)
dev2 = "Test1_RPP"                      # Name of version 2


output = "TEST"                       # Name of merged dashboard, waveVisualisation, and meta masterlabel
app = "SharedApp"                       # Name of the application to where you want to save the new dashboard

recipe = "NEW"
dataflow = "NEW"



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












