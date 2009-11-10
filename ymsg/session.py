from ymsg import const
from ymsg.packet import *
from ymsg.util import *
import socket
import threading


class Session():
    def __init__(self, u, p, invisible=False, threaded=True):
        self.username = u
        self.password = p
        if invisible:
            self.status = const.YAHOO_STATUS_INVISIBLE 
        else:
            self.status = const.YAHOO_STATUS_AVAILABLE
        self.threaded = threaded
        self.sid = 0
        self.worker = None
        self.connected = False
    
    def newThread(self, f, args=()):
        t = threading.Thread(target=f, args=args)
        t.deamon = True
        t.start()
        return t

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setblocking(1)
            self.sock.connect((const.YAHOO_PAGER_HOST, const.YAHOO_PAGER_PORT))
        except:
            if self.threaded:
                self.newThread(self.onDisconnect, (const.YAHOO_RETCODE_ERR_SRVCON,))
            else:
                self.onDisconnect(const.YAHOO_RETCODE_ERR_SRVCON)
            return
            
        pOut = Packet()
        pOut.setService(const.YAHOO_SERVICE_HANDSHAKE)
        pOut.setStatus(self.status)
        pOut.setSid(self.sid)
        writePacket(self.sock, pOut)
        
        pIn = readPacket(self.sock)
        
        pOut = Packet()
        pOut.setService(const.YAHOO_SERVICE_AUTH)
        pOut.setStatus(self.status)
        pOut.setSid(self.sid)
        pOut.appendBody(['1', self.username])
        writePacket(self.sock, pOut)
        
        pIn = readPacket(self.sock)
        self.sid = pIn.getSid()
        challenge = pIn['94']
        retcode, token = getToken(self.username, self.password, challenge)
        if retcode != const.YAHOO_RETCODE_OK:
            if self.threaded:
                self.newThread(self.onDisconnect, (retcode,))
            else:
                self.onDisconnect(retcode)
            return
        crumb, y, t = getCrumbCookieYT(token)
        yhash = y64Encode(getHash(crumb, challenge))
        
        pOut = Packet()
        pOut.setService(const.YAHOO_SERVICE_AUTHRESP)
        pOut.setStatus(self.status)
        pOut.setSid(self.sid)
        pOut.appendBody(['1', self.username])
        pOut.appendBody(['0', self.username])
        pOut.appendBody(['277', y])
        pOut.appendBody(['278', t])
        pOut.appendBody(['307', yhash])
        pOut.appendBody(['244', '2097087'])
        pOut.appendBody(['2', self.username])
        pOut.appendBody(['2', '1'])
        pOut.appendBody(['98', 'us'])
        pOut.appendBody(['135', '9.0.0.2162'])
        writePacket(self.sock, pOut)
        
        if self.threaded:
            self.worker = self.newThread(self.listner)
            self.newThread(self.onConnect)
        else:
            self.onConnect()
            self.listner()
    
    def isConnected(self):
        return self.connected
    
    def disconnect(self):
        if self.connected:        
            self.connected = False
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            if self.threaded:
                self.newThread(self.onDisconnect, (const.YAHOO_RETCODE_OK,))
            else:
                self.onDisconnect(const.YAHOO_RETCODE_OK)
            
    def listner(self):
        self.connected = True
        while self.connected:
            pIn = readPacket(self.sock)
            if pIn:
                self.sid = pIn.getSid()
                if pIn.getService() == const.YAHOO_SERVICE_PING:
                    pOut = Packet()
                    pOut.setService(const.YAHOO_SERVICE_PING)
                    pOut.setStatus(self.status)
                    pOut.setSid(self.sid)
                    writePacket(self.sock, pOut)
                elif pIn.getService() == const.YAHOO_SERVICE_MESSAGE:
                    src  = pIn['4']
                    dest = pIn['5']
                    msg  = cleanTags(pIn['14'])
                    if self.threaded:
                        self.newThread(self.onMessage, (src, dest, msg))
                    else:
                        self.onMessage(src, dest, msg)
                else:
                    if self.threaded:
                        self.newThread(self.onUnknownPacket, (pIn,))
                    else:
                        self.onUnknownPacket(pIn)
                
    def sendIm(self, w, m):
        if self.connected:
            pOut = Packet()
            pOut.setService(const.YAHOO_SERVICE_MESSAGE)
            pOut.setStatus(self.status)
            pOut.setSid(self.sid)
            pOut.appendBody(['0', self.username])
            pOut.appendBody(['1', self.username])
            pOut.appendBody(['5', w])
            pOut.appendBody(['14', m])
            writePacket(self.sock, pOut)
    
    def sendBuzz(self, w):
        self.sendIm(w, '<ding>')

    #Callbacks
    def onConnect(self):
        pass
    def onMessage(self, src, dest, msg):
        pass
    def onUnknownPacket(self, p):
        pass
    def onDisconnect(self, retcode):
        pass
