# Build-Your-Own-Tar
A "Coding Challenge" from John Crickett's  [Coding Challenges](https://codingchallenges.fyi/challenges/intro)

In specific, look to his [Build Your Own Tar] (https://codingchallenges.fyi/challenges/challenge-tar) challenge.

This solution was built on Ubuntu Linux (Ubuntu 22.04.4 LTS) using Python3 (3.10.12). 

My solution has definite limitations and variations.

Since I wrote this in Ubuntu, I got a surprise lesson in "blocking factors". Ubuntu's version of tar uses a blocking factor of 20. For the purposes of this challenge, that means a lot of 512 blocks that are only null bytes.

To keep in scope and honor the spirit of the challenge, if not the exact letter, I modified the tar command used to create the intial tar file to be used to compare your work against.

Instead of:
tar -cf files.tar file1.txt file2.txt file3.txt

I used 
tar -c -b 8 -f files.tar file1.txt file2.txt file3.txt

That should give you 2 sets of 512 null bytes.

Otherwise, you end up with an additonal 12 sets of 512 null bytes.

The parameters are different and limited. 
"list"
"create"
"extact"

The corresponding commands would be:
python3 cctar.py list files.tar 
python3 cctar.py create files.tar file1.txt file2.txt file3.txt
python3 cctar.py extract files.tar 

This is not a complete re-creation of the tar command.

This code is limited by the implied scope of the original challenge.
For example:
* The file names do not include, or deal with, subdirectories.
* The contents of each file is small. There is no overflow past 512 bytes.
* Only 3 files are put into the original tarball. Additional files may, or may not work.

Shout out to John for giving me some feedback on the code itself. My original release seemed to work, within scope, but it was definitely chaotic. He recommended that I review the struct library. That took some additional thought on my part, but it does look like code that will be more clear in six months than what I had originally wrote.
