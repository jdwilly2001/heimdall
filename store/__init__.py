from data import RealmInfo

class AbstractHeimdallStore(object):

    def __init__(self, config_dict):
        '''
        Initialize the store object.
        '''
        raise NotImplementedError("AbstractHeimdallStore is an abstract class. You cannot initialize it.")

    def store_realm(self, realm_info):
        '''
        Store the info about the realm to watch.
        '''
        raise NotImplementedError("AbstractHeimdallStore is an abstract class. You cannot initialize it.")        

    def get_realm(self, guild_id, realm_name):
        '''
        Retreive the GuildInfo for a realm with a given guild_id and name
        '''
        raise NotImplementedError("AbstractHeimdallStore is an abstract class. You cannot initialize it.")

