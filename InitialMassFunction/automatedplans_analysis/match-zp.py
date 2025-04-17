import os
import math
import statistics
import sys


#read the filenames from the arguments
catMags = sys.argv[1:][0]
print("Catalogue magnitudes: "+catMags)

instMags=  sys.argv[1:][1]
print("Instrument magnitudes: "+instMags)

outfile=  sys.argv[1:][2]
print("Output file for matches: "+outfile)

if os.path.exists(outfile):
	print("Output file already exists")
	sys.exit()

filt = sys.argv[1:][3] #"B"

print("---------------------")

print("Filter is "+filt)

#Maximum distance from expected coordinates for a source to be considered (arcseconds)
maxDist = 2

#outlier rejection
maxdif = 0.3

#Open the corresponding source list for reading
instMagsFile = open(instMags, "r")
instLines = instMagsFile.readlines()

catFile = open(catMags, "r")
catLines = catFile.readlines()

lineNum=0
			
zplist = []

x=0
print("---------------------")
print("Matching stars...")

matches = 0

#Loop through all lines in the file
for line in instLines:

	
	if lineNum >1:

		parts = line.split(",")
		
		if parts[0]!="End":
			
			#Extract useful values from the source list
			ra = float(parts[3]) 	#Right ascensions (degrees)
			dec = float(parts[4]) 	#Declination (degrees)
			mag = float(parts[14])			#Source instrument magnitude
			
			#print(str(lineNum )+" "+str(ra)+" "+str(dec)+" "+str(mag))
			
			firstLine = 0
			
			closest = 360
			

			for lineCat in catLines:
			
			
				#print(lineCat)
				if firstLine>0:
				
					#if line not empty
					if lineCat.strip():
						partsCat = lineCat.split("|")

						raCat = float(partsCat[0]) 	#Right ascensions (degrees)
						decCat = float(partsCat[1]) 	#Declination (degrees)
						Vmag= float(partsCat[2])			#Source instrument magnitude
						Bmag= float(partsCat[3].strip())			#Source instrument magnitude
						
						ra1 = math.radians(raCat)
						ra2 = math.radians(ra)
						d1 = math.radians(decCat)
						d2 = math.radians(dec)			
						
						#Calculate the distance from this source to the target
						angSep = 3600*math.degrees(math.acos(math.sin(d1)*math.sin(d2)+math.cos(d1)*math.cos(d2)*math.cos(ra1-ra2)))
						
						if angSep < maxDist and angSep<closest:
								
							closest = angSep
							
							if filt=="V":
								catmag = Vmag
							else:
								catmag = Bmag
							

						
				
				elif lineCat[:4] == "----":
					firstLine = 1
					#print(lineCat)
				#else:
					#print(lineCat)
					
			
			if closest<maxDist:
			
				zp = catmag-mag
				zplist.append(zp)
				matches = matches+1
				
				#print(str(closest)+" "+str(mag)+" "+str(catmag)+" "+str(zp))
		
	lineNum=lineNum+1
			
print(str(matches) + " matches found")
print("---------------------")		

print("Pass one")		

medzp = statistics.median(zplist)	
stdevzp = statistics.stdev(zplist)	

print("Zero point: "+ str(round(medzp,4)))
print("Stdev: "+str(round(stdevzp,4)))

print("---------------------")
print("Rejecting outliers")		

for zp in zplist:

	dif = zp - medzp
	
	if abs(dif)>maxdif:
		
		zplist.remove(zp)
		
print("Pass two")		
	
medzp = statistics.median(zplist)	
stdevzp = statistics.stdev(zplist)	

print("Zero point: "+ str(round(medzp,4)))
print("Stdev: "+str(round(stdevzp,4)))
	
	
print("---------------------")
print("Writing to file: "+outfile)		
	
f= open(outfile,"a")	

#write header
f.write("RA,Dec,"+filt+"mag\n")

lineNum=0	
	
for line in instLines:

	if lineNum >1:

		parts = line.split(",")
		
		#Extract useful values from the source list
		ra = parts[3] 	#Right ascensions (degrees)
		dec = parts[4] 	#Declination (degrees)
		#print(parts[14])
		mag = float(parts[14])			#Source instrument magnitude
		
		calmag = mag+medzp
		
		f.write(ra+","+dec+","+"{:.4f}".format(calmag)+"\n")
		
	lineNum=lineNum+1

f.close()

print("Done")	
