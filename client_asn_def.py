#!/usr/bin/env python3

from multiprocessing import Process, Queue
import socket
from threading import Thread
import threading
import binascii
import sctp
import time
from pycrate_asn1dir import S1AP
from pycrate_asn1rt.utils import *
from binascii import hexlify, unhexlify
from six.moves import configparser

# Getting input data for request_parameter.txt
config = configparser.ConfigParser()
configFilePath = r'/home/amit/Documents/myproject/Simulator/request_parameter.txt'
config.read(configFilePath)
config.sections()
server_ip = config['SERVER']['server_ip']
server_port = config['SERVER']['server_port']
AP_Starting_packet = config['ATTRIBUTE']['AP_Starting_packet']
Number_of_packet = config['ATTRIBUTE']['Number_of_packet']
delay_in_second = int(config['ATTRIBUTE']['delay_in_second'])
packet_limit = int(config['ATTRIBUTE']['packet_limit'])
exit_time = int(config['ATTRIBUTE']['exit_time'])

PDU = S1AP.S1AP_PDU_Descriptions.S1AP_PDU

# Server host and Port
HOST = server_ip
PORT = int(server_port)

id = int(AP_Starting_packet)


# Creating S1Ap packet
def creating_packets(id):
    msg_list = []
    for num in range(0,int(Number_of_packet)):
        IEs = []
        IEs.append({'id': 59, 'value': ('Global-ENB-ID', {'pLMNidentity': b'\x45\xf6\x42', 'eNB-ID': ('homeENB-ID',(id, 28))}), 'criticality': 'reject'})
        IEs.append({'id': 60, 'value': ('ENBname', 'ipaccess'), 'criticality': 'ignore'})
        IEs.append({'id': 64, 'value': ('SupportedTAs', [{'tAC': b'\x00\x1b', 'broadcastPLMNs': [b'\x45\xf6\x42']}]), 'criticality': 'reject'})
        IEs.append({'id': 137, 'value': ('PagingDRX', 'v128'), 'criticality': 'ignore'})
        val = ('initiatingMessage', {'procedureCode': 17, 'value': ('S1SetupRequest', {'protocolIEs': IEs}), 'criticality': 'reject'})
        id = id + 1
        PDU.set_val(val)
        #print(PDU.to_asn1())
        msg =  hexlify(PDU.to_aper())
        msg = binascii.unhexlify(msg)
        msg_list.append(msg)

    return msg_list

# Sending packets
def send_packet(msg,count):
    # Enabiling Heartbeat
    ss = sctp.paddrparams.flags_HB_ENABLE
    ss = 1

    # Creating sctp socket
    s = sctp.sctpsocket_tcp(socket.AF_INET)
    s.connect((HOST, PORT))

    # Setting Heartbeat interval
    # getpaddrObj = s.get_paddrparams(0, (HOST, PORT))
    # getpaddrObj.hbinterval = 1
    # s.set_paddrparams(getpaddrObj)
    q = s.sctp_send(msg,ppid= 301989888)
    #data = s.recv(1024)
    # if data:
    #     print("GOT RESPONSE FOR homeENB-ID NO.{}".format(count))
    # else:
    #     print("NO RESPONSE FOR homeENB-ID NO.{}".format(count))
    #time.sleep(1)

num_processes = 1
processes = []
count = int(AP_Starting_packet)

if __name__ == '__main__':
    while True:
        my_list = creating_packets(id)
        start = time.time()
        for msg in my_list:
            process_name = "Process {}".format(num_processes)
            q = Queue()
            p = Process(target=send_packet(msg,count), name=process_name)
            num_processes = num_processes + 1
            count = count + 1
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        end = time.time()

        print("With {} Processes, we took {} seconds to send {} packet".format(num_processes-1,end-start,num_processes-1))
        id = id + int(Number_of_packet)
        my_list = creating_packets(id)
        if num_processes < packet_limit:
            time.sleep(delay_in_second)
            print('in loop')
        else:
            break


    print('out of loop')
    time.sleep(exit_time)
