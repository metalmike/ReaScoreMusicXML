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

from music21 import stream


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
    stream1 = stream.Stream()
    TrackList = getSelectedTracksIdList()
    GetTrackName(TrackList[0])
    
    stream1.show('musicxml') 
    #sBach = corpus.parse('bach/bwv7.7')
    #sBach.show()
    #RPR_Main_OnCommand(40007,0)



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