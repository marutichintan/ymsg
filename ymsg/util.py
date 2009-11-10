from ymsg import const
from ymsg.packet import *
import urllib2
import base64
import hashlib
import re


def readPacket(s):
    try:
        header = s.recv(20)
    except:
        pass
    if header:
        pIn = Packet()
        if header[:4] == pIn.magic and len(header) == 20:
            pIn.setType("IN")
            pIn.version   = header[4:8]
            pIn.length    = header[8:10]
            pIn.service   = header[10:12]
            pIn.status    = header[12:16]
            pIn.sid       = header[16:20]
            recivedSz     = 0
            while recivedSz < pIn.getLength() :
                try:
                    pIn.body += s.recv(pIn.getLength() - recivedSz)
                except:
                    pass
                recivedSz = len(pIn.body)
            return pIn
        else:
            raise BadHeader(header)
    else:
        return None

def writePacket(s, pOut):
    pOut.setType("OUT")
    s.send(pOut.getPacketData())

def getToken(u, p, c):
    fd = urllib2.urlopen(const.YAHOO_TOKEN_URL % (u, p, c))
    buff = fd.read()
    data = buff.split("\r\n")
    if data[0] == '0':
        return (const.YAHOO_RETCODE_OK, data[1].split("=")[1])
    elif data[0] == '100':
        return (const.YAHOO_RETCODE_ERR_UPMISSING, None)
    elif data[0] == '1013':
        return (const.YAHOO_RETCODE_ERR_UHASAT, None)
    elif data[0] == '1212':
        return (const.YAHOO_RETCODE_ERR_LOGIN, None)
    elif data[0] == '1218':
        return (const.YAHOO_RETCODE_ERR_UDEACTIVATED, None)
    elif data[0] == '1235':
        return (const.YAHOO_RETCODE_ERR_UNOTEXIST, None)
    else:
        return (const.YAHOO_RETCODE_ERR_LOCKED, None)

def getCrumbCookieYT(t):
    fd = urllib2.urlopen(const.YAHOO_LOGIN_URL % t)
    data = fd.read()
    crumb = data.split("\r\n")[1].split("=")[1]
    cookiey = data.split("\r\n")[2][2:]
    cookiet = data.split("\r\n")[3][2:]
    return (crumb, cookiey, cookiet)

def getHash(cr, ch):
    return hashlib.md5(cr + ch).digest()
    
def y64Encode(s):
    data = base64.b64encode(s)
    return data.replace("+",".").replace("/", "_").replace("=", "-")
    
def y64Decode(s):
    data = s.replace(".","+").replace("_", "/").replace("-", "=")
    return base64.b64decode(data)

def cleanTags(msg):
    regex = re.compile("\x1b\[\d+m|<font.*?>|</font>", re.UNICODE|re.IGNORECASE)
    return regex.sub("", msg)    
