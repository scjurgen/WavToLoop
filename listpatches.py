#!/usr/bin/env python3

import os.path
import sys
import re
import uuid
import shutil


def run_main():
    prefix_path = sys.argv[1]
    for i in range(100):
        nr = str(i).zfill(2) 
        path = prefix_path + "/Patch" + nr
        try:
            with open(path+"/patch.xml", 'r') as file:
                data = file.read().replace('\n', '').replace('\r','')
            try:
                name = ""
                bpm = 0
                beats = 0
                res = re.search('<PatchName>(.*)</PatchName>', data, re.IGNORECASE)
                if res:
                    name = res.group(1)
                else:
                    print("not found")
                with open(path+"/PhraseA/phrase.xml", 'r') as file:
                    data = file.read().replace('\n', '').replace('\r','')
                try:
                    res = re.search('<BeatsPerMinute>(.*)</BeatsPerMinute>', data, re.IGNORECASE)
                    if res:
                        bpm = res.group(1)
                except:
                    pass
                try:
                    res = re.search('<BeatsPerMeasure>(.*)</BeatsPerMeasure>', data, re.IGNORECASE)
                    if res:
                        beats = res.group(1)
                except:
                    pass
                print("#{nr:2} {bpm}\t{beats}\t{title}".format(nr=nr, title=name, bpm=bpm, beats=beats))
            except Exception as e:
                print(e)
        except:
            pass

if __name__ == "__main__":
    run_main()


