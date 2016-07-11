#!/usr/bin/python 
import socket 
import time
import P2S
import P2P
import sys
from random import randint
import threading 
import os 
import platform
import Status
from _socket import gethostname





CIIP = raw_input("Enter the CI IP address: ")
rfclist = {}
srcdir=""
dstdir=""
ostype = platform.system()
print ostype
if(ostype=="Windows"):
    srcdir = os.getcwd()+"\\P2PFilesrc"
    dstdir = os.getcwd()+"\\P2PFiledst"
else:
    srcdir = os.getcwd()+"/P2PFilesrc"
    dstdir = os.getcwd()+"/P2PFiledst"

        

class rfc_client:
    
    def __init__(self, number, title):
        self.number = number
        self.title = title
    
    def getaslist(self):
        return self.number , self.title

class PeerClient(threading.Thread):
    def __init__(self, ip, serverport, listenport):
        threading.Thread.__init__(self) 
        self.ser_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.ip = ip
        self.serverport = serverport
        self.connect()
        self.listenport = listenport
        return
    
    def connect(self):
        self.ser_sock.connect((self.ip, self.serverport))
    
    def run(self):
        #sending all rfc files details to centralized index
        global rfclist
        global srcdir, dstdir
        #for key,value in rfclist.iteritems():
        #   self.sendADDRequest(key, "RFC"+key)
        
        while True:
            print "Please select from the following option"
            print "1.ADD RFC to  CI server"
            print "2.LOOKUP request to CI Server "
            print "3.List all request to CI server"
            print "4.Download rfc"
            print "5.Exit"
            user_choice= raw_input()
            if user_choice =='1':
                rfc_num=raw_input("Enter RFC Number to Add")
                rfc_title=raw_input("Enter RFC Title to Add")
                print "Sending Add RFC to  CI server"
                res = self.checkRFCAvailability(rfc_num)
                if res==1:
                    if(ostype=="Windows"):
                        rfclist[rfc_num]= srcdir+'\\rfc'+str(rfc_num)+'.pdf' 
                    else:
                        rfclist[rfc_num]= srcdir+'/rfc'+str(rfc_num)+'.pdf'
                    self.sendADDRequest(rfc_num,rfc_title)
                else:
                    print 'File Not available'
                    print 'Save the file in the format -> rfc'+str(rfc_num)+'.pdf <- in P2PFilesrc Folder\n'   
            elif user_choice=='2':
                rfc_num=raw_input("Enter RFC Number to lookup")
                rfc_title=raw_input("Enter RFC Title to lookup")
                print "Sending lookup request"
                self.sendLookUpRequest(rfc_num,rfc_title)
            elif user_choice=='3':
                print "Sending list all request"
                self.sendListAllRequest()
            elif user_choice=='4':
                print 'Downloading RFC'
                rfc_num=raw_input("Enter RFC Number to download")
                rfc_title=raw_input("Enter RFC Title to download")
                resp = self.sendLookUpRequest(rfc_num,rfc_title)
                host,port,stat = P2S.parseLookupResponse(resp,rfc_num,rfc_title)
                print 'stat' + str(stat)
                if(stat==200):
                    self.downloadRFC(rfc_num, host, int(port))
                else:
                    print "Download Failed: "+Status.getResponsePhrase(stat)
            elif user_choice=='5':
                print "Exiting program"
                print("socket closed")
                self.ser_sock.close()
                os._exit(1)
                break
            else:
                print "Invalid input"
            
        return
    
    
    def sendLookUpRequest(self,rfc_num,rfc_title):
        self.ser_sock.sendall(P2S.lookupRequest(rfc_num,rfc_title, str(self.listenport))) 
        resp = self.ser_sock.recv(1024)
        print resp

        return resp
    
    def sendADDRequest(self,rfc_num,rfc_title):
        self.ser_sock.sendall(P2S.addRequest(rfc_num,rfc_title, str(self.listenport))) 
        resp = self.ser_sock.recv(1024)
        print resp
        
        return resp
    
    
    
    def sendListAllRequest(self):
        self.ser_sock.sendall(P2S.listAllRequest(str(self.listenport)))
        resp = self.ser_sock.recv(1024)
        print resp
        
        return resp
    
    def checkRFCAvailability(self,rfcnum):
        global srcdir
        srcpath = srcdir
        files =  os.listdir(srcpath);
        for f in files:
            if (f=="rfc"+rfcnum+".pdf"):
                return 1;
        return -1;

    def downloadRFC(self, rfcNum, hostname, port):
        global srcdir, dstdir
        # Get details from server using P2S Lookup request
        request = P2P.getRequestHeader(rfcNum, hostname)
        peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        #peer_sock.connect((socket.gethostname(), port))
        peer_sock.connect((hostname, port))
        peer_sock.send(request)
        
        l = peer_sock.recv(200)
        #parse response
        res = P2P.validateGetReponse(l)
        if(res==200):
            if (ostype=="Windows"):
                fpath = dstdir+"\\rfc"+rfcNum+".pdf"
            else:
                fpath = dstdir+"/rfc"+rfcNum+".pdf"
            print 'fpath '+ fpath
            f = open(fpath, "wb")
            print l    
            data = peer_sock.recv(1024)
            while (data):
                f.write(data)
                data = peer_sock.recv(1024)
                if(sys.getsizeof(data) == 0):
                    break;
        else:
            print 'Download failed: '+Status.getResponsePhrase(res)
        f.close()        
        peer_sock.close()



