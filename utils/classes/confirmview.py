import discord

class ConfirmView(discord.ui.View):
    def __init__(self, action, message):
        super().__init__(timeout=60)
        self.action = action
        self.message = message
        
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.message.author:
            return await interaction.response.send_message("This isn't your upload.", ephemeral=True)
        
        if self.action[0] == 1:
            # You can use interaction.followup to send new messages
            await interaction.response.edit_message(content="Processing texture...", view=None)
            # Run your texture processing code here
            
        elif self.action[0] == 2:
            await interaction.response.edit_message(content="Processing model...", view=None)
            # Run your model processing code here
        
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.message.author:
            return await interaction.response.send_message("This isn't your upload.", ephemeral=True)
        
        await interaction.response.edit_message(content="Upload cancelled.", view=None)
        self.stop()