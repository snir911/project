import  urllib, socket, random, struct
#from bcode import bdecode
from urlparse import urlparse
import binascii
import sys


def mod3_announce_udp(tracker,payload,do_i_have_con):
    tracker = tracker.lower()
    parsed = urlparse(tracker)
    # Teporarly Change udp:// to http:// to get hostname and portnumbe
    url = parsed.geturl()[3:]
    url = "http" + url
    hostname = urlparse(url).hostname
    port = urlparse(url).port


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(8)
    conn = (socket.gethostbyname(hostname), port)
    #sock.bind((socket.gethostname(),s_port))
    #Get connection ID
    req, transaction_id = mod3_udp_create_connection_request()
    #print binascii.hexlify(req)
    #print conn
    sock.sendto(req, conn);
    buf = sock.recvfrom(2048)[0]
        
    if (do_i_have_con == 0):
        connection_id = mod3_udp_parse_connection_response(buf, transaction_id)
        return connection_id
    else :
        connection_id = do_i_have_con

    #Annoucing
    s_port = sock.getsockname()[1] #get port number to which socket is connected
    req, transaction_id = mod3_udp_create_announce_request(connection_id, payload,s_port)
    sock.sendto(req, conn)
    #print "\tAnnounce Request Sent\r",
    buf = sock.recvfrom(2048)[0]
    #print "\tResponse received               \r",
    return mod3_udp_parse_announce_response(buf, transaction_id)

def mod3_udp_create_announce_request(connection_id, payload, s_port):
    action = 0x1 #action (1 = announce)
    transaction_id = mod3_udp_get_transaction_id()
    #print "2.Transaction ID :", transaction_id
    #print "3.Connection ID :", connection_id
    buf = struct.pack("!q", connection_id)                                  #first 8 bytes is connection id
    buf += struct.pack("!i", action)                                        #next 4 bytes is action 
    buf += struct.pack("!i", transaction_id)                                #followed by 4 byte transaction id
    buf += struct.pack("!20s", urllib.unquote(payload['info_hash']))        #the info hash of the torrent we announce ourselves in
    buf += struct.pack("!20s", urllib.unquote(payload['peer_id']))          #the peer_id we announce
    buf += struct.pack("!q", int(payload['downloaded']))                    #number of bytes downloaded
    buf += struct.pack("!q", int(payload['left']))                          #number of bytes left
    buf += struct.pack("!q", int(payload['uploaded']))                      #number of bytes uploaded
    buf += struct.pack("!i", 0x2)                                           #event 2 denotes start of downloading
    buf += struct.pack("!i", 0x0)                                           #IP address set to 0. Response received to the sender of this packet
    key = mod3_udp_get_transaction_id()                                          #Unique key randomized by client
    buf += struct.pack("!i", key)
    buf += struct.pack("!i", -1)                                            #Number of peers required. Set to -1 for default
    buf += struct.pack("!i", s_port)                                       #port on which response will be sent
    return (buf, transaction_id)

def mod3_udp_parse_announce_response(buf, sent_transaction_id):
    #print "Response is:"+str(buf)  
    if len(buf) < 20:
        raise RuntimeError("Wrong response length while announcing: %s" % len(buf)) 
    action = struct.unpack_from("!i", buf)[0] #first 4 bytes is action
    res_transaction_id = struct.unpack_from("!i", buf, 4)[0] #next 4 bytes is transaction id    
    if res_transaction_id != sent_transaction_id:
        raise RuntimeError("Transaction ID doesnt match in announce response! Expected %s, got %s"
            % (sent_transaction_id, res_transaction_id))
    #print "\tReading Response           \r",
    if action == 0x1:
        #print "\tAction is 3"
        ret = dict()
        offset = 8; #next 4 bytes after action is transaction_id, so data doesnt start till byte 8      
        #ret['interval'] = struct.unpack_from("!i", buf, offset)[0]
        #print "Interval:"+str(ret['interval'])
        offset += 4
        ret['leeches'] = struct.unpack_from("!i", buf, offset)[0]
        #print "\tLeeches:"+str(ret['leeches'])
        offset += 4
        ret['seeds'] = struct.unpack_from("!i", buf, offset)[0]
        #print "\tSeeds:"+str(ret['seeds'])
        offset += 4
        peers = list()
        x = 0
        #print ""
        while offset != len(buf):
            peers.append(dict())
            peers[x]['IP'] = struct.unpack_from("!i",buf,offset)[0]
            #print x 
            #print "IP: "+socket.inet_ntoa(struct.pack("!i",peers[x]['IP']))
            offset += 4
            if offset >= len(buf):
                raise RuntimeError("Error while reading peer port")
            peers[x]['port'] = struct.unpack_from("!H",buf,offset)[0]
            #print "Port: "+str(peers[x]['port'])
            offset += 2
            x += 1
        return ret,peers
    else:
        #an error occured, try and extract the error string
        error = struct.unpack_from("!s", buf, 8)
        print "Action="+str(action)
        raise RuntimeError("Error while annoucing: %s" % error)

def mod3_udp_create_connection_request():
    connection_id = 0x41727101980                   #default connection id
    action = 0x0                                    #action (0 = give me a new connection id)   
    transaction_id = mod3_udp_get_transaction_id()
    
    #print "1.Transaction ID :", transaction_id
    buf = struct.pack("!q", connection_id)          #first 8 bytes is connection id
    buf += struct.pack("!i", action)                #next 4 bytes is actionudp_create_announce_request 
    buf += struct.pack("!i", transaction_id)        #next 4 bytes is transaction id
    
    return (buf, transaction_id)

def mod3_udp_parse_connection_response(buf, sent_transaction_id):
    if len(buf) < 16:
        raise RuntimeError("Wrong response length getting connection id: %s" % len(buf))            
    action = struct.unpack_from("!i", buf)[0] #first 4 bytes is action

    res_transaction_id = struct.unpack_from("!i", buf, 4)[0] #next 4 bytes is transaction id
    if res_transaction_id != sent_transaction_id:
        raise RuntimeError("Transaction ID doesnt match in connection response! Expected %s, got %s"
            % (sent_transaction_id, res_transaction_id))

    if action == 0x0:
        connection_id = struct.unpack_from("!q", buf, 8)[0] #unpack 8 bytes from byte 8, should be the connection_id
        return connection_id
    elif action == 0x3:     
        error = struct.unpack_from("!s", buf, 8)
        raise RuntimeError("Error while trying to get a connection response: %s" % error)
    pass

def mod3_udp_get_transaction_id():
    return int(random.randrange(0, 255))