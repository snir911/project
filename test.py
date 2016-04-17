import libtorrent as lt
import hashlib  
from test2 import announce_udp
from time import sleep
from mag_to_tor import magnet2torrent
from getFromWeb import get_magnet_by_name_pitatebay

#torrent mode
rawdata = open('C:/Users/User/test.torrent', "rb").read()


#magnet mode
#magnet = get_magnet_by_name_pitatebay("star_wars")
#print "Magnet recived"

#rawdata = magnet2torrent(magnet)

#takes to long to callback
di=lt.bdecode(rawdata)


fileSize = 0
print("INFO")
print "##################################################################################################"
print "##################################################################################################"
if "announce" in di.keys():
    announce=di["announce"]
    print("\nannounce:\n"+ di["announce"])
if "name" in di["info"].keys():
    print("\nname:\n"+ di["info"]["name"])
if "piece length" in di["info"].keys():
    print("\npiece length:")
    print(di["info"]["piece length"])
if "length" in di["info"].keys(): 
    fileSize = di["info"]["length"]
if "announce-list" in di.keys():
    print("\nannounce list:")
    for elem in di["announce-list"]:
        print elem
if "files" in di["info"].keys():
    print("\nfiles list:")
    for elem in di["info"]["files"]:
        print elem["path"]
        fileSize += elem["length"]

print("\nTotal length:")
print fileSize


#calc hash
pop=di["info"]
sha1 = hashlib.sha1()#create sha1 object
sha1.update(lt.bencode(di["info"]))#calc sha1 for file into object
sha1str=sha1.digest()#sha1 str


print "\ninfo hash:"
print repr(sha1str)

print "\n\nREQUEST - RESPONSE"
print "##################################################################################################"
print "##################################################################################################"

requestDict = {"info_hash" : sha1str,"peer_id" : "-DE1360-qfkf.ZPfKJ42" ,"port" : "50515" , "uploaded": "0" ,"downloaded" : "0" ,"left" : fileSize}


if "announce-list" in di.keys():
    for elem in di["announce-list"]:
        if str(elem[0])[0] == 'u':             #means udp url
            print "\nTracker : " + elem[0] + "\n"
            try:
                announce_udp(elem[0],requestDict)
            except:
                print "tracker " + elem[0] + " unavailable"
            #nnounce = elem[0]#rm
            #break#rm
            sleep(2)
            print "\n------------------------------------------------------------------------"
try:
    announce_udp(announce,requestDict)#rm
except:
    print "tracker " + announce + " unavailable"