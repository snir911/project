from mag_to_tor import magnet2torrent
import libtorrent as lt
import hashlib 
import binascii
from test2 import announce_udp
from mod3funs import mod3_announce_udp
from time import sleep
from getFromWeb import get_magnet_by_name_pitatebay
from getFromWeb import get_magnet_Latest_torrent
from check_seed import checkseed
import socket,struct
from MySQLdb.constants.REFRESH import FAST
import sys

#compare ip_table with list  
ip_table = []
def main():
    ans=True
    while ans:
        print ("""
        1.mode 1 - Find peers using torrent file/magent link
        2.mode 2 - Find first seeder
        3.mode 3 - Scan trackers list to find if certain peer is sharing hot files 
        4.Exit/Quit
        """)
        ans=raw_input("Please choose mode : ") 
        if ans=="1": 
            print("\nmode 1")
            mode1()
        elif ans=="2":
            print("\nmode 2") 
            mode2()
        elif ans=="3":
            mode3()
            print("\nmode 3") 
        elif ans=="4":
            print("\nGoodbye") 
            ans=False
        elif ans !="":
            print("\n Not Valid Choice Try again")
            main()
        #ans=False
def mode1():
    ans1=raw_input("Input Source : \n\t1. torrent file\n\t2. magnet link\n\nPlease choose source : ") 
    if ans1=="1":
        file_path=raw_input("Please enter file path : ")
        rawdata = open(file_path, "rb").read()
        print_from_raw(rawdata)
        print("\n torrent file")
    elif ans1=="2":
        magnet=raw_input("Please enter magnet link : ")
        rawdata = magnet2torrent(magnet)
        print("\n magent_link ")
        print_from_raw(rawdata)
        
    
def mode2():
    print ("Please choose mode:\n1.Pirate bay Latest torrent\n")
    print ("2.Pirate bay by keyword\n")
    ans=raw_input("mode: ")
    if ans=="1":
        magnet=get_magnet_Latest_torrent()
        rawdata = magnet2torrent(magnet)
        print_from_row(rawdata)
    elif ans=="2":
        keyword=raw_input("enter keyword: ")
        magnet=get_magnet_by_name_pitatebay(keyword)
        rawdata = magnet2torrent(magnet)
        print_from_row(rawdata)
    
    ip_table2 = []
    checkseed(ip_table2)
    for elem in ip_table2:
        if elem in ip_table:
            print elem
            
def mode3():
    print "\n### MODE 3 ###\n"
    print "Tracker List = List of trackers to scan"
    print "Hashes List = List of hot files hashes to test if the target IP is sharing them"
    print "Target IP = This is the target IP you would like to know if is sharing hot files\n"
    #trackers_file_path=raw_input("Please enter tracker list file path : ")
    #trackers_list= [line.strip() for line in open(trackers_file_path, "r")]
    trackers_list= [line.strip() for line in open('/home/snir/Desktop/project/trackers', "r")]
    #hash_file_path = raw_input("Please enter hashes list file path : ")
    #hash_list = [line.strip() for line in open(hash_file_path, "r")]
    hash_list = [line.strip() for line in open('/home/snir/Desktop/project/hashs', "r")]
    ip = raw_input("Please enter target IP : ")
    for elem in hash_list:
        hash_elem = binascii.unhexlify(elem)
        print "\nTrying hash " + elem + " at the following trackers:\n-------------------------------------------------------------\n" 
        for elem2 in trackers_list:
            if str(elem2[0]) == 'u':             #means udp url
                requestDict = {"info_hash" : hash_elem, "peer_id" : "-DE1360-qfkf.ZPfKJ42" ,"port" : "50515" , "uploaded": "0" ,"downloaded" : "0","left":"0"}
                print "\nTracker : " + elem2 #+ "\n"
                if(annonce_retrieve_until_found(elem2,ip,requestDict,0.95)):#retrieve peers until received 30% from all available peers
                    print ip + " is in swarm of hash "+ elem +"\n"
                    break

        
def is_ip_on_list(ipdictlist,ipstr):
    for elem in ipdictlist:
        if (socket.inet_ntoa(struct.pack("!i",elem['IP']))==ipstr):
            return True
    return False        
def annonce_retrieve_until_found(tracker,ip,requestDict,howMany):
    peers_no_dup=[]
    try:
        con = mod3_announce_udp(tracker,requestDict,0)
        ret,peers = mod3_announce_udp(tracker,requestDict,con)
        print "\tLeeches:"+str(ret['leeches'])
        print "\tSeeds:"+str(ret['seeds'])
        sleep(2)
        #print "\tretrieved "+str(len(peers))+" from "+str(ret['seeds'])+"\n"
    except:
        print "Result : Tracker unavailable"
        return False
    peers_no_dup = concate_no_dup(peers_no_dup,peers)
    
    if(is_ip_on_list(peers_no_dup,ip)==True):
        return True
    else:
        backoff = 2
        while (len(peers_no_dup) < ret['seeds']*howMany):
            sys.stdout.write('\r' + "\tretrieved "+str(len(peers_no_dup))+" from "+str(ret['seeds']) + ' ' * 20)
            sys.stdout.flush() # important
            try:
                ret,peers = mod3_announce_udp(tracker,requestDict,con)
            except:
                #print "tracker " + tracker + " unavailable"
                if (backoff <15):
                    backoff += 3
                else:
                    print "\n\t"+ ip + " is probably not signed as sharing this swarm at "+ tracker
                    return False
                sleep(backoff)
                

            peers_no_dup = peers_no_dup = concate_no_dup(peers_no_dup,peers)
        if(is_ip_on_list(peers_no_dup,ip)==True):
            print "Result : "
            return True
    sys.stdout.write('\r' + "\tretrieved "+str(len(peers_no_dup))+" from "+str(ret['seeds']) + ' ' * 20 )
    print "\nResult : " + ip + " is probably not signed as sharing this swarm at "+ tracker
    #print "\n\t" + str(len(peers_no_dup)) + " users were retrieved\n"
    return False    


