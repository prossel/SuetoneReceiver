import asyncio
from bleak import BleakScanner, BleakClient, BleakError

device_name = "Suetone"  # replace with your device's name
characteristic_uuid = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # replace with your characteristic's UUID
output_file = "output.txt"  # replace with your desired output file

def notification_handler(sender: int, data: bytearray):
    print(f"Received: {data} from {sender}")
    with open(output_file, "ab") as file:
        # file.write(str(data) + "\n")
        
        # append raw bytes to the file
        file.write(data)
        
        
        
async def run():
    scanner = BleakScanner()
    try:
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
    except KeyboardInterrupt:
        print("Received exit signal, stopping...")

loop = asyncio.get_event_loop()
loop.run_until_complete(run())