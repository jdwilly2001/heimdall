from discord.ext.commands import Cog, command
from data import RealmInfo

class StartInstanceCog(Cog):

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    #Update CloudFlare - Example: https://github.com/cloudflare/python-cloudflare/blob/master/examples/example_update_dynamic_dns.py#L77
    def _update_cloudflare(self, public_ip):
        #CloudFlare Client
        cf_token = self.config.get("cloudflare").get("cloudflare_access_token")
        cf = CloudFlare.CloudFlare(token=cf_token)
        
        #Parameters
        cf_zone_id = self.config.get("cloudflare").get("dns_zone_id")
        cf_endpoint = self.config.get("cloudflare").get("endpoint_name")

        params = {'name':cf_endpoint, 'match':'all'}
        main_endpoint = cf.zones.dns_records.get(cf_zone_id, params=params)
        main_endpoint_id = main_endpoint[0]['id']

        #Update the CF entry
        dns_record = {
            'name': cf_endpoint,
            'type': "A",
            'content': public_ip,
            'proxied': True,
        }

        try:
            dns_record = cf.zones.dns_records.put(cf_zone_id, main_endpoint_id, data=dns_record)
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/zones.dns_records.put %s - %d %s - api call failed' % (cf_endpoint, e, e))
        print("CloudFlare UPDATED!")

        #Delay for 10 seconds while cloudflare updates
        time.sleep(10)
        return cf_endpoint

    @command()
    async def start(ctx, realm_name):
    '''
    Start the realm with the given name

    :param realm_name: Name of the realm you wish to start
    :type realm_name: str
    '''
    
    # use the store on the bot to get the realm info
    try:
        realm_info = bot.store.get_realm(ctx.guild_id, realm_name)
    except Exception as e:
        await ctx.send("I am having some trouble accessing my memory right now. Try again another time.")
        raise

    if not realm_info:
        await ctx.send("I do not know of that realm. Perhaps it is known by another name")

    #TODO: abstract aws implementation into specific AWS driver
    realm_instance_id = realm_info.server_identifier

    realm_instance = ec2.Instance(realm_instance_id)
    status = realm_instance.state["Name"]
    if status == "stopped":
        await ctx.send(f"Please wait while I connect you to the {realm_name} realm!")
        realm_instance.start()
        
        operation_time = 0
        poll_frequency_ms = 5000 # 5 second polling interval
        operation_timeout = 300000
        while status != "running":
            print("Checking EC2 instance status...")
            await ctx.trigger_typing()
            time.sleep(poll_frequency_ms/1000)
            realm_instance.reload()
            status = realm_instance.state["Name"]
            print(f"Current status: {status}")
            operation_time += poll_frequency_ms
            if operation_time > operation_timeout:
                await ctx.send(f"There was some difficulty connecting to the {realm_name} realm. Please contact the keeper of that realm. (Administrator)")
                break
        
        if status == "running":
            public_ip_address = realm_instance.public_ip_address
            cloudflare_endpoint = self.update_cloudflare(public_ip_address)
            await ctx.send(f"The {realm_name} realm is online. You may proceed with care to the realm. Stay safe. I'll be watching for your return.")
            await ctx.send(f"https://{cloudflare_endpoint} -- https://{public_ip_address}")

            now = datetime.now()
            stop_after = now + timedelta(hours=4)

            tag = realm_instance.create_tags(
                Tags=[
                    {
                        "Key": "heimdall.stopafter",
                        "Value": f"{datetime.timestamp(stop_after)}"
                    }
                ]
            )
    else:
        await ctx.send(f"The gateway to {realm_name} is in a strange state. ({status}). Please try again in a moment or contact the realm's keeper.")
