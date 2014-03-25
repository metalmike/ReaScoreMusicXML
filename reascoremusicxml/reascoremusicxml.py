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

from Tkinter import *
import Tkinter

from music21 import stream, metadata, note, clef, midi


def msg(m) :
    s = str(m) + '\n'
    RPR_ShowConsoleMsg(s)


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
    msg(trackItemCount)
 
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

    for i, rpr_chunk in enumerate(chunkLists):
        for j, rpr_chunk_part in enumerate(rpr_chunk):
            if rpr_chunk_part.startswith("HASDATA "):
                if (ticksPerQuarterNote == None):
                    ticksPerQuarterNote = rpr_chunk_part.split(" ")[2]
                elif (ticksPerQuarterNote == rpr_chunk_part.split(" ")[2]):
                    pass
                else:
                    raise("Different ticksPerQuarterNote in chunks! - Not supported!")
                
            if rpr_chunk_part.startswith("E ")  or rpr_chunk_part.startswith("e "):
                midiEventListRaw.append(rpr_chunk_part.split(" ")[1:])
    return ticksPerQuarterNote, midiEventListRaw
        
        
def Generate():
    rpr_chunk = ""
    rpr_chunkLists = []
    
    s1 = stream.Score()
    s1.metadata = metadata.Metadata()
    s1.metadata.composer = 'Mike'
    s1.metadata.title='Reaper Symphony'
    s1.metadata.popularTitle='Silent Death'
    s1.metadata.date = '2014'
    
    #TODO: Loop over tracks
    p1 = stream.Part()
    p1.id = 'myBass'

    rpr_trackList = getSelectedTracksIdList()
    GetTrackName(rpr_trackList[0])
    
    rpr_track_ItemIdL = getTrackItemsIdList(rpr_trackList[0])
    for rpr_track_ItemId in rpr_track_ItemIdL:
        rpr_chunk = RPR_GetSetItemState2(rpr_track_ItemId, "", 1024*1024*4, 1)[2]
        rpr_chunkLists.append(list(rpr_chunk.split("\n")))
 
    #midiStream = stream.Part()
    #midi.translate.midiStringToStream("", midiStream)
    
    ticksPerQuarterNote, midiEventListRaw = chunk_parser(rpr_chunkLists)    

    msg(ticksPerQuarterNote)
    msg(midiEventListRaw)
    
    
    n1 = note.Note('g3', type='half')
    n2 = note.Note('d4', type='half')
    
    #cf1 = clef.AltoClef()
    
    m1 = stream.Measure(number=1)
    m1.append([n1, n2])
    #m1.insert(0, cf1)
   
    p1.append(m1)
    s1.append(p1)
    
    #s1.show('musicxml') 
    #s1.show('text')



root = Tkinter.Tk()

root.title('ReaScoreMusicXML')
root.resizable(0, 0)
root.minsize(width=300, height=100)

var1 = IntVar()
Checkbutton(root, text="Tabulature", variable=var1).grid(row=1, sticky=W)

#var2 = IntVar()
#Checkbutton(root, text="Remove Source Item (Move)", variable=var2).grid(row=2, sticky=W)

Button(root, text ="Generate", command = Generate).place(bordermode=INSIDE, height=25, width=60, x=135, y=55)

root.mainloop()

if __name__ == '__main__':
    pass