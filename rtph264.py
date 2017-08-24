import socket
import bitstring

MAX_RTP_PKT_LEN = 4096

TYPE_SINGLE_NALU_01 = 1
TYPE_SINGLE_NALU_23 = 23
TYPE_STAPA = 24
TYPE_NALU_FUA = 28
START_BYTES = "\x00\x00\x00\x01"

class RFC3984(object):

    def parse_frame(self, pay):

        frame = None

        bt = bitstring.BitArray(bytes=pay)

        bc = 0; lc=0;
 
        fb=bt[bc] # i.e. "F"
        nri=bt[bc+1:bc+3].uint # "NRI"
        nlu0=bt[bc:bc+3] # "3 NAL UNIT BITS" (i.e. [F | NRI])
        typ=bt[bc+3:bc+8].uint # "Type"

        print "F, NRI, Type :", fb, nri, typ
        #print "nlu0 : ", nlu0 

        bc+=8; lc+=1;

        start=bt[bc] # start bit
        end=bt[bc+2] # end bit
        nlu1=bt[bc+3:bc+8] # 5 nal unit bits

        nlu = nlu0+nlu1
        head = START_BYTES + nlu.bytes
        print ">>>type", typ
        if (typ >= TYPE_SINGLE_NALU_01) and (typ <= TYPE_SINGLE_NALU_23):
            print ">>> Single NALU", start
            #frame = head+pay[lc:]
            frame = START_BYTES + pay[lc:] 
        elif typ == TYPE_NALU_FUA:
            if (start):
                print ">>> First FUA"
                lc+=1 
                frame = head+pay[lc:]
            else:
                print ">>> FUA" 
                lc+=1
                frame = pay[lc:]
            
        
        else:
            print ">>> Else"

        return frame, typ

class RTP(object):

    def __init__(self, file_name):
        self._first_pkt = False
        self._rtp_sn = 0
        self._payload_type = None

        self._file = open(file_name, 'wb')

        self._rfc3984 = RFC3984()
        
        self._first_fua = False

    def parse_hader(self, pkt):

        bt=bitstring.BitArray(bytes=pkt)
        if self._first_pkt == False:
            self._first_pkt = True
 
        v2=bt[0:2]
        version=bt[0:2].uint # version
        p=bt[3] # P
        x=bt[4] # X
        cc=bt[4:8].uint # CC
        m=bt[9] # M
        pt=bt[9:16].uint # PT
        sn=bt[16:32].uint # sequence number
        timestamp=bt[32:64].uint # timestamp
        ssrc=bt[64:96].uint # ssrc identifier


        print "version, p, x, cc, m, pt",version,p,x,cc,m,pt 
        print "sequence number, timestamp",sn,timestamp

        lc=12 # so, we have red twelve bytes
        bc=12*8 # .. and that many bits
        cids=[]
        for i in range(cc):
            cids.append(bt[bc:bc+32].uint)
            bc+=32; lc+=4;
        print "csrc identifiers:",cids
 
        if (x):
            # this section haven't been tested.. might fail
            hid=bt[bc:bc+16].uint
            bc+=16; lc+=2;

            hlen=bt[bc:bc+16].uint
            bc+=16; lc+=2;

            print "ext. header id, header len",hid,hlen

            hst=bt[bc:bc+32*hlen]
            bc+=32*hlen; lc+=4*hlen;

        frame, frame_type = self._rfc3984.parse_frame(pkt[lc:])
   
        #if frame_type == TYPE_NALU_FUA:
        #    self._first_fua = True
  
        if frame != None and frame_type == TYPE_NALU_FUA:
            self._file.write(frame)
   
    def recv_pkt(self, pkt):
       self.parse_hader(pkt)


def main():
    address = ('127.0.0.1', 1236)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(address)
    #startbytes = "\x00\x00\x00\x01"X
    #x = bitstring.BitArray(bytes = startbytes)
    #y=len(x)
    #print y
    rtp_parser = RTP("input.264")

    while True:
        data, addr = s.recvfrom(MAX_RTP_PKT_LEN)
        if not data:
            print "client has exist"
            break
        rtp_parser.recv_pkt(data)

    s.close()

if __name__ == '__main__':

    main()

