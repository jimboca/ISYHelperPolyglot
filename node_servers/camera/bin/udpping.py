#!/usr/bin/python
#
# Basic script to send UDP requests looking for foscam cameras.
#

import os
import socket
import sys
import time
import select
from struct import unpack,pack

TIMEOUT = 30 # Run for 30 seconds max.
PING_INTERVAL    = 3  # Once every 5 seconds
PING_PORT_NUMBER = 10000
PING_MSG_SIZE    = 130

# ftp://109.108.88.53/Nadzor/FOSCAM/SDK%20CGI/MJPEG%20CGI%20SDK/MJPEG%20CGI%20SDK/Ipcamera%20device%20search%20protocol.pdf
SEARCH_REQUEST = pack(">4sH?8sll4s", "MO_I", 0, 0, "", 67108864, 0, "")

def foscam_poll():

    clients = ()
    clients_by_addr = {}

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Ask operating system to let us do broadcasts from socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Bind UDP socket to local port so we can receive pings
    sock.bind(('', PING_PORT_NUMBER))
    # Use timeout
    sock.settimeout(PING_INTERVAL)

    main_timeout = time.time() + TIMEOUT
    responses = {}
    while time.time() < main_timeout:

        # Broadcast our beacon
        print ("---------------------------------\nPinging for Foscam's")
        sock.sendto(SEARCH_REQUEST, 0, ("255.255.255.255", PING_PORT_NUMBER))
            
        ping_timeout = time.time() + PING_INTERVAL

        while time.time() < ping_timeout:

            # Listen for a response with timeout
            addr = None
            try:
                msg, (addr, uport) = sock.recvfrom(PING_MSG_SIZE)
                # Someone answered our ping, store it.
                if addr not in responses:
                    print "- Saving response from %s:%s" % (addr,uport)
                    responses[addr] = msg
            except socket.timeout:
                print "- No more reponses"
    print "All done looking."

    for addr, msg in responses.iteritems():

        print "----\nResponse from: %s" % (addr)
        if msg == SEARCH_REQUEST:
            print "  ignore my echo"
        elif len(msg) == 88:
            #print "msg=%s" % msg
            upk = unpack('>23s13s21s4I4b4b4bH?',msg)
            #print upk
            (header, id, name, ip_i, mask_i, gateway_i, dns_i, r1, r2, r3, r4, s1, s2, s3, s4, a1, a2, a3, a4, port, dhcp) = upk
            client = { 
                id:        id.rstrip('\x00'),
                name:      name.rstrip('\x00'),
                ip:        socket.inet_ntoa(pack('!I',ip_i)),
                port:      port,
                mask:      socket.inet_ntoa(pack('!I',mask_i)), 
                gateway:   socket.inet_ntoa(pack('!I',gateway_i)), 
                dns:       socket.inet_ntoa(pack('!I',dns_i)), 
                reserve:   "%d.%d.%d.%d" % (r1, r2, r3, r4),
                sys:       "%d.%d.%d.%d" % (s1, s2, s3, s4),
                app:       "%d.%d.%d.%d" % (a1, a2, a3, a4), 
                dhcp:      dhcp,
                reserve_a: (r1, r2, r3, r4),
                sys_a:     (s1, s2, s3, s4),
                app_a:     (a1, a2, a3, a4),
            }
            print "  Foscam Info: "
            print client
            clients.push(client)
        else:
            print "   Ignoring message of size " + str(len(msg))

    return clients

if __name__ == '__main__':
    foscam_poll()
