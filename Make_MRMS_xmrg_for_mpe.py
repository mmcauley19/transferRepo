#-----------------------------------------------------------------------------
# This script makes 1 hour MRMS and NBM xmrg qpe grids for use in MPE.
#
# If the Q3 data is not current and/or missing, it will also copy the MRMS xmrg into the Q3 directory 
#
# It also copies the NBM xmrg into the MPE satpre directory so that a locally biased NBM is generated every hour in MPE 
#
# Dan Virgillito MBRFC March 2023
# ----------------------------------------------------------------------------

## MenuItems has been set to [] so that the procedure is hidden
#MenuItems = []
MenuItems = ["Consistency"]

from numpy import *
import string,os,struct,math,AbsTime,time,TimeRange
import SmartScript

class Procedure (SmartScript.SmartScript):
    def __init__(self, dbss):
        SmartScript.SmartScript.__init__(self, dbss)


    def makeXMRG (self, model, element, directory):
        # Change the origin and extent values to match your RFC xnav hrap
        # coordinates.  These values should be in .Apps_defaults_site:
        # hrap_xor, hrap_yor, hrap_x, hrap_y
        origin=[235,375]
        extent=[485,325]

        tTime = time.gmtime()
        hour = ("0" + str(tTime.tm_hour))[-2:]
        print()
        print("this is the current hour in ZULU time:", hour)
        print()



        latestmodel = str(self.findDatabase(model)) # Most recent HRRR model
        print("This is the", model, "forecast run:", latestmodel)
        tTime = time.gmtime()
        hour = ("0" + str(tTime.tm_hour))[-2:]
        print("this is the current hour in ZULU time:", hour)


        if model == "NBM" :
            beginhour=int(hour)-3
            endhour=int(hour)+1
            timeRange = self.createTimeRange(beginhour,endhour, "Zulu")
            print ("this is the NGM beginhour:     ", beginhour)
            print ("this is the NGM endhour:     ", endhour)
            print ("this is the NGM timeRange:     ", timeRange)

        
        elif model == "MRMS" :
            print("model is: ",model)
            beginhour=int(hour)-2
            endhour=int(hour)
            timeRange = self.createTimeRange(beginhour,endhour, "Zulu")
            print ("this is the MRMS beginhour:     ", beginhour)
            print ("this is the MRMS endhour:     ", endhour)
            print ("this is the MRMS timeRange:     ", timeRange)


 
        print("Starting grid: ", timeRange.startTime())
        print("Ending grid: ", timeRange.endTime())
        print("Duration of all grids selected (seconds): ", timeRange.duration())
        print("the time range is: ", timeRange)
 
        # Variable definitions
        start = timeRange.startTime()
        #end = timeRange.endTime()
        duration = timeRange.duration()
        timeRange2=TimeRange.TimeRange(start,start + 1 * 3600)
        print("The timeRange2 is: ", timeRange2)
 
 
        # Loop through each grid, loop counter is 'duration' variable which
        # subtracts 1 hour (3600 seconds) during each iteration until it reaches
        # zero.
        while (duration>0):
 
#            print "Processing grid: ", timeRange2.startTime()
            print("Processing grid: ", timeRange2.endTime())
 
            # This section derives the tair grid name based on the GFE grid
            # starting time.
            # e.g. Converts: Nov 03 08 05:00:00 GMT to tair1103200805z
