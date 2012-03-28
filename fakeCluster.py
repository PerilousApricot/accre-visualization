#!/usr/bin/env python
import socket, random, struct,time

UDP_IP="127.0.0.1"
UDP_PORT=9899
sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP

fromIds = range(17,25)
toIds   = range(16)
toIds.extend(range(25,64))
print "fromIds is %s" % fromIds
print "toIds is %s" % toIds
sequence = 0
while True:
    time.sleep(0.01)
    version = 1
    message = 1
    fromId  = random.choice(fromIds)
    toId   = random.choice(toIds)
    sequence += 1
    if sequence > 100000000:
        sequence = 0
    nbytes = random.randint(0, 1024*1024*1024 )
    
    packed = struct.pack("LLLLLL", version, message, fromId, toId, sequence, nbytes)
    

    sock.sendto( packed, (UDP_IP, UDP_PORT) )