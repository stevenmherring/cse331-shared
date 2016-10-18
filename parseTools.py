from struct import *
#ID reference
IP_PACKET_ID = 8
TCP_PROTOCOL_ID = 6
UDP_PROTOCOL_ID = 17

#Static Packet Lengths
ETHERNET_LENGTH = 14

def ethernet_address(arg):
  ret = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(arg[0]) , ord(arg[1]) , ord(arg[2]), ord(arg[3]), ord(arg[4]) , ord(arg[5]))
  return ret

def init_packet_parse(packet, fd):
    #parse & unpack header, addresses from packet
    ethernet_header = packet[:ETHERNET_LENGTH]
    ethernet = unpack("!6s6sH" , ethernet_header) #splits into 6 char string, 6 char string, 2byte int
    ethernet_protocol = sniffSocket.ntohs(ethernet[2]) #last element is out protocol ID
    print "Dest MAC address: " + ethernet_address(packet[0:6]) + " Source MAC address: " + ethernet_address(packet[6:12]) + " Protocol type: " + str(ethernet_protocol))

    #Parse packets by type, IP first, what we really are looking for
    if ethernet_protocol == IP_PACKET_ID:
        if(parse_ip_packet(packet, ETHERNET_LENGTH, fd) == False):
            return False
    else:
        print "uhhhh not here yet"
    return True
def parse_ip_packet(packet, ethernet_length, fd):
    #parse header
    ipheader = packet[ethernet_length:ethernet_length+20] #extract 20 byte IP header
    #IP Header as defined by RFC noted with unpacked location [i]
    #Version / IHL[0] - DSCP / ECN[1] - LENGTH[2]
    #ID[3] - Flags / Frag OS[4]
    #TTL[5] - Protocol[6] - Check sum[7]
    #SOURCE[8]
    #DEST[9]
    #    0                   1                   2                   3
    #0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|Version|  IHL  |Type of Service|          Total Length         |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|         Identification        |Flags|      Fragment Offset    |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|  Time to Live |    Protocol   |         Header Checksum       |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                       Source Address                          |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                    Destination Address                        |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                    Options                    |    Padding    |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    ipheader = unpack("!BBHHHBBH4s4s", ipheader)
    version_ipheader = ipheader[0]
    version = version_ipheader >> 4 #version is the 4 MSB of initial byte
    ihl = version_ipheader & 0xF #ihl is the 4 LSB, mask off the 4 MSB
    ttl = ipheader[5]
    protocol = ipheader[6]
    src_address = socket.inet_ntoa(ipheader[8])
    dest_address = socket.inet_ntoa(ipheader[9])
    out_data = "Packet Number: " + packet_number + " Version: " + str(version) + " IHL: " + str(ihl) + " TTL: " + str(ttl) + " Protocol: " + str(protocol) + " Source Address: " + str(src_address) + " Destination Address: " + str(dst_address)
    packet_number++
    print out_data
    try:
        fd.write(out_data)
    except IOError as err:
        print str(err)
        return False
    ipheader_length = ihl * 4
    #check if tcp/udp/http/dns
    if protocol == TCP_PROTOCOL_ID:
        if(parse_tcp(packet, ipheader_length, fd) == False):
            return False
    elif protocol = UDP_PROTOCOL_ID:
        if(parse_udp(packet, ipheader_length, fd) == False):
            return False
    else:
        #other packet types
    return True

def parse_tcp(packet, ipheader_length, fd):
    #parse header
    start = ipheader_length + ETHERNET_LENGTH
    header = packet[start:start+20] #extract 20 byte tcp header
    #TCP header as defined by RFC 791
    #    0                   1                   2                   3
    #0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|          Source Port          |       Destination Port        |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                        Sequence Number                        |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                    Acknowledgment Number                      |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|  Data |           |U|A|P|R|S|F|                               |
    #| Offset| Reserved  |R|C|S|S|Y|I|            Window             |
    #|       |           |G|K|H|T|N|N|                               |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|           Checksum            |         Urgent Pointer        |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                    Options                    |    Padding    |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                             data                              |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    header = unpack("!HHLLBBHHH", header) #unpack packet
    src_port = header[0]
    dest_port = header[1]
    seq_number = header[2]
    ack_number = header[3]
    header_length = header[4] >> 4
    #print and write packet details
    out_data = "Source Port: " + str(src_port) + " Destination Port: " + str(dest_port) + " Sequence Number: " + str(seq_number) + " Acknowledgment Number: " + str(ack_number) + " TCP Length: " + strheader_length)
    print out_data
    try:
        fd.write(out_data)
    except IOError as err:
        print str(err)
        return False
    header_size = ETHERNET_LENGTH + ipheader_length + header_length * 4
    #print and write packet data
    #--TODO-
    #we need to check out_data for HTTP payloads.
    #Look for "HTTP/1.x" for HTTP
    #content-length: field will give the total size of the packet. (useful but not necessary)
    #Refere to RFC 2616 for reconstruction of HTTP
    out_data = pack[header_size:]
    if "HTTP/1." in out_data: #this condition isn't good enough to use, needs to be more exclusive
        if(parse_http(packet, out_data, fd) == False):
            return False
    else:
        print " Data: " + out_data
        try:
            fd.write(out_data)
        except IOError as err:
            print str(err)
            return False
    return True

def parse_udp(packet, ipheader_length, fd):
    start = ipheader_length + ETHERNET_LENGTH
    header = packet[start:start+8] #extract 8 byte udp header
    #UDP header as defined by RFC 791
    #    0      7 8     15 16    23 24    31
    # +--------+--------+--------+--------+
    # |     Source      |   Destination   |
    # |      Port       |      Port       |
    # +--------+--------+--------+--------+
    # |                 |                 |
    # |     Length      |    Checksum     |
    # +--------+--------+--------+--------+
    # |
    # |          data octets ...
    # +---------------- ...
    header = unpack("!HHHH", header)
    src_port = header[0]
    dest_port = header[1]
    length = header[2]
    checksum = header[3]
    #print and write packet details
    out_data = "Source Port: " + str(src_port) + " Destination Port: " + str(dest_port) + " Length: " + str(header_length) + " Checksum: " + str(checksum)
    print out_data
    try:
        fd.write(out_data)
    except IOError as err:
        print str(err)
        return False
    header_size = ETHERNET_LENGTH + ipheader_length + header_length
    #TODO
    #need to check if packet contains DNS data
    #RFC Reference TBD
    #print and write packet data
    out_data = pack[header_size:]
    print " Data: " + out_data
    try:
        fd.write(out_data)
    except IOError as err:
        print str(err)
        return False
    return True

def parse_http(packet, data, fd):
    #split raw http by :
    http_data_list = data.split("\r\n")
    print http_data_list
    http_data = dict(s.split(":") for s in http_data_list)
    print http_data
    try:
        #insert back the : and separate each header to its own line
        for key, value in http_data.iteritems():
            fd.write(key + ": " + value)
    except IOError as err:
        print str(err)
        return False
    return True

def parse_dns(packet, data, fd):