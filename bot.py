from dotenv import load_dotenv
import discord
from discord import app_commands
import os
from utils.threadutils import *  # noqa: F403
from utils.classes.confirmview import ConfirmView
from utils.mcitems import mc_items
from utils.gitutils import upload_files
from utils.modelutils import create_textures_folder

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
path_str = os.getenv("PATH")

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
texture_cat_id = (
    1498357668346069012  # ethis: 1498357668346069012 # bts3 1518943883252338708
)
post_channel_id = (
    1498358237932556479  # ethis: 1498358237932556479 # bts3 1518944668971302952
)

max_model_uploads_per_week = 2


@client.event
async def on_ready():
    ethis_id = 925805443887022121
    test3_id = 987779478413525023
    current_id = ethis_id
    tree.copy_global_to(guild=discord.Object(id=current_id))
    synced_commands = await tree.sync(guild=discord.Object(id=current_id))  # ethis
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
        if thread.parent.category_id == texture_cat_id and verify_owner(channel=message.channel, author=message.author) and message.attachments:  # type: ignore # noqa: F405
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


@tree.command(name="create-texture", description="Creates a model for an item")
@app_commands.describe(name="The name of the model you're adding.")
async def texture(interaction: discord.Interaction, name: str):
    channel = interaction.channel
    if not channel:
        await interaction.response.send_message(
            "You somehow used this command in something that is not a channel, ask sky",
            ephemeral=False,
        )
    if channel.category_id != texture_cat_id and not isinstance(channel, discord.Thread):  # type: ignore
        await interaction.response.send_message(
            "This command can only be used in the texture channel.", ephemeral=True
        )
        return
    if not isAllowedToUpload(  # noqa: F405
        interaction, max_upload_count=max_model_uploads_per_week
    ):
        await interaction.response.send_message(
            "You have reached your weekly upload limit, comeback next week or subscribe to Ethis+.",
            ephemeral=True,
        )
        return

    thread: discord.Thread = await create_thread(interaction.user, channel, name)  # type: ignore  # noqa: F405
    update_thread_content(
        threadid=thread.id, isPainting=False, thread_name=thread.name
    )  # noqa: F405
    create_textures_folder(thread_name=thread.name)
    if not thread:
        await interaction.response.send_message(
            "Somehow a thread wasn't created, ask sky", ephemeral=False
        )

    await interaction.response.send_message(f"Thread created at {thread.jump_url}", ephemeral=False)  # type: ignore


@tree.command(name="create-painting", description="Creates a painting from a png")
@app_commands.describe(
    name="The name of the painting you're adding. Please make your name only has characters from [a-z0-9/._-]."
)
async def painting(interaction: discord.Interaction, name: str):
    channel = interaction.channel
    if not channel:
        await interaction.response.send_message(
            "You somehow used this command in something that is not a channel, ask sky",
            ephemeral=False,
        )
    if channel.category_id != texture_cat_id and not isinstance(channel, discord.Thread):  # type: ignore
        await interaction.response.send_message(
            "This command can only be used in the texture channel.", ephemeral=True
        )
        return
    if not isAllowedToUpload(
        interaction, max_upload_count=max_model_uploads_per_week
    ):  # noqa: F405
        await interaction.response.send_message(
            "You have reached your weekly upload limit, comeback next week or subscribe to Ethis+.",
            ephemeral=True,
        )
        return
    thread: discord.Thread = await create_thread(interaction.user, channel, name)  # type: ignore  # noqa: F405
    if not handle_model_name(thread.name):
        await interaction.response.send_message(
            "Why couldnt you just use a model name that Minecraft can handle, why do you have to be so difficult? Ask sky",
            ephemeral=False,
        )
    update_thread_content(
        threadid=thread.id,
        isPainting=True,
        mcitem="paper",
        model=thread.name + ".json",
        thread_name="paintings",
    )  # noqa: F405

    if not thread:
        await interaction.response.send_message(
            "Somehow a thread wasn't created, ask sky", ephemeral=False
        )

    await interaction.response.send_message(f"Thread created at {thread.jump_url}", ephemeral=False)  # type: ignore

    # print the guide in the thread.


