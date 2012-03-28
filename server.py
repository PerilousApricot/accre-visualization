import zmq, json, time, random, socket, struct

context = zmq.Context()
zsock = context.socket(zmq.PUB)
zsock.bind("tcp://0.0.0.0:9898")

harvester = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
harvester.bind( ("0.0.0.0", 9899) )
while True:
    data, _ = harvester.recvfrom(1024)
    (version, message, fromId, toId, sequence, nbytes) = struct.unpack("LLLLLL", data)
    if version == 1 and message == 1: # bfsSend message
        zsock.send("bfsdump %s" % json.dumps( {'type' : 'bfsSend',
                                                          'from' : fromId,
                                                          'to'   : toId,
                                                          'size' : nbytes } ) )
    if version == 1 and message == 100: # gridftp notification
        print "got gridftp notification"
    