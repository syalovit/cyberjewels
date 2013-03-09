'''
Created on Jan 21, 2013

@author: ruslana
'''

'''
Created on Feb 2, 2013

@author: ruslana
'''

class ProcessSample:
    rate= [0,0,0,0,0,0,0,0,0,0];                    # used to hold last ten self.IBI values
    sampleCounter = 0;          # used to determine pulse timing
    lastBeatTime = 0;           # used to find the inter beat interval
    P =256;                      # used to find peak in pulse wave
    T = 256;                     # used to find trough in pulse wave
    thresh = 256;                # used to find instant moment of heart beat
    amp = 100;                   # used to hold amplitude of pulse waveform
    firstBeat = True;           # used to seed rate array so we startup with reasonable BPM
    secondBeat = True;       # used to seed rate array so we startup with reasonable BPM
    IBI = 600;             # holds the time between beats, the Inter-Beat Interval
    Pulse = False;     # true when pulse wave is high, false when it's low
    QS = False;        # becomes true when Arduoino finds a beat.

    def process_sample(self,reading):    
        Signal = reading 
        self.sampleCounter += 2;                         
        N = self.sampleCounter - self.lastBeatTime;       # monitor the time since the last beat to avoid noise
    
        # find the peak and trough of the pulse wave
        if (Signal < self.thresh) and (N > (self.IBI/5)*3):       # avoid dichrotic noise by waiting 3/5 of last self.IBI
            if Signal < self.T:                       # T is the trough
                self.T = Signal;                         # keep track of lowest point in pulse wave 
          
        if (Signal > self.thresh) and (Signal > self.P):          # self.thresh condition helps avoid noise
            self.P = Signal;                             # P is the peak
                                                   # keep track of highest point in pulse wave
        
      #  NOW IT'S TIME TO LOOK FOR THE HEART BEAT
      # signal surges up in value every time there is a pulse
        if N > 250:                                   # avoid high frequency noise
            if ( (Signal > self.thresh) and (self.Pulse == False) and (N > (self.IBI/5)*3) ):        
                self.Pulse = True;                             # set the Pulse flag when we think there is a pulse
                self.IBI = self.sampleCounter - self.lastBeatTime;       # measure time between beats in mS
                self.lastBeatTime = self.sampleCounter;             # keep track of time for next pulse
             
                if self.firstBeat:                         # if it's the first time we found a beat, if firstBeat == TRUE
                    self.firstBeat = False;                # clear firstBeat flag
                    return;                           # self.IBI value is unreliable so discard it
                
                if self.secondBeat:                        # if this is the second beat, if secondBeat == TRUE
                    self.secondBeat = False;               # clear secondBeat flag
                    for i in range(9):                # seed the running total to get a realisitic BPM at startup
                        self.rate[i] = self.IBI;                      
                        
                
              
                # keep a running total of the last 10 self.IBI values
                runningTotal = 0;                   # clear the runningTotal variable    
    
                for i in range(8):                  # shift data in the rate array
                    self.rate[i] = self.rate[i+1];            # and drop the oldest self.IBI value 
                    runningTotal += self.rate[i];        # add up the 9 oldest self.IBI values
            
            
                self.rate[9] = self.IBI;                      # add the latest self.IBI to the rate array
                runningTotal += self.rate[9];            # add the latest self.IBI to runningTotal
                runningTotal /= 10;                 # average the last 10 self.IBI values 
                BPM = (60000/runningTotal);           # how many beats can fit into a minute? that's BPM!
                return BPM,self.IBI 
        # QS FLAG IS NOT CLEARED INSIDE THIS ISR
                               
    
    
        if (Signal < self.thresh) and (self.Pulse == True):    # when the values are going down, the beat is over        
            self.Pulse = False;                           # reset the Pulse flag so we can do it again
            self.amp = self.P - self.T;                            # get amplitude of the pulse wave
            self.thresh = self.amp/2 + self.T;                     # set self.thresh at 50% of the amplitude
            self.P = self.thresh;                            # reset these for next time
            self.T = self.thresh;
            
        if (N > 2500):                             # if 2.5 seconds go by without a beat
            self.thresh = 256;                          # set self.thresh default
            self.P = 256;                               # set P default
            self.T = 256;                               # set T default
            self.lastBeatTime = self.sampleCounter;          # bring the self.lastBeatTime up to date        
            self.firstBeat = True;                        # set these to avoid noise
            self.secondBeat = True;                     # when we get the heartbeat back
            
        return None,None




def main():
    


    import socket
    host = '' 
    port = 3054  
    backlog = 5 
    size = 1024 
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    s.bind((host,port))
#    s.listen(backlog)
    p = ProcessSample()
    while 1:
        data, addr  = s.recvfrom(size)        
#        data = client.recv(size)
        if len(data) > 0:                     
            #print [ord(x) for x in data]
            pulse = '%02X' % ord(data[6]) + '%02X' % ord(data[7])
            pulse_int = int(pulse,16)
            #print pulse_int
            #print pulse_int
            z = p.process_sample(pulse_int)
            if z and z[0]:
                print z
#            data = client.recv(size)
#        client.close() 

main()        