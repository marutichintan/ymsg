from ymsg.session import Session
from ymsg import const

class YmsgClient(Session):
    def onConnect(self):
        print "Hi!"
    
    def onMessage(self, src, dest, msg):
        print "%s: %s" % (src, msg)
    
    def onUnknownPacket(self, p):
        print p
        
    def onDisconnect(self, retcode):
        if retcode == const.YAHOO_RETCODE_OK:
            print "Bye!"
        elif retcode == const.YAHOO_RETCODE_ERR_SRVCON:
            print "Error connecting to server."
        elif retcode == const.YAHOO_RETCODE_ERR_UPMISSING:
            print "Username or password is missing."
        elif retcode == const.YAHOO_RETCODE_ERR_UHASAT:
            print "Username contains @yahoo.com or similar which needs removing."
        elif retcode == const.YAHOO_RETCODE_ERR_LOGIN:
            print "Username or password is incorrect."
        elif retcode == const.YAHOO_RETCODE_ERR_UDEACTIVATED:
            print "The account has been deactivated by Yahoo."
        elif retcode == const.YAHOO_RETCODE_ERR_UNOTEXIST:
            print "Username does not exist."
        elif retcode == const.YAHOO_RETCODE_ERR_LOCKED:
            print "Account locked."
        else:
            print ":("
            

        
y = YmsgClient("username", "password")
y.connect()
while y.isConnected():
        who = raw_input("who: ")
        msg = raw_input("msg: ")
        y.sendIm(who, msg)
y.disconnect()