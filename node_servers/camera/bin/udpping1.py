#!/usr/bin/python

#
# UDP ping command
# Model 1
#
# http://askubuntu.com/questions/100529/how-to-install-python-package-pyzmq-properly
#
# sudo apt-get install libzmq-dev
# sudo pip install pyzmq
#

import os
import socket
import sys
import time
from struct import unpack,pack
import zmq

#include <czmq.h>
PING_PORT_NUMBER = 10000
PING_MSG_SIZE    = 130
PING_INTERVAL    = 5  # Once per second

# ftp://109.108.88.53/Nadzor/FOSCAM/SDK%20CGI/MJPEG%20CGI%20SDK/MJPEG%20CGI%20SDK/Ipcamera%20device%20search%20protocol.pdf
SEARCH_REQUEST = pack(">4sH?8sll4s", "MO_I", 0, 0, "", 67108864, 0, "")

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
            msg, (addr, uport) = sock.recvfrom(PING_MSG_SIZE)
            print "\nResponse from: %s:%d" % (addr, uport)
            #print "msg=%s" % msg
            if len(msg) == 88:
                upk = unpack('>23s13s21s4I4b4b4bH?',msg)
                #print upk
                (header, id, name, ip_i, mask_i, gateway_i, dns_i, r1, r2, r3, r4, sysv1, sysv2, sysv3, sysv4, appv1, appv2, appv3, appv4, port, dhcp) = upk
                ip      = socket.inet_ntoa(pack('!I',ip_i))
                mask    = socket.inet_ntoa(pack('!I',mask_i))
                gateway = socket.inet_ntoa(pack('!I',gateway_i))
                dns     = socket.inet_ntoa(pack('!I',dns_i))
                id      = id.rstrip('\x00')
                name   = name.rstrip('\x00')
                print "  Foscam Info: "
                print "   ID:%s" % id
                print "   Name:%s" % name
                print "   IP:%s" % ip
                print "   mask:%s" % mask
                print "   gateway:%s" % gateway
                print "   dns:%s" % dns
                print "   reserve:%d.%d.%d.%d" % (r1, r2, r3, r4)
                print "   sys:%d.%d.%d.%d" % (sysv1, sysv2, sysv3, sysv4)
                print "   app:%d.%d.%d.%d" % (appv1, appv2, appv3, appv4)
                print "   port:%s" % port
                print "   dhcp:%s" % dhcp
            else:
                print "   Ignored"

        if time.time() >= ping_at:
            # Broadcast our beacon
            print ("Pinging peers\n")
            sock.sendto(SEARCH_REQUEST, 0, ("255.255.255.255", PING_PORT_NUMBER))
            
            ping_at = time.time() + PING_INTERVAL

if __name__ == '__main__':
    main()
