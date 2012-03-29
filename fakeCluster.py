#!/usr/bin/env python
import socket, random, struct,time

UDP_IP="127.0.0.1"
UDP_PORT=9899
sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP


seIds    = range(16)
depotIds = range(17,25)
wnIds    = range(25, 64)
globalIds= range(1000,1010)
fromIds  = depotIds
toIds    = seIds[:]
toIds.extend(wnIds)
print "fromIds is %s" % fromIds
print "toIds is %s" % toIds
sequence = 0
while True:
    time.sleep(0.025)
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
    
    # send gridftp information
    version = 1
    message = 100 # gridftp send
    if random.randint(1,2) == 1:
        fromId  = random.choice( seIds )
        toId    = random.choice( globalIds )
    else:
        fromId  = random.choice( globalIds )
        toId    = random.choice( seIds )

    duration = random.randint( 1, 10 )
    bytes = random.randint(0, 1024*1024*1024 )
    
    packed = struct.pack("LLLLLL", version, message, int(fromId), int(toId), int(bytes), int(duration))
    sock.sendto( packed, (UDP_IP, UDP_PORT) )


    

