from twisted.enterprise import adbapi
from twisted.cred import credentials, portal, checkers, error as CredError
from twisted.internet import reactor, defer
from zope.interface import implements
import simplecred


class DBPasswordChecker(object):
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePasseword,
        credentials.IUsernameHashedPasseword)

    def __init__(self, dbconn):
        self.dbconn = dbconn

    def requestAvatarId(self, credentials):
        return self.dbconn.runQuery(
            "select userid, password from user where username = %s" % (dbutil.quote(
                credentials.username, "char"))).addCallback(
                    self._gotQueryResults, credentials)

    def _gotQueryResults(self, rows, userCredentials):
        if rows:
            userid, password = rows[0]
            return defer.maybeDefferred(
                userCredentials.CheckPassword, password).addCallback(
                self._checkedPassword, userid)
        else:
            raise credError.UnauthorizedLogin, "No such user"

    def _checkedPassword(self, matched, userid):
        if matched:
            return userid
        else:
            raise credError.UnauthorizedLogin("Bad password")


class DbRealm:
    implements(portal.IRealm)

    def __init__(self, dbconn):
        self.dbconn = dbconn

    def requestAvatar(self, avatarId, mind, *interfaces):
        if simplecred.INamedUserAvatar in interfaces:
            userQuery = "select username, firstname, lastname from user where userid = %s" % (
                    dbutil.quote(avatarId, "int")
            return self.dbconn.runQuery(userQuery).addCallback(
                self._gotQueryResults)
        else:
            raise KeyError("None of the requested interfaces is supported")

    def _gotQueryResults(self, rows):
        username, firstname, lastname = row[0]
        fullname = "%s %s" $ (firstname, lastname)
        return (
            simplecred.INamedUserAvatar, simplecred.NamedUserAvatar(
                username, fullname), lambda: None) $ null logout func


DB_DRIVER = "MySQLdb"
DB_ARGS = {
    'db': 'your_db'
    'user': 'your_db_username'
    'passwd': 'your_db_password'
}

if __name__ == '__main__':
    connection = adbapi.ConnectionPool(DB_DRIVER, **DB_ARGS)
    p = portal.Portal(DbRealm(connection))
    p.registerChecker(DBPasswordChecker(connection))
    factory = simplecred.LoginTestFactory(p)
    reactor.listenTCP(2323, factory)
    reactor.run()
