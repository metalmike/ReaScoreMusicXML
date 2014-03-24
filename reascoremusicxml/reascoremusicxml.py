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

from music21 import stream, metadata, note, clef


def msg(m) :
    s = str(m) + '\n'
    RPR_ShowConsoleMsg(s)

'Returns a list of the selected Tracks'
def getSelectedTracksIdList():
    trackIdL = []
    selTrackCount = RPR_CountSelectedTracks(0)

    if selTrackCount == 0:
##        msg("Select tracks first")
        return 0
    for i in range(selTrackCount):
        trackId = RPR_GetSelectedTrack(0, i)
        trackIdL.append(trackId)
        return trackIdL


def GetTrackName(trackId):
    currentName = str(RPR_GetSetMediaTrackInfo_String(trackId, "P_NAME", "", 0)[3])
    msg(currentName)
    return currentName
    
    
def Generate():
    rpr_chunk = ""
    rpr_chunkLists = []
    rpr_track_ItemIdL = []    
    
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
    rpr_itemsInTrack = RPR_CountTrackMediaItems(rpr_trackList[0])
    msg(rpr_itemsInTrack)
    
    rpr_track_ItemId = RPR_GetTrackMediaItem(rpr_trackList[0], 0)
    rpr_track_ItemIdL.append(rpr_track_ItemId)
    
    #rpr_chunk_test = RPR_GetSetItemState2(rpr_track_ItemId, "", 1024*1024*4, 1)
    rpr_chunk = RPR_GetSetItemState2(rpr_track_ItemId, "", 1024*1024*4, 1)[2]
    rpr_chunkLists.append(list(rpr_chunk.split("\n")))
    
    #i = ""
    for rpr_chunk_part in rpr_chunk.split("\n"):
        if rpr_chunk_part.startswith("E "):
            msg(rpr_chunk_part)
    
    
    
    n1 = note.Note('g3', type='half')
    n2 = note.Note('d4', type='half')
    
    cf1 = clef.AltoClef()
    
    m1 = stream.Measure(number=1)
    m1.append([n1, n2])
    m1.insert(0, cf1)
   
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