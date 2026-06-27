import discord
from ..threadutils import download_texture, download_model, download_animation

class ConfirmView(discord.ui.View):
    def __init__(self, action, message):
        super().__init__(timeout=60)
        self.action = action
        self.message:discord.Message = message
        
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.message.author:
            return await interaction.response.send_message("This isn't your upload.", ephemeral=True)
        
        if self.action[0] == 1:
            try:
                # You can use interaction.followup to send new messages
                await download_texture(message=self.message)
                await interaction.response.edit_message(content="Processed texture", view=None)
            except discord.errors.InteractionResponded:
                pass
            
        elif self.action[0] == 2:
            await download_model(message=self.message)
            await interaction.response.edit_message(content="Processed model", view=None)
            
        elif self.action[0] == 3:
            await download_animation(message=self.message)
            await interaction.response.edit_message(content="Processed animation", view=None)
        
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.message.author:
            return await interaction.response.send_message("This isn't your thread.", ephemeral=True)
        
        await interaction.response.edit_message(content="Upload cancelled.", view=None)
        self.stop()