import eyed3
from os import listdir
from ShazamAPI import Shazam
import argparse
from pprint import pprint
from gui import Form
from eyed3.id3.frames import ImageFrame


def get_mp3s(directory):
    files = listdir(directory)
    mp3s = [eyed3.load(directory + file) for file in files if file[-4:] == ".mp3"]
    return mp3s


def has_tags(mp3):
    # assuming if title is there, the rest I care about are there
    if mp3.tag is None:
        mp3.initTag()

    return mp3.tag.title is not None

        


def set_mp3_tags(mp3, set_track_num, tags):   

    print(mp3.tag.images)
    if mp3.tag.title is None:
        mp3.tag.title = tags.get("title") 

    if mp3.tag.artist is None:
        mp3.tag.artist = tags.get("artist")

    if mp3.tag.album is None:
        mp3.tag.album = tags.get("album")

    if mp3.tag.cd_id is None:
        mp3.tag.album_artist = str(tags.get('albumadamid'))

    if mp3.tag.images is None:
        mp3.tag.images.set(ImageFrame.FRONT_COVER, open(tags['background'],'rb').read(), 'image/jpeg')

    
    if set_track_num and mp3.tag.track_num is None:
        mp3.tag.track_num = tags.get('track_num')


    mp3.tag.save()


def manual_tag_verification(mp3, tags):
    # return True means skip the file. False means don't skip the file
    # getting verification
    print(f"The tags found for {mp3} were")
    pprint(tags)
    response = input("Are these correct (y/n): ")

    # if not y, we need more inputs from the user
    if response != 'y':
        # do we want to input or skip this file?
        response = input(f"Update Tags 'u' \nContinue to next file 'Enter'\n?")
        # if we just want to skip the file
        if response != 'u':
            print(f"skipping file {mp3}")
            return True

        manual_set_new_tag(tags)
    
    return False

def manual_set_new_tag(tags):

    while True:
        tag_options = dict(zip(list(range(len(tags.keys()))), tags.keys()))
        pprint(f"Which tag would you like to update {tag_options}")
        tag_index = int(input("? "))
        tag = tag_options[tag_index]
        tags[tag] = input(f"Input new value for {tag}: ")

        pprint(f"Are these tags acceptable? {tags}")
        exit = input("(y/n): ")
        if exit == 'y':
            return

def query_shazam(recognize_generator):
    mp3_json = next(recognize_generator) # current offset & shazam response to recognize requests
    print(mp3_json)
    return mp3_json

def setup_mp3_for_Shazam(mp3):
    mp3_file_content_to_recognize = open(mp3.path, 'rb').read()
    shazam = Shazam(mp3_file_content_to_recognize)
    recognize_generator = shazam.recognizeSong()
    return recognize_generator

def get_audio_tags_from_json(mp3_json):
    
    tags = {}

    track = mp3_json[1].get('track', {})
    tags["title"] = track.get('title')
    tags["artist"] = track.get('subtitle')

    images = track.get('images', {})

    if tags:
        tags['background'] = images.get('background', '')


    metadata = track.get("sections", [{}])[0].get('metadata')

    if metadata:
        tags["album"] = metadata[0]['text']
        tags["albumadamid"] = track.get("albumadamid")
        # tags["album_cover_url"] = track.get('share', {}).get('image') #we're gonna save this to album_artist

    return tags



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog = 'Set MP3 Tags',
                    description = 'Takes an MP3. Querries ShazamAPI to get the tags, and sets the tags')

    parser.add_argument("-d", "--directory", default='/home/jack/Music/mp3s/')
    parser.add_argument("-a", "--all_files_in_directory", action="store_true", default=True)
    parser.add_argument("-o", "--overwrite_tags", action="store_true", default=False)
    parser.add_argument("-s", "--skip_manual_verification", action="store_true", default=False)
    parser.add_argument("-f", "--filename")

    args = parser.parse_args()

    if args.all_files_in_directory:
        # get all mp3 objects
        mp3s = get_mp3s(args.directory)
    else: 
        mp3s = [eyed3.load(args.directory + args.filename)]

    
    # filter out mp3s that already have tags, unless we want to overwrite them
    mp3s = [mp3 for mp3 in mp3s if not has_tags(mp3)] if not args.overwrite_tags else mp3s
        
    for i, mp3 in enumerate(mp3s):
        print(f"File {i} of {len(mp3s)}")
        print(f"Grabbing tags for {mp3}")
        
        recognize_generator = setup_mp3_for_Shazam(mp3)
        mp3_json = query_shazam(recognize_generator) # current offset & shazam response to recognize requests
        tags = get_audio_tags_from_json(mp3_json)

        # if you just wanna trust shazam to get it right
        if not args.skip_manual_verification:
            skip_file = manual_tag_verification(mp3, tags)
            if skip_file:
                continue
        set_mp3_tags(mp3, False, tags)