@tree.command(name="select-item", description="Select a Minecraft item for your model.")
@app_commands.describe(mcitem="The Minecraft item")
async def select_item(interaction: discord.Interaction, mcitem: str):
    await verify_thread(interaction=interaction)  # noqa: F405
    assert isinstance(interaction.channel, discord.Thread)

    if mcitem in mc_items:
        update_thread_content(interaction.channel.id, mcitem=mcitem)  # noqa: F405
        await interaction.response.send_message(f"You've selected {mcitem}")
    else:
        await interaction.response.send_message(
            f"Item {mcitem} does not exist, please use /get-minecraft-items to get the full list."
        )


@tree.command(name="complete-texture", description="Completes the model creation")
async def complete_texture(interaction: discord.Interaction):
    await verify_thread(interaction=interaction)  # noqa: F405
    assert isinstance(interaction.channel, discord.Thread)

    update_thread_content(  # noqa: F405
        interaction.channel.id, owner=interaction.user.display_name
    )  # noqa: F405
    result = verify_uploads(interaction.channel.id)  # noqa: F405
    if isinstance(result, bool):
        treshold = create_texture(interaction.channel.id)  # noqa: F405
        await interaction.response.send_message(
            f"Your model is using CustomModelData: {treshold}"
        )
        upload_files()

        await close_thread(
            thread=interaction.channel, post_channel_id=post_channel_id
        )  # noqa: F405

    elif isinstance(result, list):
        await interaction.response.send_message(
            f"You havent uploaded: {" ".join(result)}"
        )

    else:
        await interaction.response.send_message(
            "Something went very wrong, ask sky", ephemeral=False
        )


@tree.command(name="delete-thread", description="Completes the model creation")
@app_commands.default_permissions(administrator=True)
async def delete_discord_thread(interaction: discord.Interaction):
    if isinstance(interaction.channel, discord.Thread):
        message_id = await delete_thread(thread=interaction.channel)
        assert isinstance(message_id, int)
        texture_post_channel: discord.TextChannel = interaction.guild.fetch_channel(post_channel_id)  # type: ignore
        del_message: discord.Message = texture_post_channel.fetch_message(message_id) # type:ignore
        await del_message.delete()
    return


@select_item.autocomplete("mcitem")
async def mcitems_autocomplete(interaction: discord.Interaction, mcitem: str):
    mcitems = [
        "shears",
        "cooked_beef",
        "golden_carrot",
        "trident",
        "diamond_axe",
        "diamond_hoe",
        "diamond_pickaxe",
        "diamond_shovel",
        "diamond_sword",
        "mace",
        "netherite_axe",
        "netherite_hoe",
        "netherite_pickaxe",
        "netherite_shovel",
        "netherite_sword",
    ]

    return [
        app_commands.Choice(name=item, value=item)
        for item in mcitems
        if mcitem.lower() in item.lower()
    ]


@tree.command(name="get-minecraft-items", description="Gives you the Minecraft items.")
async def get_items(interaction: discord.Interaction):
    await interaction.response.send_message(
        "All Minecraft items of this version can be found here: <https://github.com/skywqlkered/Resourcepack-editing/blob/main/mcitems.txt>",
        ephemeral=True,
    )


# @tree.command(name="test_buttons", description="Test action rows")
# async def test_buttons(interaction: discord.Interaction):
#     # This sends the message with the ActionRow containing the buttons
#     view = ConfirmView(action=1, message=interaction.message)
#     await interaction.response.send_message("Choose an action:", view=view)

if TOKEN:
    client.run(TOKEN)
else:
    raise ReferenceError("TOKEN doesnt exist")
