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


from music21 import stream, metadata, midi, meter, tempo
#from music21 import *
    

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

def get_numTempoTimeSigMarker(): 
    return RPR_CountTempoTimeSigMarkers(-1)


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


def getProjectBeat():
    temp = RPR_TimeMap2_timeToBeats(-1, 0, 0, 0, 0, 0)
    msg('RPR_TimeMap2_timeToBeats: ' + str(temp))
    '''e.g. for 6/8 and 130bpm: RPR_TimeMap2_timeToBeats: (1e-11, -1, 0, 0, 6, 0.0, 8)'''
    beatNumerator = temp[4]
    beatDenumerator = temp [6]
    return beatNumerator, beatDenumerator 


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
                
                deltaTime = float(0)
                if (chunk_pos > markerActual):
                    deltaTime = chunk_pos - markerActual
                    msg('deltaTime:' + str(deltaTime))
                    
                    deltaBeats = float(RPR_TimeMap2_timeToBeats(-1, deltaTime,0,0,0,0)[0])
                    """convert a time into beats.
                    if measures is non-NULL, measures will be set to the measure count, return value will be beats since measure.
                    if cml is non-NULL, will be set to current measure length in beats (i.e. time signature numerator)
                    if fullbeats is non-NULL, and measures is non-NULL, fullbeats will get the full beat count (same value returned if measures is NULL).
                    if cdenom is non-NULL, will be set to the current time signature denominator.
                    double TimeMap2_timeToBeats(ReaProject* proj, double tpos, int* measures, int* cml, double* fullbeats, int* cdenom)"""
                    
                    msg('RPR_TimeMap2_timeToBeats:' + str(int(deltaBeats)))
                                
            if rpr_chunk_part.startswith("LENGTH "):
                chunk_lenght = float(rpr_chunk_part.split(" ")[1])
                msg('Chunk len:' + str(chunk_lenght))

            if rpr_chunk_part.startswith("HASDATA "):
                if (ticksPerQuarterNote == None):
                    ticksPerQuarterNote = rpr_chunk_part.split(" ")[2]
                elif (ticksPerQuarterNote == rpr_chunk_part.split(" ")[2]):
                    pass
                else:
                    raise("Different ticksPerQuarterNote in chunks! - Not supported!")
                
            rpr_chunk_part = rpr_chunk_part.lower()
            if rpr_chunk_part.startswith("e "):
                rawEvent = rpr_chunk_part.lstrip("e ")
                
                '''If there's a gap between two chunks, the delta time of the first chunk event,
                must be replaced by the time of the gap (in beats*ticksPerQuarterNote)'''
                if (deltaTime != 0) :
                    rawEvent = rawEvent.split(' ')
                    rawEvent[0] = str(int(deltaBeats)*int(ticksPerQuarterNote))
                    rawEvent = ' '.join(rawEvent)
                    
                    deltaTime = 0
                    
                midiEventListRaw.append(rawEvent)
                
                
        markerActual = chunk_pos + chunk_lenght
        msg('markerActual:' + str(markerActual))
                
    return ticksPerQuarterNote, midiEventListRaw
        
        
