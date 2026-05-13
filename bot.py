from dotenv import load_dotenv
import discord
import os
from discordutils import *  # noqa: F403

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.all()
client = discord.Bot(intents=intents)

texture_id = 1498357668346069012

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if isinstance(message.channel, discord.Thread):
        thread: discord.Thread = message.channel
        if thread.parent.category_id == texture_id and verify_owner(message=message) and message.attachments: # type: ignore # noqa: F405
            action = decide_action(message) # noqa F405
            if action[0] == 0: # error
                await message.reply(f"{action[1]}")
            
            # confirm upload
            return
            
            
            if action[0] == 1:
                await message.reply("Processing texture.")
            if action[0] == 2:
                await message.reply("Processing model.")
                
    


@client.event
async def on_connect():
    if client.auto_sync_commands:
        await client.sync_commands()
    print(f"{client.user} synced.")


# @client.command(description="command description")
# async def command_name(ctx:discord.commands.context.ApplicationContext):
#    await ctx.respond(f"command reply", empheral=True)


@client.command(
    description="Sends the bot's latency."
)  # this decorator makes a slash command
async def ping(
    ctx: discord.ApplicationContext,
):  # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {client.latency}", ephemeral=True)


@client.slash_command(description="Creates a new model for an item")
@discord.option("name", str, description="Enter the name of the model you're adding.")
async def texture(ctx: discord.ApplicationContext, name: str):
    channel = ctx.channel
    if not channel:
        return
    if channel.category_id != texture_id: # type: ignore
        await ctx.respond("This command can only be used in texture channel.", ephemeral=True)
    thread: discord.Thread = await create_thread(ctx.author, channel, name)  # type: ignore  # noqa: F405
    if not thread:
        return

    await ctx.respond(f"Thread created at {thread.jump_url}", ephemeral=False)  # type: ignore
    
    # print the guide in the thread.


if TOKEN:
    client.run(TOKEN)
else:
    raise ReferenceError("TOKEN doesnt exist")
