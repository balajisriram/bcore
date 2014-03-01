from BCore.Classes.ClientAndServer.BServer import BServer


class BServerLocal(BServer):
    """
        BSERVERLOCAL  is a BServer which defaults to using *localhost*,
        which subjects are allowed in which station and data storage locations.
            serverID            : string Identifier
            serverDataPath      : path set by the object automatically
            stations            : list of stations
            subjects            : list of subjects
            assignments         : dictionary with keys being subjectID
                                and values being list of stationIDs
            revisionControl     : dictionary with access to details about
                                the repository
    """

    def __init__(server, **kwargs):
        super(BServerLocal, server).__init__(**kwargs)
        # this is the only substantial change in BServerLocal
        server.serverIP = 'localhost'


class DefaultBServerLocal(BServerLocal):

    def __init__(self):
        kw_values = {
            'serverID': 0,
            'serverName': 'DefaultLocalServer'
            }
        super(DefaultBServerLocal, self).__init__(**kw_values)


if __name__ == "__main__":
    print("here")
