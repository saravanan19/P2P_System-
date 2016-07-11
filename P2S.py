import socket
import Status


def addRequest(rfcNum,rfcTitle,port):
    host = socket.gethostname()
    pktheader = "ADD RFC "+rfcNum+"  P2P-CI/1.0\r\n" + \
                "Host: "+host+"\r\n" + \
                "Port: "+port+"\r\n" + \
                "Title: "+rfcTitle+"\r\n"+ \
                "\r\n"
    return pktheader

def lookupRequest(rfcNum,rfcTitle,port):
    host = socket.gethostname()
    pktheader = "LOOKUP RFC "+rfcNum+"  P2P-CI/1.0\r\n"+ \
                "Host: "+host+"\r\n" + \
                "Port: "+port+"\r\n" + \
                "Title: "+rfcTitle+"\r\n" + \
                "\r\n"
    return pktheader

def listAllRequest(port):
    host = socket.gethostname()
    pktheader = "LIST ALL P2P-CI/1.0\r\n"+ \
                "Host: "+host+"\r\n" + \
                "Port: "+port+"\r\n" + \
                "r\n"
    return pktheader



def response(status, li):
    pktheader = "P2P-CI/1.0 "+str(status)+" "+Status.getResponsePhrase(status)+"\r\n\r\n" 
    pktdata  = ""
    if li=='null':
        pktdata+="\r\n"
        return pktheader+pktdata
    
    for rfcn,title,hostname,port in li:
        dataline = "RFC "+rfcn+" "+title+" "+hostname +" "+str(port)+"\r\n";
        pktdata+=dataline
    pktdata+="\r\n"
    return pktheader+pktdata

    

def readlines(buff,delim='\r\n'):
        while buff.find(delim) != -1:
                line, buff = buff.split('\r\n',1)
                yield line
        return


    
def decodeHeader(data):
    lines=[]
    linesDic={}
    
    for line in readlines(data):
        lines.append(line)
    print lines
    if lines:    
        for count,line in enumerate(lines):
            if line:
                data=line.split()
                if count!=0:
                    linesDic[data[0]]=data[1]                
                else:
                    linesDic[data[0]]=data[1:]            
                        
    #if linesDic:
    #   print linesDic
    return linesDic





def parseLookupResponse(resp,rfcnum,rfctitle):
    delimchunk = '\r\n\r\n'
    delimline ='\r\n'
    data =""
    
    
    if resp.find(delimchunk) != -1:
        header, data =  resp.split(delimchunk,1)
    else:
        return -1,-1,400
    
    print 'res header' 
    print header
    print 'data'
    print data
    
    datalines = []
            
            
    for line in readlines(data):
        if line:
            datalines.append(line)

    hl = header.split()
    
    if((hl[0].find("P2P-CI/")==0)):
        if(hl[0]=="P2P-CI/1.0"):
            if(hl[1]=="404"):
                return -1,-1,404
            if (hl[1]=="200" and hl[2]=="OK"):
                dl = datalines[0].split(" ")
                length = len(dl)
                if(len < 5):
                    return -1,-1,400
                if(dl[0]!="RFC" or dl[1]!=rfcnum):
                    return -1,-1,400
                return dl[length-2],dl[length-1],200
                
            elif (hl[1]=="200"):
                return -1,-1,400
            else:
                return -1,-1,hl[1]
        else:
            return -1,-1,505
    else:
        return -1,-1,400
    



        
        