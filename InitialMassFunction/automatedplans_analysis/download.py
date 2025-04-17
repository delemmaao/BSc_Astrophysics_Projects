from urllib import request, parse
from astropy.io import fits
import os
import sys

#read the filename from the arguments
filename = sys.argv[1:][0]

#Open the fits file header data unit
hdul = fits.open(filename)

try:
    #Extract Right ascension of centre of the image
    RA= float(hdul[0].header['CRVAL1'])	
    print("RA: "+str(RA))

    #Extract declination of centre of the image
    DEC= float(hdul[0].header['CRVAL2'])	
    print("DEC: "+str(DEC))
    
except:
    print("Error: Could not find CRVAL1 or CRVAL2 in FITS header. This likely means the image has not been plate-solved.")
    print("See https://observatory.herts.ac.uk/wiki/Plate_Solving for help with plate-solving images.")
    quit()


postData = {  '-source' : 'I/322A/out', '-out.max' : '10000',  '-out.form' : '| -Separated-Values',  '-oc.form' : 'dec',  '-c.eq' : 'J2000', '-c.r' : '++2', '-c.u' : 'arcmin', '-c.geom' : 'r', '-out.src' : 'I/322A/out', '-out.orig' : 'standard',  '-out' : 'RAJ2000, DEJ2000, Vmag, Bmag', 'Bmag' : '>0',  'Vmag' : '>0', 'RAJ2000' : str(RA)+'+/-0.5',  'DEJ2000' : str(DEC)+'+/-0.5'}

#URL encode data

data = parse.urlencode(postData).encode()


#Create web request
req =  request.Request('http://vizier.u-strasbg.fr/viz-bin/asu-tsv', data=data)

#print("Downloading UCAC4 data")

#Request web query
response = request.urlopen(req)

#Get return data
return_data = response.read()

#print(response)

#print(return_data)

print("Writing to file: "+os.path.splitext(filename)[0]+"-UCAC4.tbl")

#write the return data to file
with open(os.path.splitext(filename)[0]+"-UCAC4.tbl", 'wb') as s:
    s.write(return_data)
	
print("Done")
