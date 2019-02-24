#!/usr/bin/env python3

import socket
import sctp
from pycrate_asn1dir import S1AP
from pycrate_asn1rt.utils import *
from binascii import hexlify, unhexlify

PDU = S1AP.S1AP_PDU_Descriptions.S1AP_PDU

# Listining ip and host
HOST = '127.0.0.1'
PORT = 36412

# Ebabling Heartbeat
ss = sctp.paddrparams.flags_HB_ENABLE
ss = 1

# Creating Socket
s = sctp.sctpsocket_tcp(socket.AF_INET)
s.bind((HOST, PORT))
s.listen()


while True:
    conn, addr = s.accept()
    data = conn.recv(1024)
    if not data:
        break
    print('Received',repr(data))

    conn.sendall(data)
