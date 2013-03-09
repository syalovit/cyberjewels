'''
Created on Feb 2, 2013

@author: ruslana
'''


rate= [0,0,0,0,0,0,0,0,0,0];                    # used to hold last ten IBI values
sampleCounter = 0;          # used to determine pulse timing
lastBeatTime = 0;           # used to find the inter beat interval
P =700;                      # used to find peak in pulse wave
T = 700;                     # used to find trough in pulse wave
thresh = 700;                # used to find instant moment of heart beat
amp = 100;                   # used to hold amplitude of pulse waveform
firstBeat = True;           # used to seed rate array so we startup with reasonable BPM
secondBeat = True;       # used to seed rate array so we startup with reasonable BPM
IBI = 600;             # holds the time between beats, the Inter-Beat Interval
Pulse = False;     # true when pulse wave is high, false when it's low
QS = False;        # becomes true when Arduoino finds a beat.


def process_sample(reading):    
    Signal = reading 
    sampleCounter += 2;                         
    N = sampleCounter - lastBeatTime;       # monitor the time since the last beat to avoid noise

    # find the peak and trough of the pulse wave
    if (Signal < thresh) and (N > (IBI/5)*3):       # avoid dichrotic noise by waiting 3/5 of last IBI
        if Signal < T:                       # T is the trough
            T = Signal;                         # keep track of lowest point in pulse wave 
      
    if (Signal > thresh) and (Signal > P):          # thresh condition helps avoid noise
        P = Signal;                             # P is the peak
                                               # keep track of highest point in pulse wave
    
  #  NOW IT'S TIME TO LOOK FOR THE HEART BEAT
  # signal surges up in value every time there is a pulse
    if N > 250:                                   # avoid high frequency noise
        if ( (Signal > thresh) and (Pulse == False) and (N > (IBI/5)*3) ):        
            Pulse = True;                             # set the Pulse flag when we think there is a pulse
            IBI = sampleCounter - lastBeatTime;       # measure time between beats in mS
            lastBeatTime = sampleCounter;             # keep track of time for next pulse
         
            if firstBeat:                         # if it's the first time we found a beat, if firstBeat == TRUE
                firstBeat = False;                # clear firstBeat flag
                return;                           # IBI value is unreliable so discard it
            
            if secondBeat:                        # if this is the second beat, if secondBeat == TRUE
                secondBeat = False;               # clear secondBeat flag
                for i in range(9):                # seed the running total to get a realisitic BPM at startup
                    rate[i] = IBI;                      
                    
            
          
            # keep a running total of the last 10 IBI values
            runningTotal = 0;                   # clear the runningTotal variable    

            for i in range(8):                  # shift data in the rate array
                rate[i] = rate[i+1];            # and drop the oldest IBI value 
                runningTotal += rate[i];        # add up the 9 oldest IBI values
        
        
            rate[9] = IBI;                      # add the latest IBI to the rate array
            runningTotal += rate[9];            # add the latest IBI to runningTotal
            runningTotal /= 10;                 # average the last 10 IBI values 
            BPM = 60000/runningTotal;           # how many beats can fit into a minute? that's BPM!
            return BPM,IBI 
    # QS FLAG IS NOT CLEARED INSIDE THIS ISR
                           


    if (Signal < thresh) and (Pulse == True):    # when the values are going down, the beat is over        
        Pulse = False;                           # reset the Pulse flag so we can do it again
        amp = P - T;                            # get amplitude of the pulse wave
        thresh = amp/2 + T;                     # set thresh at 50% of the amplitude
        P = thresh;                            # reset these for next time
        T = thresh;
        
    if (N > 2500):                             # if 2.5 seconds go by without a beat
        thresh = 512;                          # set thresh default
        P = 512;                               # set P default
        T = 512;                               # set T default
        lastBeatTime = sampleCounter;          # bring the lastBeatTime up to date        
        firstBeat = True;                        # set these to avoid noise
        secondBeat = True;                     # when we get the heartbeat back
        
    return None,None