class uploadHandler(threading.Thread): 
    def __init__(self, client):
        threading.Thread.__init__(self) 
        self.client_sock, self.client_addr = client
        self.client = client 
        return
    
    def run(self):
        global rfclist
        data = self.client_sock.recv(250)  # Download request
        print 'Download request received'
        res, rfc = P2P.validateGetRequest(data, rfclist)
        
        #res,rfc = 200 , 200
        if(res == 200):
            if (data):
                segSize = 1024;
                if(ostype=="Windows"):
                    filepath = srcdir+"\\rfc"+rfc+".pdf"
                else:
                    filepath = srcdir+"/rfc"+rfc+".pdf"
                f = open(filepath, "rb")
                pktheader = P2P.getResponseHeader(200, filepath)
                self.client_sock.send(pktheader)
                data = f.read(segSize)
                while (data):
                    self.client_sock.sendall(data)
                    data = f.read(segSize)
                f.close()
                self.client_sock.close()
                print 'upload complete'
        else:
            pktheader = P2P.getResponseHeader(res, 'null')
            self.client_sock.send(pktheader)
            print 'Upload Failed: '+Status.getResponsePhrase(res)
        
        self.client_sock.close()
        return
    
    
    
    
class PeerServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.port = 0
    def bind(self):
        while(True):
            try:
                self.port = randint(1024, 10000)
                self.sock.bind((socket.gethostname(), self.port)) 
                break;
            except:
                continue;
        self.sock.listen(2)    
        return self.port

    def accept(self): 
        print 'server waiting for request'
        client = self.sock.accept()
        self.Ph = uploadHandler(client)
        self.Ph.start()

def findLocalRFCFiles():
    global rfclist, srcdir
    srcpath = srcdir
    files =  os.listdir(srcpath);
    for f in files:
        l = len(f)
        if f.startswith("rfc") and f.endswith(".pdf"):
            rfclist[f[3:l-4]] = srcpath+'\\'+ f
            
def checkEnvSetup():
    global srcdir,dstdir
    if not os.path.exists(srcdir):
        os.makedirs(srcdir)
    if not os.path.exists(dstdir):
        os.makedirs(dstdir)

def main():
    global CIIP
    checkEnvSetup()
    findLocalRFCFiles()
    peersever = PeerServer()
    listenport = peersever.bind()
    serverport = 7734
    if(CIIP=='localhost'):
        pclient = PeerClient(socket.gethostname(), serverport, listenport)
    else:
        pclient = PeerClient(socket.gethostname(), serverport, listenport)
    pclient.start()  
    
    while(True):
        peersever.accept()
    
if __name__ == "__main__":
    main()



