import discord
import asyncio
import time
import yaml
from discord.ext import commands
import re
import boto3
import CloudFlare



config = None
try:
    with open("./config.yaml", "r") as config_file:
        config = yaml.load(config_file)
except:
    raise RuntimeError("Failed to load configuration file!")

boto_session = boto3.session.Session(
    aws_access_key_id=config.get("aws").get("access_key_id"),
    aws_secret_access_key=config.get("aws").get("secret_access_key"),
    region_name=config.get("aws").get("region")
)

ec2 = boto_session.resource("ec2")
   
    
bot = commands.Bot(
    command_prefix=["heimdall ","heim ","!h "],
    description="A bot who will watch over your self-hosted gaming worlds and protect your wallet from the Giants!",
    case_insensitive=True
)

@bot.check
async def echo_message(ctx):
    print(ctx)
    return True

@bot.command()
async def ping(ctx):
    '''
    A simple ping/pong command to see if i am alive
    '''
    await ctx.send("PONG")

@bot.command()
async def status(ctx, realm_name="foundry"):
    '''
    Describes the status of the realm

    :param realm_name: Name of the realm you wish to check status 
    :type real_name: str

    '''
    if realm_name in config["realms"]:
        realm_instance_id = config["realms"][realm_name]["instance_id"]
    else:
        await ctx.send("I do not know if that realm. Maybe its known by some other name?")
        return

    realm_instance = ec2.Instance(realm_instance_id)
    status = realm_instance.state["Name"]
    public_ip_address = realm_instance.public_ip_address

    if status == "running":
        reply_message = f"The gateway to the {realm_name} realm is currently open at https://{public_ip_address}. Enjoy."

    else:
        reply_message = f"The gateway to the {realm_name} realm is closed currently."

    await ctx.send(reply_message)

@bot.command()
async def start(ctx, realm_name="foundry"):
    '''
    Start the realm with the given name

    :param realm_name: Name of the realm you wish to start
    :type realm_name: str
    '''

    if realm_name in config["realms"]:
        realm_instance_id = config["realms"][realm_name]["instance_id"]
    else:
        await ctx.send("I do not know if that realm. Maybe its known by some other name?")
        return

    realm_instance = ec2.Instance(realm_instance_id)
    status = realm_instance.state["Name"]
    if status == "stopped":
        await ctx.send(f"Please wait while I connect you to the {realm_name} realm!")
        realm_instance.start()
        
        operation_time = 0
        poll_frequency_ms = 5000 # 5 second polling ineterval
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
        
        print("Done with the loop.... ")
        if status == "running":
            public_ip_address = realm_instance.public_ip_address
            await ctx.send(f"The {realm_name} realm is online. You may proceed with care to the realm. Stay safe. I'll be watching for your return.")
            await ctx.send(f"https://{public_ip_address}")
    else:
        await ctx.send(f"The gateway to {realm_name} is in a strange state. ({status}). Please try again in a moment or contact the realm's keeper.")
        
@bot.command()
async def stop(ctx, realm_name="foundry"):
    '''
    Stop the realm with the given name

    :param realm_name: Name of the realm to stop
    :type realm_name: str
    '''
    if realm_name in config["realms"]:
        realm_instance_id = config["realms"][realm_name]["instance_id"]
    else:
        await ctx.send("I do not know if that realm. Maybe its known by some other name?")
        return

    realm_instance = ec2.Instance(realm_instance_id)
    status = realm_instance.state["Name"]

    if status == "running":
        await ctx.send(f"I am stopping the {realm_name} realm. Make haste to exit and MIND THE GAP!")
        realm_instance.stop()
        operation_time = 0
        poll_frequency_ms = 5000 # 5 second polling ineterval
        operation_timeout = 300000
        while not realm_instance.state["Name"] == "stopped":
            await ctx.trigger_typing()
            time.sleep(poll_frequency_ms/1000)
            realm_instance.reload()
            operation_time += poll_frequency_ms
            if operation_time > operation_timeout:
                await ctx.send(f"There was some difficulty closing the gateway! Contact the keeper of the realm immediately as it may overload their budget!!!")
                break       
        
        if realm_instance.state["Name"] == "stopped":
            await ctx.send(f"The gateway to {realm_name} has been closed. I'm glad you've made it back with all your bits intact!")
    
    else:
        await ctx.send(f"The gateway to {realm_name} is in a strange state. ({status}). Please try again in a moment or contact the realm's keeper.")


bot.run(config.get("discord").get("client_auth_token"))