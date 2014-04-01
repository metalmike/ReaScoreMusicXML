'''
Created on 20.03.2014

@author: Michael
'''
import sys
sys.argv=["Main"]

#from Chunkparser import *

from reaper_python import *
#from sws_python import *
#import re
#from ctypes import *

from Tkinter import *
import Tkinter

from music21 import stream, metadata, midi


def msg(m) :
    s = str(m) + '\n'
    RPR_ShowConsoleMsg(s)


def get_curr_project_filename():
    proj = RPR_EnumProjects(-1, "", 512)
    if proj[2] == "":
        msg("Unsaved project")
    else:
        msg(proj[2])
        return (proj[2])
    

def getSelectedTracksIdList():
    'Returns a list of the selected Tracks'
    trackIdL = []
    selTrackCount = RPR_CountSelectedTracks(0)
    
    if selTrackCount == 0:
##        msg("Select tracks first")
        return 0
    for i in range(selTrackCount):
        trackId = RPR_GetSelectedTrack(0, i)
        trackIdL.append(trackId)
    
    return trackIdL


def getTrackItemsIdList(trackId):
    'Returns a list of the items in a track'
    itemIdL = []
    trackItemCount = RPR_CountTrackMediaItems(trackId)
    #msg(trackItemCount)
 
    if trackItemCount == 0:
        msg("No item(s) in track\n")
        return 0
    for i in range(trackItemCount):
        itemId = RPR_GetTrackMediaItem(trackId, i)
        itemIdL.append(itemId)
    return itemIdL


def GetTrackName(trackId):
    currentName = str(RPR_GetSetMediaTrackInfo_String(trackId, "P_NAME", "", 0)[3])
    msg(currentName)
    return currentName


def chunk_parser(chunkLists):
    midiEventListRaw = []
    ticksPerQuarterNote = None

    chunk_pos = float(0)
    chunk_lenght = float(0)
    markerActual = float(0)

    for i, rpr_chunk in enumerate(chunkLists):
        
        for j, rpr_chunk_part in enumerate(rpr_chunk):
            
            if rpr_chunk_part.startswith("POSITION "):
                chunk_pos = float(rpr_chunk_part.split(" ")[1])
                msg('Chunk pos:' + str(chunk_pos))
                
                #retval = float(RPR_TimeMap2_beatsToTime(-1, chunk_pos, 0)[0])
                #msg('RPR_TimeMap2_beatsToTime:' + str(retval))
                
                #DividedBpmAtTime = RPR_TimeMap_GetDividedBpmAtTime(chunk_pos)
                #msg('RPR_TimeMap_GetDividedBpmAtTime:' + str(DividedBpmAtTime))
                deltaTime = float(0)
                if (chunk_pos > markerActual):
                    deltaTime = chunk_pos - markerActual
                    msg('deltaTime:' + str(deltaTime))
                    
                    TimetoBeats = float(RPR_TimeMap2_timeToBeats(-1, deltaTime,0,0,0,0)[0])
                    """convert a time into beats.
                    if measures is non-NULL, measures will be set to the measure count, return value will be beats since measure.
                    if cml is non-NULL, will be set to current measure length in beats (i.e. time signature numerator)
                    if fullbeats is non-NULL, and measures is non-NULL, fullbeats will get the full beat count (same value returned if measures is NULL).
                    if cdenom is non-NULL, will be set to the current time signature denominator.
                    double TimeMap2_timeToBeats(ReaProject* proj, double tpos, int* measures, int* cml, double* fullbeats, int* cdenom)"""
                    
                    msg('RPR_TimeMap2_timeToBeats:' + str(int(TimetoBeats)))
                    #midiEventListRaw.append(TimetoBeats*ticksPerQuarterNote'')
                
                
            if rpr_chunk_part.startswith("LENGTH "):
                chunk_lenght = float(rpr_chunk_part.split(" ")[1])
                msg('Chunk len:' + str(chunk_lenght))

            if rpr_chunk_part.startswith("HASDATA "):
                if (ticksPerQuarterNote == None):
                    ticksPerQuarterNote = rpr_chunk_part.split(" ")[2]
                    if (deltaTime != 0) :
                        midiEventListRaw.append(str(int(TimetoBeats)*int(ticksPerQuarterNote)) + ' 80 31 0')
                elif (ticksPerQuarterNote == rpr_chunk_part.split(" ")[2]):
                    pass
                else:
                    raise("Different ticksPerQuarterNote in chunks! - Not supported!")
                
            rpr_chunk_part = rpr_chunk_part.lower()
            if rpr_chunk_part.startswith("e "):
                midiEventListRaw.append(rpr_chunk_part.lstrip("e "))
                
        markerActual = chunk_pos + chunk_lenght
        msg('markerActual:' + str(markerActual))
                
    return ticksPerQuarterNote, midiEventListRaw
        
        
def Generate():
    
    s1 = stream.Score()
    s1.metadata = metadata.Metadata()
    s1.metadata.composer = 'Mike'
    
    projectFilename = get_curr_project_filename()
    s1.metadata.title = projectFilename.split(".")[0].split('\\')[-1]
    
    s1.metadata.popularTitle='Silent Death'
    s1.metadata.date = '2014'
    
    rpr_trackList = getSelectedTracksIdList()
    
    for track in rpr_trackList:
        rpr_chunk = ""
        rpr_chunkLists = []
        ScorePart = stream.Part()

        GetTrackName(track)
        ScorePart.id = 'myBass'
        
        rpr_track_ItemIdL = getTrackItemsIdList(track)
        for rpr_track_ItemId in rpr_track_ItemIdL:
            rpr_chunk = RPR_GetSetItemState2(rpr_track_ItemId, "", 1024*1024*4, 1)[2]
            #msg(rpr_chunk)
            rpr_chunkLists.append(list(rpr_chunk.split("\n")))
         
        ticksPerQuarterNote, midiEventListRaw = chunk_parser(rpr_chunkLists)    
    
        msg(ticksPerQuarterNote)
        msg(midiEventListRaw)
        
        midiTrack = []
        midiTrack.append(midiEventListRaw)
      
        midiBinStr = midi.translate.midiAsciiStringToBinaryString(tracksEventsList = midiTrack)
        ScorePart = midi.translate.midiStringToStream(midiBinStr, ScorePart)
        
        s1.insert(0, ScorePart)
        
    
    s1.show('musicxml') 
    #s1.show('text')



root = Tkinter.Tk()

root.title('ReaScoreMusicXML')
root.resizable(0, 0)
root.minsize(width=300, height=100)

var1 = IntVar()
#Checkbutton(root, text="Tabulature", variable=var1).grid(row=1, sticky=W)

#var2 = IntVar()
#Checkbutton(root, text="Remove Source Item (Move)", variable=var2).grid(row=2, sticky=W)

Button(root, text ="Generate", command = Generate).place(bordermode=INSIDE, height=25, width=60, x=135, y=55)

root.mainloop()

if __name__ == '__main__':
    pass