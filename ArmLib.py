class ArmData:
    encoders   = [0.0,0.0,0.0]
    setpoints  = [0.0,0.0,0.0]
    gravity    = [0.0,0.0,0.0]
    loadvalues = [0.0,0.0,0.0]
    tarevalues = None
    
    rollingavg = []
    
    tare = True
    def __init__(self,line,tare=True):
        self.tare = tare
        self.parseline(line)
        pass
    
    def parseline(self,line):
        # strip whitespae and control chars. split on spaces.
        p = line.strip().split(" ")
        
        line  = line.strip()
        #for i,x in enumerate(p):
        #    print "%d: %s"%(i,x)
        try:
            self.encoders[0]  = float(p[3])
            self.encoders[1]  = float(p[5])
            self.encoders[2]  = float(p[7])
            
            self.setpoints[0] = float(p[10])
            self.setpoints[1] = float(p[12])
            self.setpoints[2] = float(p[14])
            
            self.gravity[0]   = float(p[17])
            self.gravity[1]   = float(p[19])
            self.gravity[2]   = float(p[21])
            
            load = [0,0,0]
            load[0] = float(p[25])
            load[1] = float(p[27])
            load[2] = float(p[29])
             
            if self.tare:
                if self.tarevalues == None:
                    print "Tareing with %s" % load
                    self.tarevalues = load

            if self.tare:
                self.loadvalues =  [a - b for a, b in zip(load, self.tarevalues)]
            else:
                self.loadvalues =  load

        except IndexError:
            print " ERROR: Malformed Packet IE"
            #print line
        except ValueError:
            print " ERROR: Malformed Packet VE"
            #print line
        
    def __repr__(self):
        encoders = self.encoders
        setpoints = self.setpoints
        gravity = self.gravity
        loadvalues = self.loadvalues
        maxes = self.maxes
        
            
        e = "[%0.4f , %0.4f , %0.4f]" % (encoders[0],encoders[1],encoders[2])
        s = "[%0.4f , %0.4f , %0.4f]" % (setpoints[0],setpoints[1],setpoints[2])
        g = "[%0.4f , %0.4f , %0.4f]" % (gravity[0],gravity[1],gravity[2])
        l = "[%0.4f , %0.4f , %0.4f]" % (loadvalues[0],loadvalues[1],loadvalues[2])
    
        return "Encoders: %s\tSetpoints: %s\tGravity: %s\tLoads: %s" % (s,e,g,l)