#            myTime=str(timeRange2.startTime())
            myTime=str(timeRange2.endTime())
 
            DD=myTime[8]+myTime[9]
            HH=myTime[11]+myTime[12]
            YYYY=myTime[0]+myTime[1]+myTime[2]+myTime[3]
            MM=myTime[5]+myTime[6]
 
            print("My time is: ", myTime)
            print("My DD is: ",DD)
            print("My HH is: ",HH)
            print("My YYYY is: ",YYYY)
            print("My MM is: ",MM)
 
            filename1 = YYYY+MM+DD+HH+"z"
            print(filename1)
 
            mysatTime=str(timeRange2.startTime())
 
            DDsat=mysatTime[8]+mysatTime[9]
            HHsat=mysatTime[11]+mysatTime[12]
            YYYYsat=mysatTime[0]+mysatTime[1]+mysatTime[2]+mysatTime[3]
            MMsat=mysatTime[5]+mysatTime[6]
 
 
            filenamesat = YYYYsat+MMsat+DDsat+HHsat+"z"
            print(filenamesat)
 
 
            # Get current time
            currtime=time.time()
            savetime=time.gmtime(currtime)
 
 
            # Create the XMRG
            # XMRG header records
            data=[]
            data.append(struct.pack('i', 16)) # Size of 1st record
            data.append(struct.pack('i',origin[0])) # hrap_xor
            data.append(struct.pack('i',origin[1])) # hrap_yor
            data.append(struct.pack('i',extent[0])) # hrap_x
            data.append(struct.pack('i',extent[1])) # hrap_y
            data.append(struct.pack('i', 16)) # Size of 1st record
            data.append(struct.pack('i', 66)) # Size of 2nd record           
            S1='L'  # p3
            S2='X'  # p3
            data.append(struct.pack('cc', S1.encode('utf-8'), S2.encode('utf-8')))   # p3
            data.append(struct.pack('8s', 'OPER'.encode('utf-8')))  # p3
            savedate="%4d-"%savetime[0]+"%02d-"%savetime[1]+"%02d "%savetime[2]+"%02d:"%savetime[3]+"%02d:"%savetime[4]+"%02d"%savetime[5]
            data.append(struct.pack('20s',savedate.encode('utf-8')))   # p3
            procflag="QPM06"
            data.append(struct.pack('8s',procflag.encode('utf-8')))   # p3
            validdate=YYYY+"-"+MM+"-"+DD+" "+HH+":00:00"
            data.append(struct.pack('20s',validdate.encode('utf-8')))   # p3
            data.append(struct.pack('i',328)) # Max allowable value in mm
            data.append(struct.pack('f',8.3)) # Intro. AWIPS Build
            data.append(struct.pack('i',66)) # Size of 2nd record
            # Data records
            datarec_size=extent[0]*2 # Size of data records
            pcpn=self.getGrids(model,element,"SFC",timeRange2)
            pcpn=flipud(pcpn)
            for j in range (origin[1], origin[1]+extent[1]):
                data.append(struct.pack('i',datarec_size))
                for i in range (origin[0], origin[0]+extent[0]):
                    val=pcpn[j-origin[1],i-origin[0]] * 2540 
                    data.append(struct.pack('h', int(val))) # p3, add int
                data.append(struct.pack('i',datarec_size))
 
            # Write the XMRG to disk
            s = B''.join (data)   # p3
 
            # *****************************************************************
            # Change location to where you want to save tair grids.
            # *****************************************************************
            filename=directory+filename1
 
#            filename="/awips2/edex/data/share/hydroapps/precip_proc/local/data/mpe/rfcqpe01/RFCMOSAIC01"+filename
##            filename="/tmp/gfe/tmp/RFCMOSAIC01"+filename
 
            w=open(filename,"wb")
            info=w.write(s)
            w.close()
 
            # Move to the next grid by adding 3600 seconds to start time; subtract
            # 3600 seconds from duration.
            start = timeRange2.startTime()
            timeRange2=TimeRange.TimeRange(start + 1 *3600, start + 2 * 3600)
            duration=duration-3600
            print(filename + " has been created and saved")
            print()
            print()
            if model == 'MRMS':
                q3dirfile = "/awips2/edex/data/share/hydroapps/precip_proc/local/data/mpe/qmosaic/QMOSAIC" + filename1
                exists = os.path.isfile(q3dirfile)
                if exists:
                    print(q3dirfile + " has been found, so do nothing")
                else:
                    command = 'cp ' + filename + ' ' + q3dirfile
                    os.system(command)
                    print(filename + ' has been copied to ' + q3dirfile)
            else:
                print('this is not the MRMS')
            if model == 'NBM':
                command = 'cp ' + filename + ' /awips2/edex/data/share/hydroapps/precip_proc/local/data/mpe/satpre/SATPRE' + filenamesat
                os.system(command)
            else:
                print('do nothing')
#            return
 



    def execute(self, editArea, timeRange, varDict):

        try:
            model = 'MRMS'
            element = 'QPE'
            directory="/awips2/edex/data/share/hydroapps/precip_proc/local/data/mpe/mrms/MRMS"
#             directory="/awips2/edex/data/share/hydroapps/precip_proc/local/data/mpe/localfield1/LOCALFIELD1"
            print("Make mrms xmrg files...\n")
            self.makeXMRG(model, element, directory)
        except:
            pass



        try:
            model = 'NBM'
            element = 'QPF1'
            directory="/awips2/edex/data/share/hydroapps/precip_proc/local/data/mpe/nbm/NBM"
#             directory="/awips2/edex/data/share/hydroapps/precip_proc/local/data/mpe/localfield1/LOCALFIELD1"
            print("Make nbm xmrgs")
            self.makeXMRG(model, element, directory)
        except:
            pass
