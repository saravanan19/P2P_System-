#!/usr/bin/python 
  
import socket 
import threading 
import P2S

RFCdic={}
peersdic ={}
RFCdic_lock=threading.Lock()
peersdic_lock=threading.Lock()
class ClientHandler(threading.Thread): 
 
    def __init__(self, client): 
        self.myrfs = []
        threading.Thread.__init__(self) 
        self.client_sock, self.client_addr = client
        self.client=client
        self.Hostname=""
        self.rfcList=[]
        return
    
    def removeIPfromPeerList(self):
        global peersdic
        peersdic_lock.acquire()
        try:
            if self.client in peersdic:
                del peersdic[self.client]
        finally:
            peersdic_lock.release()
            #print "Current Peer List after connection is closed:"
        #print self.peersDic
        return
    
    def removeRFCitem(self):
        global RFCdic
        RFCdic_lock.acquire()
        try:
            for rfcnum in self.rfcList:
                #print rfcnum
                for li in RFCdic[rfcnum]:
                    if self.Hostname in li:
                        RFCdic[rfcnum].remove(li)
                        if RFCdic[rfcnum] == []:
                            RFCdic.pop(rfcnum)
        finally:
            RFCdic_lock.release()
                        
                
    
    def decodeADD(self,dataDic):
        global RFCdic
        rfcNum=0
        rfcNum=dataDic['ADD'][1]
        version=dataDic['ADD'][2]
        self.Hostname= dataDic['Host:']
        port=int(dataDic['Port:'])
        Title=dataDic['Title:']
        if( port <0 or port > 65535  or rfcNum==0 or dataDic['ADD'][0]!="RFC" ):
            self.sendBadresponse()
            return
        elif version!= "P2P-CI/1.0":
            self.sendInvalidVersion()
            return
        else:
            self.rfcList.append(rfcNum)
            RFCdic_lock.acquire()
            try:
                if (RFCdic.has_key(rfcNum) == False):
                    RFCdic[rfcNum]=[ [rfcNum,Title,self.Hostname,port]] 
                else:
                    lis=RFCdic[rfcNum]
                    dup=False
                    for rfc,tit,host,po in lis:
                        if (rfc==rfcNum and tit==Title and host==self.Hostname and po==port):
                            dup=True
                            break
                    if dup==False:
                        lis.insert(0,[rfcNum,Title,self.Hostname,port])           
                print RFCdic
                self.sendADDResponse()                
            finally:
                RFCdic_lock.release()    
            return
            
    
    def decodeLOOKUP(self,dataDic):
        global RFCdic
        rfcNum=0
        rfcNum=dataDic['LOOKUP'][1]
        version=dataDic['LOOKUP'][2]
        
        self.Hostname= dataDic['Host:']
        port=int(dataDic['Port:'])
        Title=""
        Title=dataDic['Title:']
        if( port <0 or port > 65535  or rfcNum==0 or dataDic['LOOKUP'][0]!="RFC" or Title==""):
            self.sendBadresponse()
            return
        elif version!= "P2P-CI/1.0":
            self.sendInvalidVersion()
            return
        else:
            RFCdic_lock.acquire()
            try:
                if (RFCdic.has_key(rfcNum) == False):
                    self.sendNotFound()
                else:
                    print RFCdic[rfcNum]
                    self.sendLOOKUPResponse(RFCdic[rfcNum])                
            finally:
                RFCdic_lock.release()
            return
    
    
    def decodeLISTALL(self,dataDic):
        global RFCdic
        version=dataDic['LIST'][1]
        self.Hostname= dataDic['Host:']
        port=int(dataDic['Port:'])
        if( port <0 or port > 65535  or dataDic['LIST'][0]!="ALL" or version!= "P2P-CI/1.0" ):
            self.sendBadresponse()
            return
        elif version!= "P2P-CI/1.0":
            self.sendInvalidVersion()
            return
        else:
            li=[]
            RFCdic_lock.acquire()
            try:
                for key in RFCdic:
                    for rfcn,title,hostname,port in RFCdic[key]:
                        li.append([rfcn,title,hostname,port])
            finally:
                RFCdic_lock.release()
            print li
            self.sendLOOKUPResponse(li)                
            return
    
    
    def sendLOOKUPResponse(self,li):
        data=P2S.response(200,li)
        self.client_sock.sendall(data)
        return
    
    def sendADDResponse(self):
        data=P2S.response(200,'null')
        self.client_sock.sendall(data)
        return
    
    def sendBadresponse(self):
        data=P2S.response(400,'null')
        self.client_sock.sendall(data)
        return
    
    def sendNotFound(self):
        data=P2S.response(404,'null')
        self.client_sock.sendall(data)
        return
    
    def sendInvalidVersion(self):
        data=P2S.response(505,'null')
        self.client_sock.sendall(data)
        return
    
    def run(self):
        global peersdic
        print "Got connection"
        while True:
            data = self.client_sock.recv(1024)
            print "Data from the user"
            print data
            if data:
                linesDic=P2S.decodeHeader(data)
                if linesDic:
                    peersdic_lock.acquire()
                    try:
                        peersdic[self.client]= [linesDic['Host:'],linesDic['Port:']]
                    finally:
                        peersdic_lock.release()
                    print "Peers Dectionary"
                    print peersdic
                    if(linesDic.has_key('ADD') != False):
                        print "Calling ADD response"
                        self.decodeADD(linesDic)
                        
                    elif( (linesDic.has_key('LOOKUP') != False)  ):
                        print "Calling LOOKUP response"
                        self.decodeLOOKUP(linesDic)
                        
                    elif( (linesDic.has_key('LIST') != False) ):
                        print "Calling LIST response"
                        self.decodeLISTALL(linesDic)
                        
                    else:
                        self.sendBadresponse()
            else:    
                print "Closing connection"
                self.client_sock.close()
                self.removeRFCitem()
                print RFCdic
                self.removeIPfromPeerList()
                print peersdic
                break  
                
                return




class CentralServer:
    
    def __init__(self,p):
        self.port=p
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.bind()        
        
    def bind(self):
        self.sock.bind((socket.gethostname(), self.port)) 
        self.sock.listen(0) 
        print "Waiting_for_clients_..." 

    def accept(self): 
        client = self.sock.accept()
        self.Ch=ClientHandler(client)
        self.Ch.start()
        
 

def main():
    cs=CentralServer(7734)
    while(True):
        cs.accept()

if __name__ == "__main__":
    main()
