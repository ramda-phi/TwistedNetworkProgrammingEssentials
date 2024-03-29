from twisted.web import client, error as weberror
from twisted.internet import reactor
import sys, getpass, base64


def printPage(data):
    print data
    reactor.stop()


def checkHTTPError(failure, url):
    failure.trap(weberror.Error)
    if failure.value.status == '401':
        print >> sys.stderr, failure.getErrorMessage()
        # prompt for user name and password
        username = raw_input("User name: ")
        password = getpass.getpass("Password: ")
        basicAuth = base64.encodestring("%s:%s" % (username, password))
        authHeader = "Besic " + basicAuth.strip()
        # try to feach the page again with authentication
        return client.getPage(
            url, headers = {"Authorization": authHeader})
    else:
        return failure


def printError(failure):
    print >> sys.stderr, "Error:", failure.getErrorMessage()
    reactor.stop()


if len(sys.argv) == 2:
    url = sys.argv[1]
    client.getPage(url).addErrback(checkHTTPError, url).addCallback(
        printPage).addErrback(printError)
    reactor.run()
else:
    print "Usage: %s <URL>" % sys.argv[0]
