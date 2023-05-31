from saleae import automation
import os
import os.path
import pandas as pd
from datetime import datetime
import multiprocessing as mp
import time
import queue

q= queue.Queue() #Set up queue to output file names
filecount = 0 #initialize file count to 0

def saleae_acquire():
    
   #while (True): 
    print("**Saleae_acquire process has started!**")

    # Connect to the running Logic 2 Application on port `10430`.
    # Alternatively you can use automation.Manager.launch() to launch a new Logic 2 process - see
    # the API documentation for more details.
    # Using the `with` statement will automatically call manager.close() when exiting the scope. If you
    # want to use `automation.Manager` outside of a `with` block, you will need to call `manager.close()` manually.
    with automation.Manager.connect(port=10430) as manager:

    # Configure the capturing device to record on desired channels
        device_configuration = automation.LogicDeviceConfiguration(
            enabled_analog_channels=[1, 2],
            analog_sample_rate=1_562_500,
            enabled_digital_channels=[0],
            digital_sample_rate=6_250_000,
            digital_threshold_volts=3.3,
        )

        capture_configuration = automation.CaptureConfiguration(
            capture_mode=automation.DigitalTriggerCaptureMode(automation.manager.DigitalTriggerType.RISING,0,None,None,after_trigger_seconds=4)
        )

        # Start a capture - the capture will be automatically closed when leaving the `with` block
        with manager.start_capture(
                #device_id='F4241', #Uncomment & edit to the ID of your device if the software is not able to find it automatically
                device_configuration=device_configuration,
                capture_configuration=capture_configuration) as capture:
            
            print("Waiting for capture to complete")

            # Wait until the capture has finished
            capture.wait()

            print("Capture complete!")

            print("Saving file...")
            # Store output in a timestamped directory
            saveDirectory = "/Users/bu5/Documents/Project Info/Pyrometer/Saleae/" #Edit this to choose directory output is saved in
            os.chdir(saveDirectory)
            output_dir = os.path.join(os.getcwd(), f'output-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}')
            os.makedirs(output_dir)

            # Export raw digital data to a CSV file
            capture.export_raw_data_csv(directory=output_dir, analog_channels=[1, 2])

            # Finally, save the capture to a file
            capture_filepath = os.path.join(output_dir, 'Pyrometer_capture.sal')
            capture.save_capture(filepath=capture_filepath)

            filename = output_dir + "/analog.csv"

            q.put(filename) #Add the name of the file to the queue for the analyze consumer loop to pick up

            print("New filename added to queue: " + filename)
            print("There are now " + str(q.qsize()) + " files waiting to be analyzed.")

def saleae_analyze():
        
        with automation.Manager.connect(port=10430) as manager:

            print("Scanning for newly created file")

            #if q.qsize() > 0 :

            #print('New file detected!')

            print("File in queue is: " + q.get())

            filename = q.get() #Retrieve the last file generated

                #filename='/Users/bu5/Documents/Project Info/Pyrometer/Saleae/output-2023-05-26_13-33-29/analog.csv'

            df = pd.read_csv(filename) #Use pandas to read the file output
            print(df.head()) #Print the first 5 rows to ensure the data is correct

            type(df.to_numpy())
            df.to_numpy()[0]

            print(df)

            #if q.empty() and filecount != 0:
                    #print("Finished acquiring")
                    #manager.close()
             

if __name__ == '__main__':

    p1 = mp.Process(target = saleae_acquire)
    p2 = mp.Process(target = saleae_analyze)

    p1.start()
    p2.start()