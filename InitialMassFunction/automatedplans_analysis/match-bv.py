import os
import math
import sys

BMags= sys.argv[1:][0] # "NGC457-B-cal-mags.csv"

VMags= sys.argv[1:][1] #"NGC457-V-cal-mags.csv"

outFile= sys.argv[1:][2] #"NGC457-BV.csv"

print("B magnitudes: "+BMags)

print("V magnitudes: "+VMags)

print("Output file: "+outFile)

if os.path.exists(outFile):
	print("Output file already exists")
	sys.exit()	

#Maximum distance from expected coordinates for a source to be considered (arcseconds)
maxDist = 2

#Open the corresponding source list for reading
VMagsFile = open(VMags, "r")
#skip headers
Vfirst_line = VMagsFile.readline()
VLines = VMagsFile.readlines()

BMagsFile = open(BMags, "r")
Bfirst_line = BMagsFile.readline()
BLines = BMagsFile.readlines()




lineNum=0
			
outlist = []

x=0

matches = 0

print("---------------------")
print("Matching stars...")

#Loop through all lines in the file
for Vline in VLines:


	partsV = Vline.split(",")
	
	#Extract useful values from the source list
	raV = float(partsV[0]) 	#Right ascensions (degrees)
	decV = float(partsV[1]) 	#Declination (degrees)
	Vmag = float(partsV[2].strip())			#Source instrument magnitude

	firstLine = 0
	
	closest = 360
	
	bestB =0

	for Bline in BLines:
	
	
		partsB = Bline.split(",")

		raB = float(partsB[0]) 	#Right ascensions (degrees)
		decB = float(partsB[1]) 	#Declination (degrees)
		Bmag= float(partsB[2].strip())			#Source instrument magnitude
		
		ra1 = math.radians(raB)
		ra2 = math.radians(raV)
		d1 = math.radians(decB)
		d2 = math.radians(decV)			
		
		#Calculate the distance from this source to the target
				
		if abs(ra1-ra2)==0 and abs(d1-d2)==0:
			angSep = 0
		else:		
			angSep = 3600*math.degrees(math.acos(math.sin(d1)*math.sin(d2)+math.cos(d1)*math.cos(d2)*math.cos(ra1-ra2)))
		
		if angSep < maxDist and angSep<closest:
				
			closest = angSep
			
			bestB = Bmag
			
	Bmag = bestB 

	if closest<maxDist:
	
		string = str(raV)+","+str(decV)+","+str(round(Vmag,4))+","+str(round(Bmag,4))+","+str(round(Bmag-Vmag,4))
		outlist.append(string)
		matches = matches + 1

			
			
print(str(matches) + " matches found")

print("---------------------")
print("Writing to file: " +outFile)	

f= open(outFile,"a")	

#write header
f.write("RA,Dec,Vmag,Bmag,B-V\n")

lineNum=0	
	
for line in outlist:

	f.write(line+"\n")

f.close()
		
print("Done")
