#!/usr/bin/env python3
import os
import re
import sys
import os.path
import uuid
import shutil

import subprocess

def is_an_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def save_patch_xml(target, name, wave_id, description, stop_mode='StopInstantly'):
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
 <JamManPatch device="JamManStereo" version="1" xmlns="http://schemas.digitech.com/JamMan/Patch">
   <PatchName>{patchname}</PatchName>
   <RhythmType>Silence</RhythmType>
   <StopMode>{stopmode}</StopMode>
   <SettingsVersion>0</SettingsVersion>
   <ID>{waveid}</ID>
   <Metadata>
     <Description>{description}</Description>
     <Artist></Artist>
     <Genre>Unspecified</Genre>
     <Rating>0</Rating>
     <Tags></Tags>
   </Metadata>
 </JamManPatch>'''.format(patchname=name, waveid=wave_id, description=description, stopmode=stop_mode)
    with open(target, "w") as text_file:
        print(xml, file=text_file)


def save_phrase_xml(target, bpm, beats_per_measure, loop, reversed, wave_id):
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
 <JamManPhrase xmlns="http://schemas.digitech.com/JamMan/Phrase" version="1">
   <BeatsPerMinute>{bpm}</BeatsPerMinute>
   <BeatsPerMeasure>{beats}</BeatsPerMeasure>
   <BpmValidated>1</BpmValidated>
   <IsLoop>{loop}</IsLoop>
   <IsReversed>{reversed}</IsReversed>
   <SettingsVersion>0</SettingsVersion>
   <AudioVersion>0</AudioVersion>
   <ID>{waveid}</ID>
 </JamManPhrase>'''.format(bpm=bpm, beats=beats_per_measure, waveid=wave_id, loop=loop, reversed=reversed)
    #print(xml)
    with open(target, "w") as text_file:
        print(xml, file=text_file)


def usage():
    print("Usage: firstIndex sourceDirectory")
    exit(1)


def save_patch(main_dir, index, file_name, bpm, nominator, denominator, stopmode, loop, reversed, title):
    wave_id = str(uuid.uuid1())
    if not os.path.exists(main_dir):
        os.mkdir(main_dir)
    patch_dir = "{0}/Patch{1:0>2}".format(main_dir, index)
    try:
        os.mkdir(patch_dir)
    except:
        pass
    wave_dir = patch_dir + "/PhraseA"
    try:
        os.mkdir(wave_dir)
    except:
        pass
    print(patch_dir)
    save_patch_xml(patch_dir + "/patch.xml", title, wave_id, "copied from pc", stopmode)
    save_phrase_xml(wave_dir + "/phrase.xml",  bpm, nominator, '1', '0', wave_id)
    shutil.copy2(file_name, wave_dir+"/phrase.wav")


def cut_patch(wavefile, resultfile, bpm, nominator, denominator, cutfrom, measures):
    start = cutfrom * nominator * 4 / denominator  * 60.0 / bpm
    length = measures * nominator * 4 / denominator * 60.0 / bpm
    cmd = "sox {source} -r 44100 -c 2 --norm {target} trim {start} {length}".format(source=wavefile, target=resultfile, start=start, length=length)
    print(cmd)
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        return 0
    output_received = ""
    while True:
        line = process.stdout.readline()
        if len(line) == 0 and process.poll() != None:
            break
        v = line.decode('utf-8')
        output_received += v
    return "1 received" in output_received


def create_patch(target_dir, index, wave_file, result_file, **kwargs):
    bpm = int(kwargs['bpm'])
    cut = True
    try:
        cut_from = int(kwargs['fromPos'])-1
    except:
        cut_from = 0
    measures = int(kwargs['measures'])
    nominator = int(kwargs['nominator'])
    denominator = int(kwargs['denominator'])
    is_loop = '1'
    is_reversed = '0'
    stop_mode = "StopInstantly"
    #print("cutfrom={0} for {1}".format(cut_from, measures))

    cut_patch(wave_file, result_file, bpm, nominator, denominator, cut_from, measures)
    save_patch(target_dir, index, result_file, bpm, nominator, denominator, stop_mode, is_loop, is_reversed, kwargs['title'])


def run_main():

    list_of_files = []

    start_path = sys.argv[2]
    index = int(sys.argv[1])
    target_path = "JamManStereo"

    for path, dirs, files in os.walk(start_path):
        for file_name in files:
            if file_name.endswith(".wav"):
                list_of_files.append(os.path.join(path, file_name))
    list_of_files.sort()
    print(list_of_files)
    for p in list_of_files:
        '''
        filesyntax:
        name _ nominator _ denominator[24168] _ bpm'bpm' _ measurelength {cutfrom,} 
        i.e.: funk#1_4_4_100bpm_8_1,9,25,41,57.wav        
        '''
        filename = os.path.split(p)
        print(filename[1])
        pattern_search = re.match('([A-Z0-9a-z#_-]*)_([0-9]+)_([24168]+)_([0-9]+)bpm_([0-9]+)_([0-9,]+).wav',
                                  filename[1], re.IGNORECASE)
        if pattern_search:
            cutFrom = [int(x) for x in pattern_search.group(6).split(",")]
        else:
            pattern_search = re.match('([A-Z0-9a-z_#-]*)_([0-9]+)_([24168]+)_([0-9]+)bpm_([0-9]+).wav', filename[1],
                                  re.IGNORECASE)
            if pattern_search:
                cutFrom = [0,]
            else:
                print("WARNING! Couldn't parse:" + filename[1])
                break
        title = pattern_search.group(1)
        orgtitle = title
        nominator = int(pattern_search.group(2))
        denominator = int(pattern_search.group(3))
        bpm = int(pattern_search.group(4))
        #bpm needs to be adapted for the jamman for rhythms with 8th or 16th denomin`ator (i.e. 6/8 11/16)
        title = title.replace('_', ' ')
        measures = pattern_search.group(5)
        for fromPosition in cutFrom:
            print("Title='{}' {}/{} bpm={} measures={} from={}".format(title, nominator, denominator, bpm, measures, fromPosition))
            titleSet = "{title} {n}/{d}".format(title=title, n=nominator, d=denominator)
            pre, ext = os.path.splitext(filename[1])
            tmp_file = filename[0] + "/tmp/" + orgtitle + "/" + orgtitle + "_" + str(bpm) + "_" + str(fromPosition) + ".wav"
            if not os.path.exists(filename[0] + "/tmp/" + orgtitle):
                os.mkdir(filename[0] + "/tmp/" + orgtitle)

            create_patch(target_path, index, p, tmp_file, bpm=bpm, title=titleSet, nominator=nominator, denominator=denominator,
                         fromPos=fromPosition, measures=measures)
            index += 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
    run_main()


