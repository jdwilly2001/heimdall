
class RealmInfo(object):
    '''
    RealmInfo object is a value object to store information about a realm
    '''

    def __init__(self, guild_id, realm_name, server_identifier, initiated_channel_id, runtime_hours=4):
        self.realm_name = realm_name
        self.guild_id = guild_id
        self.server_identifier = server_identifier
        self.initiated_channel_id = initiated_channel_id
        self.runtime_hours = runtime_hours
   

    def __str__(self):
        return f"Realm Info: {self.__dict__()}"


    
