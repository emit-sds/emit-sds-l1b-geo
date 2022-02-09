# Short script to extract the TLE from the json file we downloaded from
# www.space-track.org. We need a straight text file for SPICE to convert
# this to a kernel
import json

t = json.load(open("iss_tle.json"))
with open("iss_tle.txt", "w") as fh:
    for tv in t:
        print(tv["TLE_LINE1"], file=fh)
        print(tv["TLE_LINE2"], file=fh)
        
    
