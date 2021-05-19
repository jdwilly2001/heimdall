from store import AbstractHeimdallStore
from data import RealmInfo
import json
import os

class FileHeimdallStore(AbstractHeimdallStore):

    def __init__(self, config_dict):
        driver_config = config_dict.get("store")
        
        self.data_path = driver_config.get("data_dir")

        print("Initializing file store...")
        if not os.path.exists(self.data_path):
            print(f"Specified data directory does not exist. Creating {self.data_dir}")
            os.makedirs(self.data_path)
    

    def store_realm(self, realm_info):
        realm_info = None
        guild_path = os.path.join(self.data_path, realm_info.guild_id)
        realm_info_file = os.path.join(guild_path, guild_info.realm_name)

        if not os.path.exists(guild_path):
            print(f"Guild store directory does not exist yet, creating...")
            os.mkdir(guild_path)

        with open(realm_info_file, "w") as file:
            file.write(json.dumps(realm_info))
    

    def get_realm(self, guild_id, realm_name):
        realm_info = None
        realm_info_file = os.path.join(self.data_path, guild_id, realm_name)

        if os.path.exists(realm_info_file):
            with open(realm_info_file, "r") as file:
                realm_info = json.load(realm_info_file)

        return realm_info
        