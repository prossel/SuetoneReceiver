# test to write a file in chunks and see how max is handling the locked file
# 
# to execute this script, run the following command:
# python3 testWriteFile.py
#
# Pierre Rossel 2024-05-05

import time

# Open the source file in binary read mode and destination file in binary write mode
with open("black.jpg", "rb") as src_file, open("capture.jpg", "wb") as dest_file:
    
    print("Writing file capture.jpg...")
    
    # file size of source file
    file_size = src_file.seek(0, 2)
    src_file.seek(0)
        
    chunk_size = file_size // 10
    
    while True:
        # Read some bytes from the source file
        chunk = src_file.read(chunk_size)
        if not chunk:
            # If the chunk is empty, this means we've reached the end of the file
            break

        # Write the chunk to the destination file
        dest_file.write(chunk)

        print(".", end="", flush=True)

        # Sleep for a bit to simulate a long write operation
        time.sleep(1)
    
    print("\nFile capture.jpg written successfully!")
    
