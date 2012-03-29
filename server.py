import zmq, json, time, random, socket, struct

context = zmq.Context()
zsock = context.socket(zmq.PUB)
zsock.bind("tcp://0.0.0.0:9898")

harvester = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
harvester.bind( ("0.0.0.0", 9899) )
while True:
    data, _ = harvester.recvfrom(1024)
    header = data[:struct.calcsize("LL")]
    (version, message) = struct.unpack("LL", header)
    data = data[ struct.calcsize("LL"):]
    if version == 1 and message == 1: # bfsSend message
        (fromId, toId, sequence, nbytes) = struct.unpack("LLLL", data)
        zsock.send(json.dumps( {'type' : 'bfsSend',
                                                          'from' : fromId,
                                                          'to'   : toId,
                                                          'size' : nbytes } ) )
    elif version == 1 and message == 100: # gridftp notification
        (fromId, toId, bytes, duration) = struct.unpack("LLLL", data)
        zsock.send(json.dumps({'type' : 'gridftpDone',
                                                 'from' : fromId,
                                                 'to'   : toId,
                                                 'size' : nbytes,
                                                 'duration' : duration } ) )

    