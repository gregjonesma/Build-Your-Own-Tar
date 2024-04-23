#cctar.py
# 4/23/2024
# Purpose Proceed with the coding challenge: "Build Your Own Tar"
# List the files in a tarball.
# Extract the files from a tarball.
# Create your own tarball.

import os
import sys
import pwd
import grp
import struct

# Define the lengths of each string in the header
# This ties back to the tar documentation's data structure for the header records.
header_string = [100, 8, 8, 8, 12, 12, 8, 1, 100, 6, 2, 32, 32, 8, 8, 155, 12]

# Construct the format string dynamically
record_format = ''.join(['{}s'.format(length) for length in header_string])

# Calculate the size of each record based on the format
# Since this is duplicating tar functionality, we know this ends up being 512 bytes.
record_size = struct.calcsize(record_format)

# Code to list the contents of the tar file
def list_contents(tar_file):
    # Open the tar file in binary mode
    with open(tar_file, 'rb') as file:
        while True:
            # Read the binary data
            binary_data = file.read(record_size)

            # If the binary_data is empty, we've reached the end of the file
            if binary_data == b'\x00' * record_size:
                break
            #print("Read {} bytes".format(len(binary_data)))
            #print("And yet, binary data ...", binary_data)
            # Unpack the record using the specified format
            record = struct.unpack(record_format, binary_data)

            # Convert each byte string to a Python string
            string_values = [field.decode('utf-8').strip('b\x00') for field in record]
            file_size_padded = string_values[4]

            # Remove null bytes from the file size
            file_size = int(file_size_padded, 8)

            # Print the unpacked record including the strings
            print(string_values[0])
            # Skip to the next block that contains the file's data
            file.seek((file_size // record_size + (1 if file_size % record_size != 0 else 0) ) * record_size, 1)
   

# Code to extract the contents of the tar file
def extract_contents(tar_file):
    # Open the tar file in binary mode
    with open(tar_file, 'rb') as file:
        while True:
            # Read a block (512 bytes) from the tar file
            # We use the variable record_size to make this more flexible.
            binary_data = file.read(record_size)

            # If the binary_data is empty, we've reached the end of the file
            if binary_data == b'\x00' * record_size:
                break
 
            # Unpack the record using the specified format
            record = struct.unpack(record_format, binary_data)

            # Convert each byte string to a Python string
            string_values = [field.decode('utf-8').strip('b\x00') for field in record]

            file_size_padded = string_values[4]
                        
            if len(file_size_padded) !=0:
                # Remove null bytes from the file size
                file_size = int(file_size_padded, 8)

                # Just so I can follow this in 6 months, I am putting the fiel name
                # in an intuitively named variable.
                filename = string_values[0]
                # Print or process file metadata as desired
                print(filename)

                # Extract the file content
                file_content = file.read(file_size)

                # Remove trailing null bytes from the file content
                file_content = file_content.rstrip(b'\x00')

                # Write the file content to disk
                with open(filename, 'wb') as outfile:
                    outfile.write(file_content)

                # Calculate the number of blocks to skip to reach the next file's metadata
                bytes_read = ((file_size + 511) // 512) * 512  # Round up to the next 512-byte block boundary
                bytes_leftover = 512 - (file_size % 512)
                
                # Skip to the start of the next file's metadata header
                file.seek(bytes_leftover, 1)
            else:
                break

# Code to create a tar file with the specified list of files
def create_tar_file(file_list, ip_new_tar_file):    
    # Open the file and truncate it to zero length
    with open(ip_new_tar_file, 'w') as f:
        pass

    # Assuming file_names is a list containing file names
    for file_name in file_list:
        # Initialize my variables.
        vb_file_contents_pre_chksum = ''
        vb_file_contents_post_chksum = ''
        my_record = [ ]
        
        # Add your processing logic here for each file_name
        # Check if the file exists
        if os.path.exists(file_name) and os.path.isfile(file_name) :
            
            running_header_bytes = file_name.ljust(100, '\x00')
            #If I can get my_record to work, then I may not need
            # the running total of vb_file_contents_pre_chksum.
            my_record.append(file_name.ljust(100, '\x00'))
            vb_file_contents_pre_chksum = running_header_bytes

            # Get file status
            file_status = os.stat(file_name)
            file_permissions = file_status.st_mode & 0o777
            # Convert file permissions to octal representation
            file_permissions_octal = oct(file_permissions)

            #Get rid if the 1st two characters. They are 0o or somesuch
            file_permissions_to_store = file_permissions_octal[2:]

            running_header_bytes += file_permissions_to_store.rjust(7, '0') + '\x00'
            my_record.append(file_permissions_to_store.rjust(7, '0') + '\x00')
            vb_file_contents_pre_chksum += file_permissions_to_store.rjust(7, '0') + '\x00'

#################################################################################
#           # Getting into some weeds
#           with open(ip_new_tar_file, 'a') as f:
#               f.write(file_name.ljust(100, '\x00'))
#               f.write(file_permissions_to_store.rjust(7, '0') + '\x00' )
#################################################################################

            #UID
            file_uid = file_status.st_uid # & 0o777
            file_uid_octal = oct(file_uid)
            file_uid_to_store = file_uid_octal[2:]
            running_header_bytes += file_uid_to_store.rjust(7, '0') + '\x00' 
            my_record.append(file_uid_to_store.rjust(7, '0') + '\x00' )
            vb_file_contents_pre_chksum += file_uid_to_store.rjust(7, '0') + '\x00' 
            
            #GID
            file_gid = file_status.st_gid 
            file_gid_octal = oct(file_gid)
            file_gid_to_store = file_gid_octal[2:]
            running_header_bytes += file_gid_to_store.rjust(7, '0') + '\x00' 
            my_record.append( file_gid_to_store.rjust(7, '0') + '\x00' )
            vb_file_contents_pre_chksum += file_gid_to_store.rjust(7, '0') + '\x00' 
            
            #File Size
            file_size = file_status.st_size
            file_size_octal = oct(file_size)
            file_size_to_store = file_size_octal[2:]
            running_header_bytes += file_size_to_store.rjust(11, '0') + '\x00' 
            my_record.append(file_size_to_store.rjust(11, '0') + '\x00')
            vb_file_contents_pre_chksum += file_size_to_store.rjust(11, '0') + '\x00' 
            
            # Time - last updated
            file_mtime = file_status.st_mtime
            file_mtime_octal = oct(int(file_mtime))
            file_mtime_to_store = file_mtime_octal[2:]
            running_header_bytes += file_mtime_to_store.rjust(11, '0') + '\x00'
            my_record.append(file_mtime_to_store.rjust(11, '0') + '\x00')
            vb_file_contents_pre_chksum += file_mtime_to_store.rjust(11, '0') + '\x00'
            
            my_checksum = 0
            for byte in running_header_bytes:
                if byte == '\x00':
                    my_checksum += ord(' ')
                else:
                    my_checksum += ord(byte)
            #Checksum. This is made up, for now.
            running_header_bytes += '        '
            my_record.append('        ')
            mychksum = 5342
            mychksum_oct = oct(mychksum)

            #We already confirmed this is good old, standard file.
            #Now we tell the tar file.
            running_header_bytes += '0'
            my_record.append('0')
            vb_file_contents_post_chksum +=  '0'

            #Name of the linked file. Out of scope, here and now.
            running_header_bytes += str('').rjust(100, '\x00')
            my_record.append(str('').rjust(100, '\x00'))
            vb_file_contents_post_chksum += str('').rjust(100, '\x00')

            magic = 'ustar '
            running_header_bytes += magic + '\x00'
            my_record.append(magic + '\x00')
            vb_file_contents_post_chksum += magic + '\x00'

            #Version characters.
            my_record.append(' ' + '\x00')

            # Get the user name (uname) associated with the file's user ID (uid)
            user_name = pwd.getpwuid(file_status.st_uid).pw_name
            running_header_bytes += user_name.ljust(32, '\x00')
            my_record.append(user_name.ljust(32, '\x00'))
            vb_file_contents_post_chksum += user_name.ljust(32, '\x00')

            # Get the group name (gname) associated with the file's group ID (gid)
            group_name = grp.getgrgid(file_status.st_gid).gr_name
            running_header_bytes += group_name.ljust(32, '\x00')
            my_record.append(group_name.ljust(32, '\x00'))
            vb_file_contents_post_chksum += group_name.ljust(32, '\x00')

            #devmajor - ignored for this
            devmajor = ''
            running_header_bytes += devmajor.ljust(8, '\x00')
            my_record.append(devmajor.ljust(8, '\x00'))
            vb_file_contents_post_chksum += devmajor.ljust(8, '\x00')

            #devminor - ignored for this
            devminor = ''
            running_header_bytes += devminor.ljust(8, '\x00')
            my_record.append(devminor.ljust(8, '\x00'))
            vb_file_contents_post_chksum += devminor.ljust(8, '\x00')

            #prefix - ignored for this. I cannot reegineer everything.
            prefix = ''
            running_header_bytes += prefix.ljust(155, '\x00')
            my_record.append(prefix.ljust(155, '\x00'))
            vb_file_contents_post_chksum += prefix.ljust(155, '\x00')

            headerwrapup = ''
            running_header_bytes += headerwrapup.ljust(12, '\x00')
            my_record.append(headerwrapup.ljust(12, '\x00'))
            vb_file_contents_post_chksum += headerwrapup.ljust(12, '\x00')

            my_checksum = 0
            my_checksum = sum(ord(byte) for byte in ''.join(my_record))  # Sum of ASCII values of all characters in my_record
            my_checksum_str = oct(my_checksum)[2:].rjust(6, '0') + '\x00' + ' '
            
            # Insert checksum into my_record at index 6
            my_record[6] = my_checksum_str
            
            my_record_bytes = [field.encode('utf-8') for field in my_record]
            binary_data = struct.pack(record_format, *my_record_bytes)
            with open(ip_new_tar_file, 'ab') as f:
                f.write(binary_data)
            
            # Populating the file with the contents
            # of the file we are tar-ing
            with open(file_name, "r") as input_file:
                with open(ip_new_tar_file, 'a') as f:
                    while True:
                        # Read 512 bytes from the input file
                        data = input_file.read(512)
                                                            
                        # If no more data is left to read, break out of the loop
                        if not data:
                            break
                                       
                        if len(data) == 512:
                            # Write the read data to the output file
                            f.write(data)
                                                                                                                                        
                        # If the data read is less than 512 bytes, pad the remaining space with null bytes
                        if len(data) < 512:
                            padding = data.ljust(512, '\x00')
                            f.write(padding)

            # Add your processing logic here
        else:
            print("File", file_name, "does not exist. Moving on")

    # Generally, there are 1024 extra bytes at the end.
    with open(ip_new_tar_file, 'a') as f:
        data = ''
        padding = data.ljust(1024, '\x00')
        f.write(padding)

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 my_tar.py [list|extract|create] <tar_file> [file1 file2 ...]")
        return

    command = sys.argv[1]
    tar_file = sys.argv[2]

    if command == "list":
        list_contents(tar_file)
    elif command == "extract":
        extract_contents(tar_file)
    elif command == "create":
        # Perhaps the user sent us redirected input rather than a list of files.
        if not sys.stdin.isatty():
            # Read file list from redirected input
            file_list = sys.stdin.read().splitlines()
        else:
            # Okay. They just sent a list of files. As you do.
            file_list = sys.argv[3:]
        create_tar_file(file_list, tar_file)
    else:
        print("Invalid command. Use 'list', 'extract', or 'create'.")

# Reminder to myself: If I run this program by itself then
# the name variable will be main. (Well, with the underscores)
# So the program will run "normally".
 
if __name__ == "__main__":
    main()