def concate_no_dup(one,two):
    for elem in two:
        if (is_ip_on_list(one,socket.inet_ntoa(struct.pack("!i",elem['IP'])))==False):
            one.append(elem)
    return one       
    
        
        
def print_from_row(rawdata):
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
        for elem in di["announce-list"][0]:
            if str(elem[0])[0] == 'u':             #means udp url
                print "\nTracker : " + elem + "\n"
                try:
                    announce_udp(elem,requestDict,ip_table)
                except:
                    print "tracker " + elem + " unavailable"
                    continue
                #nnounce = elem[0]#rm
                #break#rm
                sleep(2)
                print "\n------------------------------------------------------------------------"
    try:
        announce_udp(announce,requestDict,ip_table)#rm
    except:
        print "tracker " + announce + " unavailable"
    
    print(len(ip_table))

def print_from_raw(rawdata):
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
    peers_no_dup = []
    if "announce-list" in di.keys():
        if len(di["announce-list"][0]) > 1:
            for elem in di["announce-list"][0]:
                if str(elem[0])[0] == 'u':             #means udp url
                    print "\nTracker : " + elem + "\n"
                    try:
                        peers_no_dup=concate_no_dup(peers_no_dup,annonce_retrieve_and_return(elem,requestDict,0.9))
                    except:
                        print "tracker " + elem + " unavailable"
                        continue
                    #nnounce = elem[0]#rm
                    #break#rm
                    sleep(2)
                    print "\n------------------------------------------------------------------------"
        else:
            for elem in di["announce-list"]:
                if str(elem[0])[0] == 'u':             #means udp url
                    print "\nTracker : " + elem[0] + "\n"
                    try:
                        peers_no_dup=concate_no_dup(peers_no_dup,annonce_retrieve_and_return(elem[0],requestDict,0.9))
                    except:
                        print "tracker " + elem[0] + " unavailable"
                        continue
                    sleep(2)
                    print "\n------------------------------------------------------------------------"

    try:
        peers_no_dup=concate_no_dup(peers_no_dup,annonce_retrieve_and_return(announce,requestDict,0.9))#rm
    except:
        print "tracker " + announce + " unavailable"
    print ""
    print str(len(peers_no_dup)) + " peers in total were retrieved as sharing this file"
    ans = raw_input("\n1. Print 2. Write to file :\n")
    if ans == "1":
        print_peers_list(peers_no_dup)
    else:
        try:
            write_to_file_peers_list(peers_no_dup)
        except:
            raw_input("\n writing failed enter 1 to print : ")
    
def annonce_retrieve_and_return(tracker,requestDict,howMany):
    peers_no_dup=[]
    try:
        con = mod3_announce_udp(tracker,requestDict,0)
        ret,peers = mod3_announce_udp(tracker,requestDict,con)
        print "\tLeeches:"+str(ret['leeches'])
        print "\tSeeds:"+str(ret['seeds'])
        sleep(2)
        #print "\tretrieved "+str(len(peers))+" from "+str(ret['seeds'])+"\n"
    except:
        print "Result : Tracker unavailable"
        return peers_no_dup
    peers_no_dup = concate_no_dup(peers_no_dup,peers)
    backoff = 2
    while (len(peers_no_dup) < ret['seeds']*howMany):
        sys.stdout.write('\r' + "\tretrieved "+str(len(peers_no_dup))+" from "+str(ret['seeds']) + ' ' * 20)
        sys.stdout.flush() # important
        try:
            ret,peers = mod3_announce_udp(tracker,requestDict,con)
        except:
            #print "tracker " + tracker + " unavailable"
            if (backoff <15):
                backoff += 3
            else:
                print_peers_list(peers_no_dup)
            sleep(backoff)
                

        peers_no_dup = concate_no_dup(peers_no_dup,peers)
    sys.stdout.write('\r' + "\tretrieved "+str(len(peers_no_dup))+" from "+str(ret['seeds']) + ' ' * 20 )
    return peers_no_dup    

def print_peers_list(peers):
    i = 0;
    print ""
    for elem in peers:
        print str(i) + ". IP: "+socket.inet_ntoa(struct.pack("!i",elem['IP']))
        print ' ' * len(str(i)) + "  Port: "+str(elem['port'])
        i = i+1
def write_to_file_peers_list(peers):
    i = 0;
    print ""
    path = raw_input("Please enter path to file : ")
    target = open(path, 'w')
    for elem in peers:
        target.write(str(i) + ". IP: "+socket.inet_ntoa(struct.pack("!i",elem['IP'])))
        target.write("\n")
        target.write( ' ' * len(str(i)) + "  Port: "+str(elem['port']))
        target.write("\n")
        i = i+1
    target.close()


if __name__ == "__main__":
    main()
        