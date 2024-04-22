# Build-Your-Own-Tar
A "Coding Challenge" from John Crickett's  [Coding Challenges](https://codingchallenges.fyi/challenges/intro)

In specific, look to his [Build Your Own Tar] (https://codingchallenges.fyi/challenges/challenge-tar) challenge.

My solution has definite limitations and variations.

Since I wrote this in Ubuntu, I had to modify his original tar call to generate a file that ostensibly matched what he was getting.

Instead of:
tar -cf files.tar file1.txt file2.txt file3.txt

I used 
tar -c -b 8 -f files.tar file1.txt file2.txt file3.txt

Otherwise, you end up with an additional 12 sets of 512 null bytes.

The parameters are different and limited. 
"list"
"create"
"extact"

The corresponding commands would be:
python3 cctar.py list files.tar 
python3 cctar.py create files.tar file1.txt file2.txt file3.txt
python3 cctar.py extract files.tar 

This is not a complete re-creation of the tar command.

It is limited by the implied scope of the original challenge.
For example:
* The file names do not include subdirectories.
* The contents of each file are small. There is no overflow past 512 bytes.
* Only 3 files are put into the original tarball. Additional files may, or may not work. 
