#cctar.py
# 4/22/2024
# Purpose Proceed with the coding challenge: "Build Your Own Tar"
# In this case, manually create a tar ball.

import os
import sys
import pwd
import grp

# Code to list the contents of the tar file
def list_contents(tar_file):
    # Open the tar file in binary mode
    with open(tar_file, 'rb') as file:
        while True:
            # Read a block (512 bytes) from the tar file
            block = file.read(512)

            # If the block is empty, we've reached the end of the file
            if not block:
                break

            # Extract file metadata from the block
            filename = block[:100].decode().rstrip('\x00')
            file_size_padded = block[124:136].decode().rstrip('\x00')
            
            if len(file_size_padded) !=0: 
                # Remove null bytes from the file size
                file_size = int(file_size_padded.replace('\x00', ''), 8)

                # Print or process file metadata as desired
                print(filename)
               
                # Skip to the next block that contains the file's data
                file.seek(file_size // 512 + (1 if file_size % 512 != 0 else 0) * 512, 1)
            else:
                break
# Code to extract the contents of the tar file
def extract_contents(tar_file):
    # Open the tar file in binary mode
    with open(tar_file, 'rb') as file:
        while True:
            # Read a block (512 bytes) from the tar file
            block = file.read(512)

            # If the block is empty, we've reached the end of the file
            if not block:
                break

            # Extract file metadata from the block
            filename = block[:100].decode().rstrip('\x00')
            file_size_padded = block[124:136].decode().rstrip('\x00')
            
            if len(file_size_padded) !=0: 
                # Remove null bytes from the file size
                file_size = int(file_size_padded.replace('\x00', ''), 8)

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
        
        # Add your processing logic here for each file_name
        # Check if the file exists
        if os.path.exists(file_name) and os.path.isfile(file_name) :
            
            running_header_bytes = file_name.ljust(100, '\x00')
            vb_file_contents_pre_chksum = running_header_bytes

            # Get file status
            file_status = os.stat(file_name)
            file_permissions = file_status.st_mode & 0o777
            # Convert file permissions to octal representation
            file_permissions_octal = oct(file_permissions)

            #Get rid if the 1st two characters. They are 0o or somesuch
            file_permissions_to_store = file_permissions_octal[2:]

            running_header_bytes += file_permissions_to_store.rjust(7, '0') + '\x00'
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
            vb_file_contents_pre_chksum += file_uid_to_store.rjust(7, '0') + '\x00' 
            
            #GID
            file_gid = file_status.st_gid 
            file_gid_octal = oct(file_gid)
            file_gid_to_store = file_gid_octal[2:]
            running_header_bytes += file_gid_to_store.rjust(7, '0') + '\x00' 
            vb_file_contents_pre_chksum += file_gid_to_store.rjust(7, '0') + '\x00' 
            
            #File Size
            file_size = file_status.st_size
            file_size_octal = oct(file_size)
            file_size_to_store = file_size_octal[2:]
            running_header_bytes += file_size_to_store.rjust(11, '0') + '\x00' 
            vb_file_contents_pre_chksum += file_size_to_store.rjust(11, '0') + '\x00' 
            
            # Time - last updated
            file_mtime = file_status.st_mtime
            file_mtime_octal = oct(int(file_mtime))
            file_mtime_to_store = file_mtime_octal[2:]
            running_header_bytes += file_mtime_to_store.rjust(11, '0') + '\x00'
            vb_file_contents_pre_chksum += file_mtime_to_store.rjust(11, '0') + '\x00'
            
            my_checksum = 0
            for byte in running_header_bytes:
                if byte == '\x00':
                    my_checksum += ord(' ')
                else:
                    my_checksum += ord(byte)
            #Checksum. This is made up, for now.
            running_header_bytes += '        '
            mychksum = 5342
            mychksum_oct = oct(mychksum)

            #We already confirmed this is good old, standard file.
            #Now we tell the tar file.
            running_header_bytes += '0'
            vb_file_contents_post_chksum +=  '0'

            #Name of the linked file. Out of scope, here and now.
            running_header_bytes += str('').rjust(100, '\x00')
            vb_file_contents_post_chksum += str('').rjust(100, '\x00')

            magic = 'ustar  '
            running_header_bytes += magic + '\x00'
            vb_file_contents_post_chksum += magic + '\x00'

            # Get the user name (uname) associated with the file's user ID (uid)
            user_name = pwd.getpwuid(file_status.st_uid).pw_name
            running_header_bytes += user_name.ljust(32, '\x00')
            vb_file_contents_post_chksum += user_name.ljust(32, '\x00')

            # Get the group name (gname) associated with the file's group ID (gid)
            group_name = grp.getgrgid(file_status.st_gid).gr_name
            running_header_bytes += group_name.ljust(32, '\x00')
            vb_file_contents_post_chksum += group_name.ljust(32, '\x00')

            #devmajor - ignored for this
            devmajor = ''
            running_header_bytes += devmajor.ljust(8, '\x00')
            vb_file_contents_post_chksum += devmajor.ljust(8, '\x00')

            #devminor - ignored for this
            devminor = ''
            running_header_bytes += devminor.ljust(8, '\x00')
            vb_file_contents_post_chksum += devminor.ljust(8, '\x00')

            #prefix - ignored for this. I cannot reegineer everything.
            prefix = ''
            running_header_bytes += prefix.ljust(155, '\x00')
            vb_file_contents_post_chksum += prefix.ljust(155, '\x00')

            headerwrapup = ''
            running_header_bytes += headerwrapup.ljust(12, '\x00')
            vb_file_contents_post_chksum += headerwrapup.ljust(12, '\x00')

            my_checksum = 0
            byte_array = running_header_bytes.encode('utf-8')
            my_checksum = [byte for byte in byte_array]
            my_checksum_str = oct(sum(my_checksum))[2:].rjust(6,'0') + '\x00' + ' ' 

            with open(ip_new_tar_file, 'a') as f:
                f.write(vb_file_contents_pre_chksum)
                f.write(my_checksum_str)
                f.write(vb_file_contents_post_chksum)
            
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



