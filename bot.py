from dotenv import load_dotenv
import discord
from discord import app_commands
import os
from utils.discordutils import *  # noqa: F403
from utils.classes.confirmview import ConfirmView

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
texture_id = 1498357668346069012

@client.event
async def on_ready():
    tree.copy_global_to(guild=discord.Object(id=925805443887022121))
    synced_commands = await tree.sync(
        guild=discord.Object(id=925805443887022121)
    )  # ethis
    print(
        f"I have logged in as {client.user} and synced {len(synced_commands)} commands."
    )


confirm_txt = (
    "Please confirm the upload of this file by clicking the corrosponding reaction."
)


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if isinstance(message.channel, discord.Thread):
        thread: discord.Thread = message.channel
        if thread.parent.category_id == texture_id and verify_owner(message=message) and message.attachments:  # type: ignore # noqa: F405
            action = decide_action(message)  # noqa F405
            if action[0] == 0:  # error
                await message.reply(f"{action[1]}", silent=True)

            else: 
                view = ConfirmView(action=action, message=message)
                await message.reply("Please confirm the upload.", view=view)

    


@tree.command(
    description="Sends the bot's latency."
)  # this decorator makes a slash command
async def ping(
    interaction: discord.Interaction,
):  # a slash command will be created with the name "ping"
    await interaction.response.send_message(
        f"Pong! Latency is {client.latency}", ephemeral=True
    )


@tree.command(description="Creates a model for an item")
@app_commands.describe(name="The name of the model you're adding.")
async def texture(interaction: discord.Interaction, name: str):
    channel = interaction.channel
    if not channel:
        return
    if channel.category_id != texture_id:  # type: ignore
        await interaction.response.send_message(
            "This command can only be used in texture channel.", ephemeral=True
        )
        return
    thread: discord.Thread = await create_thread(interaction.user, channel, name)  # type: ignore  # noqa: F405
    if not thread:
        return

    await interaction.response.send_message(f"Thread created at {thread.jump_url}", ephemeral=False)  # type: ignore

    # print the guide in the thread.


@tree.command(name="test_buttons", description="Test action rows")
async def test_buttons(interaction: discord.Interaction):
    # This sends the message with the ActionRow containing the buttons
    view = ConfirmView(action=1, message=interaction.message)
    await interaction.response.send_message("Choose an action:", view=view)

if TOKEN:
    client.run(TOKEN)
else:
    raise ReferenceError("TOKEN doesnt exist")