def Generate():
    
    #s1 = extractedScore
    s1 = stream.Score()
    s1.metadata = metadata.Metadata()
    s1.metadata.composer = 'Mike'
    
    projectFilename = get_curr_project_filename()
    s1.metadata.title = projectFilename.split(".")[0].split('\\')[-1]
    
    s1.metadata.popularTitle='Silent Death'
    s1.metadata.date = '2014'
    
    #TODO: extract this in seperate methos and return a list!
    numTempoTimeSigMarker = get_numTempoTimeSigMarker()
    msg('numTempoTimeSigMarker: ' + str(numTempoTimeSigMarker))

    if (numTempoTimeSigMarker != 0):
        for marker in range(numTempoTimeSigMarker): 
            #(Boolean retval, ReaProject* proj, Int ptidx, Float timeposOut, Int measureposOut, Float beatposOut, Float bpmOut, Int timesig_numOut, Int timesig_denomOut, Boolean lineartempoOut) = RPR_GetTempoTimeSigMarker(proj, ptidx, timeposOut, measureposOut, beatposOut, bpmOut, timesig_numOut, timesig_denomOut, lineartempoOut)
            temp =  RPR_GetTempoTimeSigMarker(0, marker, 0, 0, 0, 0, 0, 0, 0)
            msg('MarkerArray: ' + str(temp))


    '''
    Python: (ReaProject* proj, Float bpmOut, Float bpiOut) = RPR_GetProjectTimeSignature2(proj, bpmOut, bpiOut)
    
    Gets basic time signature (beats per minute, numerator of time signature in bpi)
    this does not reflect tempo envelopes but is purely what is set in the project settings.
    e.g. for 6/8 and 130bpm: RPR_GetProjectTimeSignature2: (-1, 260.0, 6.0)'''
    #temp =  RPR_GetProjectTimeSignature2(-1, 0, 0)
    #msg('RPR_GetProjectTimeSignature2: ' + str(temp))
    

    #retval = float(RPR_TimeMap2_beatsToTime(-1, 0, 0)[0])
    #msg('RPR_TimeMap2_beatsToTime:' + str(retval))
    
    DividedBpmAtTime = RPR_TimeMap_GetDividedBpmAtTime(0)
    msg('RPR_TimeMap_GetDividedBpmAtTime: ' + str(DividedBpmAtTime))
    

    rprProjBeatNumerator, rprProjBeatDenumerator = getProjectBeat()
    msg('ProjectBeat: %s' % rprProjBeatNumerator + '/%s' % rprProjBeatDenumerator)
    scoreBeats = meter.TimeSignature('%s' % rprProjBeatNumerator + '/%s' % rprProjBeatDenumerator)
    s1.insert(0, scoreBeats)
    
    projectTempo = DividedBpmAtTime * 4 / int(rprProjBeatDenumerator)
    msg('projectTempo: ' + str(projectTempo))
    metro = tempo.MetronomeMark(number = projectTempo)
    #metro.setContextAttr(attrName, value)
    #d = Direction()
    #d.set('placement', 'above')

    #d.append(metro)
    
    #TODO: extract tempo from reaper project and set it in music21    
    
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
        
        ScorePart.insert(0, metro)

        s1.insert(0, ScorePart)
    
    return s1


class GUIApplication:
    
    def __init__(self, root):
        self.root = root
        
        self.frame = Frame(self.root)
        self.frame.pack()
        
        self.root.title('ReaScoreMusicXML')
        self.root.resizable(0, 0)
        self.root.minsize(width=300, height=100)
        self.root.attributes('-topmost', 1)
        
        self.extractedData = None
        
        self.buildGUI()
        
        
    def buildGUI(self):
        self.var1 = IntVar()
        self.extractCheckBox = Checkbutton(self.frame, text="Extract data from Project", variable=self.var1)
        self.extractCheckBox.select()
        
        self.var2 = IntVar()
        self.processCheckBox = Checkbutton(self.frame, text="Export extracted data to MusicXML", variable=self.var2)^
        self.processCheckBox.select()
        
        self.extractCheckBox.pack()
        self.processCheckBox.pack()
        
        #self.quitButton = Button(self.frame, text="QUIT", fg="red", command=self.root.quit)       
        self.genButton = Button(self.frame, text ="Generate", command = self.process)

        #self.quitButton.pack(side = LEFT)
        self.genButton.pack()
        
            
    def exportData(self):
        self.extractedData.show()
        
            
    def process(self): 
        if (self.var1.get() == 1):
            self.extractedData = Generate()
            
        if (self.var2.get() == 1):
            self.exportData()



#TODO: Unittests
if __name__ == '__main__':
    root = Tk()
    app = GUIApplication(root)
    root.mainloop()
