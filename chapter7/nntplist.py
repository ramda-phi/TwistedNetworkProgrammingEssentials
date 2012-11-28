from twisted.news import nntp
#from twisted.protocols import nntp
from twisted.internet import protocol, defer


class NNTPGroupListerProtocol(nntp.NNTPClient):
    def connectionMade(self):
        nntp.NNTPClient.connectionMade(self)
        self.fetchGroup()

    def gotAllGroups(self, groups):
        groupnames = [groupInfo[0] for groupInfo in groups]
        self.factory.deferred.callback(groupnames)
        self.quit()

    def getAllGroupFailed(self, error):
        self.factory.deferred.errback(error)

    def connectionLost(self, error):
        if not self.factory.deferred.called:
            self.factory.deferred.errback(error)


class NNTPGroupListerFactory(protocol.ClientFactory):
    protocol = NNTPGroupListerProtocol

    def __init__(self):
        self.deferred = defer.Deferred()


if __name__ == '__main__':
    from twisted.internet import reactor

    def printGroups(groups):
        for group in groups:
            print group
        reactor.stop()

    def handleError(error):
        print >> sys.stderr, error.getErrorMessage()
        reactor.stop()

    import sys
    server = sys.argv[1]
    factory = NNTPGroupListerFactory()
    factory.deferred.addCallback(printGroups).addErrback(handleError)
    #reactor.connectTCP('sys.argv[1]', 119, factory)
    reactor.connectTCP(server, 119, factory)
    reactor.run()
