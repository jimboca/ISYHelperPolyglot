#!/usr/bin/python

#
# UDP ping command
# Model 1
#

import os
import socket
import sys
import time
from struct import unpack
import zmq

#include <czmq.h>
PING_PORT_NUMBER = 10000
PING_MSG_SIZE    = 130
PING_INTERVAL    = 2  # Once per second

def main():

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Ask operating system to let us do broadcasts from socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Bind UDP socket to local port so we can receive pings
    sock.bind(('', PING_PORT_NUMBER))

    # main ping loop
    # We use zmq_poll to wait for activity on the UDP socket, since
    # this function works on non-0MQ file handles. We send a beacon
    # once a second, and we collect and report beacons that come in
    # from other nodes:

    poller = zmq.Poller()
    poller.register(sock, zmq.POLLIN)

    # Send first ping right away
    ping_at = time.time()

    while True:
        timeout = ping_at - time.time()
        if timeout < 0:
            timeout = 0
        try:
            events = dict(poller.poll(1000* timeout))
        except KeyboardInterrupt:
            print("interrupted")
            break

        # Someone answered our ping
        if sock.fileno() in events:
            msg, addrinfo = sock.recvfrom(PING_MSG_SIZE)
            print "Found peer %s:%d" % addrinfo
            print "msg=%s" % msg
            # ftp://109.108.88.53/Nadzor/FOSCAM/SDK%20CGI/MJPEG%20CGI%20SDK/MJPEG%20CGI%20SDK/Ipcamera%20device%20search%20protocol.pdf
            print "unpacked=%s %s %d %d %d %d %s %s %s" % unpack('13s21s<i<i<i<i4c4c<h?',msg)

        if time.time() >= ping_at:
            # Broadcast our beacon
            print ("Pinging peers\n")
            sock.sendto(b'0001', 0, ("255.255.255.255", PING_PORT_NUMBER))
            ping_at = time.time() + PING_INTERVAL

if __name__ == '__main__':
    main()
