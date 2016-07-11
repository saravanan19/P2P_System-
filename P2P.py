import platform
import Status
import datetime
import os.path
import time


def getRequestHeader(rfcNum,host):
    opsys = platform.system()+" "+platform.release()+" "+platform.version()
    pktheader = "GET RFC "+rfcNum+" P2P-CI/1.0\r\n" + \
                "Host: "+host+"\r\n" + \
                "OS: "+opsys+"\r\n" + \
                "\r\n"
    return pktheader
    
    
    
def getResponseHeader(status,fi):
    opsys = platform.system()+" "+platform.release()+" "+platform.version()
    #path = 'C:\\SARAVANANB\\NCSU MAIN\\NCSU-Sem1\\CSC505\\Programs\\P2P\\P2PFilesrc\\1234.txt'
    
    pktheader = "P2P-CI/1.0 "+str(status)+" "+Status.getResponsePhrase(status)+ "\r\n" \
                "Date: "+str(datetime.datetime.now().time()) + "\r\n" \
                "OS: "+opsys+"\r\n" 
    if(fi!='null'):
        contlen = os.path.getsize(fi)
        pktheader+="Last-Modified: "+str(time.ctime(os.path.getmtime(fi))) + "\r\n" +\
        "Content-Length: " + str(contlen) + "\r\n" + \
        "Content-Type: text/text\r\n"
        
    pktheader+="\r\n"
    
    return pktheader
    
                

def validateGetRequest(header,rfclist):
    lines = []
    print 'P2P Decoder header'
    for line in readlines(header):
        lines.append(line)
        
    print 'request'
    print header

    hl = lines[0].split()
    print hl[0], hl[1], hl[3][0:6]
    if(hl[0]=="GET" and hl[1]=="RFC" and (hl[3][0:6]=="P2P-CI")):
        if(hl[3]=="P2P-CI/1.0"):
            if rfclist.has_key(hl[2]):
                return 200,hl[2] 
            else:
                print 'inside'
                return 404,-1
        else:
            return 505,-1
    else:
        print 'last'
        return 400,-1


def validateGetReponse(header):
    lines = []
    print 'P2P response header'
    for line in readlines(header):
        lines.append(line)
        
    print header

    hl = lines[0].split()
    if(hl[0][0:6]=="P2P-CI" ):
        if(hl[0]=="P2P-CI/1.0"):
            if(hl[1]=='200' and hl[2]=='OK'):
                return 200 
            elif(hl[1]=='404'):
                return 404
            else:
                return 400
        else:
            return 505
    else:
        return 400
    


def readlines(buff,delim='\r\n'):
        while buff.find(delim) != -1:
                line, buff = buff.split('\r\n',1)
                yield line
        return
    
    
  