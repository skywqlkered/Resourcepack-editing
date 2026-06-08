from dotenv import load_dotenv
import discord
from discord import app_commands
import os
from utils.discordutils import *  # noqa: F403
from utils.classes.confirmview import ConfirmView
from utils.mcitems import mc_items

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
path_str = os.getenv("PATH")

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
        if thread.parent.category_id == texture_id and verify_owner(channel=message.channel, author=message.author) and message.attachments:  # type: ignore # noqa: F405
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


@tree.command(name="create-texture",description="Creates a model for an item")
@app_commands.describe(name="The name of the model you're adding.")
async def texture(interaction: discord.Interaction, name: str):
    channel = interaction.channel
    if not channel:
        return
    if channel.category_id != texture_id and not isinstance(channel, discord.Thread):  # type: ignore
        await interaction.response.send_message(
            "This command can only be used in the texture channel.", ephemeral=True
        )
        return
    thread: discord.Thread = await create_thread(interaction.user, channel, name)  # type: ignore  # noqa: F405
    if not thread:
        return

    await interaction.response.send_message(f"Thread created at {thread.jump_url}", ephemeral=False)  # type: ignore

    # print the guide in the thread.

@tree.command(name="select-item",description="Select a Minecraft item for your model.")
@app_commands.describe(mcitem="The Minecraft item")
async def select_item(interaction: discord.Interaction, mcitem: str):
    if verify_owner(interaction.channel, author=interaction.user) and isinstance(interaction.channel, discord.Thread): # noqa: F405
        if mcitem in mc_items:
            update_thread_content(interaction.channel.id, mcitem=mcitem)# noqa: F405
            await interaction.response.send_message(f"You've selected {mcitem}")            
        else: 
            await interaction.response.send_message(f"Item {mcitem} does not exist, please use /get-minecraft-items to get the full list.")
    else: 
        await interaction.response.send_message("This isn't your thread.", ephemeral=True)

@tree.command(name="complete-texture",description="Completes the model creation")
async def complete_texture(interaction: discord.Interaction):
    if verify_owner(interaction.channel, author=interaction.user) and isinstance(interaction.channel, discord.Thread):# noqa: F405
        update_thread_content(interaction.channel.id, owner=interaction.user.display_name)# noqa: F405
        result = verify_uploads(interaction.channel.id) # noqa: F405
        if isinstance(result, bool): 
            treshold = create_texture(interaction.channel.id)# noqa: F405
            await interaction.response.send_message(f"Your model is using CustomModelData: {treshold}")
        
        elif isinstance(result, list):
            await interaction.response.send_message(f"You havent uploaded: {" ".join(result)}")
            
        else:
            await interaction.response.send_message("Something went very wrong, ask sky")
    else:
        await interaction.response.send_message("This isn't your thread.", ephemeral=True)

@select_item.autocomplete("mcitem")
async def mcitems_autocomplete(interaction: discord.Interaction, mcitem: str):
    mcitems = [
        "shears", "cooked_beef", "golden_carrot", "trident",
        "diamond_axe", "diamond_hoe", "diamond_pickaxe",
        "diamond_shovel", "diamond_sword", "mace",
        "netherite_axe", "netherite_hoe", "netherite_pickaxe",
        "netherite_shovel", "netherite_sword"
    ]

    return [
        app_commands.Choice(name=item, value=item)
        for item in mcitems
        if mcitem.lower() in item.lower()
    ]

@tree.command(name="get-minecraft-items",description="Gives you the Minecraft items.")
async def get_items(interaction: discord.Interaction):
    await interaction.response.send_message("All Minecraft items of this version can be found here: <https://github.com/skywqlkered/Resourcepack-editing/blob/main/mcitems.txt>", ephemeral=True)
    
# @tree.command(name="test_buttons", description="Test action rows")
# async def test_buttons(interaction: discord.Interaction):
#     # This sends the message with the ActionRow containing the buttons
#     view = ConfirmView(action=1, message=interaction.message)
#     await interaction.response.send_message("Choose an action:", view=view)

if TOKEN:
    client.run(TOKEN)
else:
    raise ReferenceError("TOKEN doesnt exist")
