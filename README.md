# set_mp3_tags

## Requirements
`pip install ShazamAPI`
`pip install eyed3`

## What this Program Does
This program will read mp3 files from a given repository, use the Shazam API to find the desired tags for the MP3. And set them to the MP3 after user verification.

## How to Run the Program
To run for all files in a directory 
How the flags work:
--directory Sets what directory your mp3s are in (Can be set to a default in the script)
--filename Which file you want to grab mp3s for. 
--all_files_in_directory Flag stating to grab tags for all mp3s in the directory. Makes --filename not necessary (Defaults to False)
--overwrite_tags Flag about whether or not you want to perform for all files, or only ones without tags (Defaults to False)
--skip_manual_verification Flag whether you want to perform manual verification on the tags that shazam finds.

Example Command
`python3 gui.py --directory <path_to_directory> -a`
