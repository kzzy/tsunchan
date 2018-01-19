from discord.ext import commands

class Voice:
    def __init__(self, bot):
        self.bot = bot
        self.bot_voice_client = None

    @commands.group(pass_context=True, aliases=['v'])
    async def voice(self):
        return

    @commands.group(pass_context=True, aliases=['j'])
    async def join(self, ctx):
        """ Joins the author's voice channel """
        member = ctx.message.author
        channel = member.voice_channel
        # Empty voice
        if channel is None:
            print("None")
            return
        # Initiate voice client for bot
        self.bot_voice_client = await self.bot.join_voice_channel(channel)

    @commands.group(pass_context=True, aliases=['uj'])
    async def leave(self, ctx):
        """ Leaves any voice channel"""
        # Not in voice
        if self.bot_voice_client.is_connected() is None:
            return

        try:
            await self.bot_voice_client.disconnect()
        except:
            pass

def setup(bot):
    bot.add_cog(Voice(bot))