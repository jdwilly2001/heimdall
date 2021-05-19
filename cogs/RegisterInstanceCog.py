from discord import Cog, commands
from data import RealmInfo

class RegisterInstanceCog(Cog):

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config


    @command(name="watch")
    '''
    Watch over a realm. You need to tell heimdall about it first

    The command example would be
    !h watch {realm_name} id: {instance_id}
    '''
    async def register_server(ctx, realm_name, dummy_arg, server_identifier):
        server_info = ServerInfo(
            guild_id = ctx.guild.id,
            realm_name = realm_name,
            server_identifier = server_identifier,
            initiated_channel = ctx.channel.id
        )

        try:
            bot.store.store_realm(server_info)
            await ctx.send(f"Ah... I think I can see that realm now.")
        except:
            await ctx.send("Hmmm.. It seems there was a problem locating that realm. ")
            raise