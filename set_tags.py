import eyed3
from os import listdir
from ShazamAPI import Shazam
import argparse
from pprint import pprint

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

    if mp3.tag.title is None:
        mp3.tag.title = tags.get("title") 

    if mp3.tag.artist is None:
        mp3.tag.artist = tags.get("artist")

    if mp3.tag.album is None:
        mp3.tag.album = tags.get("album")

    if mp3.tag.cd_id is None:
        mp3.tag.album_artist = str(tags.get('albumadamid'))

    if set_track_num and mp3.tag.track_num is None:
        mp3.tag.track_num = tags.get('track_num')

    mp3.tag.save()

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

def get_audio_tags(mp3):
    mp3_file_content_to_recognize = open(mp3.path, 'rb').read()
    shazam = Shazam(mp3_file_content_to_recognize)
    recognize_generator = shazam.recognizeSong()

    mp3_recognizer = next(recognize_generator) # current offset & shazam response to recognize requests

    tags = {}

    track = mp3_recognizer[1].get('track', {})
    tags["title"] = track.get('title')
    tags["artist"] = track.get('subtitle')
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

    parser.add_argument("-d", "--directory", default='/home/jack/Music/jack/mp3s/')
    parser.add_argument("-a", "--all_files_in_directory", action="store_true", default=True)
    parser.add_argument("-o", "--overwrite_tags", action="store_true", default=False)
    parser.add_argument("-f", "--filename")
    args = parser.parse_args()


    if args.all_files_in_directory:
        # get all mp3 objects
        mp3s = get_mp3s(args.directory)
        # filter out mp3s that already have tags, unless we want to overwrite them
        mp3s = [mp3 for mp3 in mp3s if not has_tags(mp3)] if not args.overwrite_tags else mp3s
        
        for mp3 in mp3s:
            # print(help(mp3))
            # crash
            print(f"Grabbing tags for {mp3}")

            tags = get_audio_tags(mp3)
            
            print(f"The tags found for {mp3} were \n title: {tags.get('title')} \n artist: {tags.get('artist')} \n album: {tags.get('album')}")
            response = input("Are these correct (y/n): ")
            if response != 'y':
              response = input(f"Update Tags 'u' \nContinue to next file 'Enter'\n?")
              if response == 'u':
                manual_set_new_tag(tags)
              else:
                print(f"skipping file {mp3}")
                continue

            set_mp3_tags(mp3, False, tags)

    else:
        mp3 = eyed3.load(args.directory + args.filename)
        tags = get_audio_tags(mp3)
        
        set_mp3_tags(mp3, False, tags
          )

        
