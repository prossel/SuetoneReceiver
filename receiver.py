# Receive the data from the BLE device and write it to a file
#
# to execute this script, run the following command:
# python3 receiver.py
#
# Pierre Rossel 2024-05-05

import asyncio
from bleak import BleakScanner, BleakClient, BleakError
import json

client = None
device_name = "Suetone"  # replace with your device's name
characteristic_uuid = "6E400003-1A90-46F9-A2C3-46028A276125"  # replace with your characteristic's UUID
output_file = "output.txt"  # replace with your desired output file
bytes_to_receive = 0
file = None

def notification_handler(sender: int, data: bytearray):
    global output_file
    global bytes_to_receive
    global file 
    
    # if we have an output file, then write the data to the file
    if file and bytes_to_receive > 0:
        # with open(output_file, "ab") as file:
            # file.write(str(data) + "\n")
            
        # append raw bytes to the file
        file.write(data)
        
        print(".", end="", flush=True)

        bytes_to_receive -= len(data)
        if bytes_to_receive < 0:
            print(f"Received more data than expected. Expected: {bytes_to_receive + len(data)}, received: {len(data)}")
        
        # close the file if we have received all the data
        if bytes_to_receive <= 0:
            print(f"\nFile {output_file} written successfully!")
            file.close()
        
            
    else:
        # print(f"Received: {data} from {sender}")
        print(f"Received: {data}")
        
        # if data is JSON like "{FILE: "image.jpg", SIZE: 123456, CHUNK: 12345}", then extract the filename, size and chunk
        # and save the chunk to a file
        # if data.startswith(b"{\"file\": "):
        if b"file" in data:
            #  trim the leading and trailing whitespaces
            data_str = data.strip()
            
            # convert JSON like data to a dictionary
            data_dict = json.loads(data_str)
            print(data_dict)
        
            bytes_to_receive = data_dict["size"]
            
            output_file = data_dict["file"]
            print(f"Writing to file {output_file}...")
            
            # create and reset the file
            file = open(output_file, "wb")
        
        
async def run():
    print (f"Scanning for device with name {device_name}")

    scanner = BleakScanner()
    while True:
        devices = await scanner.discover()

        for device in devices:
            if device.name == device_name:
                print(f"Found device with name {device.name} and address {device.address}")
                try:
                    async with BleakClient(device) as client:
                        print(f"Connected: {client.is_connected}")
                        await client.start_notify(characteristic_uuid, notification_handler)
                        while True:
                            if not client.is_connected:
                                print("Disconnected, trying to reconnect...")
                                break
                            await asyncio.sleep(1.0)  # check connection status every second
                        if client.is_connected:
                            await client.stop_notify(characteristic_uuid)
                except BleakError as e:
                    print(f"Could not connect to device: {e}")
                break
        else:
            print(f"No device found with the desired name {device_name}")
            # print the list of devices found
            print("Devices found:")
            for device in devices:
                print(f" - {device.name}")
                
            await asyncio.sleep(1.0)  # wait for a second before scanning again

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
except KeyboardInterrupt:
    print(" Received exit signal in loop, stopping...")
     
    # Cancel all tasks lingering
    tasks = asyncio.all_tasks(loop=loop)
    for task in tasks:
        task.cancel()
    # Gather all tasks and let them finish
    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
except BleakError as e:
    # may be raised if Bluetooth is disabled (happend on macOS when sleep mode is activated)
    print(f"Error: {e}")
finally:
    # cleanup
    # print("Closing event loop.")
    loop.close()
