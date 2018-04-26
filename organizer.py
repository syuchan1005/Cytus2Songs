import json
import os
import sys
import shutil

import mutagen.id3
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TRCK, TCON
from mutagen.mp3 import MP3
from pydub import AudioSegment


def WAVtoMP3(path: str):
    if path.endswith(".wav"):
        AudioSegment.from_wav(path).export(path[:-3] + "mp3", format="mp3", bitrate="320k")


def setMetaTag(filename, title, artist, album, track, track_album):
    audio = MP3(filename, ID3=ID3)
    try:
        audio.add_tags(ID3=ID3)
    except mutagen.id3.error:
        pass
    audio["TIT2"] = TIT2(encoding=3, text=title)
    audio["TPE1"] = TPE1(encoding=3, text=artist)
    audio["TALB"] = TALB(encoding=3, text=album)
    audio['TCON'] = TCON(encoding=3, text="Cytus 2")
    audio["TRCK"] = TRCK(encoding=3, text=[(track, track_album)])
    audio.save()


def print_progress_bar(iteration, total, decimals=1, length=60, fill='#', nofill='-',
                       prefix='Progress:', suffix='Complate'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + nofill * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end="")
    sys.stdout.flush()
    if iteration == total:
        print()


if __name__ == "__main__":
    print("Enter the resource path")
    dirPath = input()

    if not dirPath.endswith("\\"):
        dirPath = dirPath + "\\"

    total = 0
    step = 0
    print_progress_bar(step, total=1)

    for list in os.listdir(dirPath):
        listPath = dirPath + list
        if os.path.isdir(listPath):
            continue
        elif (not list.endswith(".wav")) or \
                os.path.getsize(listPath) // 1000000 <= 17:
            os.remove(listPath)
        else:
            total += 1
            s = list.split("-")
            if len(s) > 1:
                os.rename(listPath, dirPath + s[0] + ".wav")

    total *= 3
    total += 2
    print_progress_bar(step, total)

    jsonFile = open("./Cytus2Songs.json", "r", encoding="utf-8")
    jsonObject = json.load(jsonFile)
    characters = jsonObject["characters"]
    songs = jsonObject["songs"]
    step += 1
    print_progress_bar(step, total)

    for i, v in enumerate(characters):
        try:
            os.mkdir(dirPath + v["name"].replace(":", " "))
        except FileExistsError:
            pass
    step += 1
    print_progress_bar(step, total)

    for file in os.listdir(dirPath):
        step += 1
        print_progress_bar(step, total)
        fullPath = dirPath + file
        if os.path.isdir(fullPath):
            continue
        if file[:-4] not in songs:
            step += 2
            print_progress_bar(step, total)
            # os.remove(fullPath)
            continue
        if file[-3:] == "wav":
            step += 1
            print_progress_bar(step, total)
            WAVtoMP3(fullPath)
            os.remove(fullPath)
            fullPath = fullPath[:-3] + "mp3"
            step += 1
            print_progress_bar(step, total)
        data = songs[file[:-4]]
        character = characters[data["character"]]
        setMetaTag(fullPath, data["name"], data["artist"], character["name"], data["track"], character["track"])
        shutil.move(fullPath,
                    dirPath + character["name"].replace(":", " ") + "\\" + ("%02d" % data["track"]) + ". " + data[
                        "name"].replace(":", " ") + ".mp3")
