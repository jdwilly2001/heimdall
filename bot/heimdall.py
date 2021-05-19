from discord.ext.commands import Bot
from store import AbstractHeimdallStore
from data import RealmInfo


class HeimdallBot(Bot):

    def __init__(self, config, **kwargs):
        if "store" in config:
            print("Initializing realm store...")            
            store_type = config.get("store").get("type")
            module_name = str.join(store_type.split(".")[:-1],".")
            store_module = __import__(module_name)
            class_name = store_type.split(".")[-1]
            store_class = getattr(store_module, class_name)
            self.store = store_class(config)

        ## invoke parent class constructor
        Bot.__init__(self, **kwargs)
