import discord
from discord.ext import commands
import asyncio

from lib import utils

MOD_ROLES = ["Admin", "Head Mod"]

class ShowtimeCog(commands.Cog):
    """
    Showcase commands and listeners
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="channel")
    @commands.has_any_role(*MOD_ROLES)
    async def channels(self, ctx, *args, **kwargs):

        async def listChannels(ctx):
            channels = utils.getChannel()
            if(channels):
                message = ""
                for channel in channels:
                    message += f"{channel['reaction']} - <#{channel['channel']}>\n"
            else:
                message = "No showcase channels are set. Please see the `channel` command's help to see how to set a showcase channel."
            await ctx.send(embed=discord.Embed(
                title="Showcase Channels",
                description=message
            ))

        # No arguments
        if(len(args) < 1):
            await listChannels(ctx)
        else:
            for arg in args:
                if(arg == "list" or arg == "ls" or arg == "l"):
                    await listChannels(ctx)
                elif(arg == "set"):
                    if(len(args) < 3):
                        await ctx.send("Too few arguments, please see the `help` command for more information.")
                        return
                    
                    # Check whether valid channel
                    try:
                        channelID = int(args[2][2:-1])
                    except ValueError:
                        await ctx.send("Not a valid channel 😢")
                        return
                    if(self.bot.get_channel(channelID) == None):
                        await ctx.send("Not a valid channel 😟")
                        return
                    
                    # Check whether valid reaction
                    reaction = args[1]
                    try:
                        await ctx.message.add_reaction(reaction)
                        await ctx.message.remove_reaction(reaction, self.bot.user)
                    except discord.NotFound:
                        await ctx.send("Not a valid reaction 😟")
                        return
                    except discord.HTTPException:
                        await ctx.send("Not a valid reaction 😟")
                        return
                    
                    utils.addChannel(channelID, reaction)
                    await ctx.send(f"New showcase channel added! {reaction} - <#{channelID}>")
                else:
                    await ctx.send("Unknown argument. Please see the `help` command for more information.")

                                


    @commands.Cog.listener()
    async def on_message(self, ctx):
        config = utils.get_config()
        requestChID = config["discord"]["showcase"]["request-channel-id"]
        approvalChID = config["discord"]["showcase"]["approval-channel-id"]

        if(ctx.author != self.bot.user):
            if(ctx.channel.id == requestChID):
                atts = []
                attStr = ""
                if(ctx.attachments):
                    for att in ctx.attachments:
                        if(att.content_type.split('/')[0] not in ['image', 'video']):
                            message = await ctx.channel.send("Only images and video are allowed.")
                            return
                        attStr += f"**[{att.filename}]({att.url})** {att.size} {att.content_type}\n"
                        atts.append({
                            "id": att.id,
                            "filename": att.filename,
                            "size": att.size,
                            "url": att.url
                        })
                else:
                    attStr = "None"

                embed = discord.Embed(
                    title="A user has request to publish a showcase",
                    colour=discord.Color.orange()
                ).add_field(
                    name="Content",
                    value=ctx.content if ctx.content else "*Not Given*",
                    inline=False
                ).add_field(
                    name="Attachments",
                    value=attStr,
                    inline=False
                ).add_field(
                    name="Author",
                    value=ctx.author.mention,
                    inline=False
                ).set_thumbnail(
                    url= atts[0]["url"] if (len(atts) > 0) else ""
                )
                
                approvalMessage = await self.bot.get_channel(approvalChID).send(embed=embed)

                utils.addShowcase(
                    originalMsgID=ctx.id,
                    approvalMsgID=approvalMessage.id,
                    content=ctx.content if ctx.content else "",
                    attachments=atts,
                    author=ctx.author.id
                )

                for channel in utils.getChannel():
                    await approvalMessage.add_reaction(channel["reaction"])
    
    @commands.Cog.listener()
    @commands.has_any_role(*MOD_ROLES)
    async def on_raw_reaction_add(self, payload):
        if(payload.user_id != self.bot.user.id):
            config = utils.get_config()
            approvalChID = config["discord"]["showcase"]["approval-channel-id"]
            if (payload.channel_id == approvalChID):

                showcase = utils.getShowcase(payload.message_id)
                if(payload.emoji.is_custom_emoji()):
                    reaction = "<:" + payload.emoji.name + ":" + str(payload.emoji.id) + ">"
                else:
                    reaction = payload.emoji.name
                
                channel = utils.getChannel(reaction=reaction)

                if(channel):
                    channel = channel["channel"]
                else:
                    await self.bot.get_channel(payload.channel_id).send("Error in reaction-channel relation.")
                    return

                attStr = ""
                for att in showcase["attachments"]:
                    attStr += att["url"] + "\n"

                showcase_str = "<@{0}>\n\n{1}\n\n{2}".format(showcase["author"], showcase["content"], attStr)

                await self.bot.get_channel(payload.channel_id).send(f"Showcase sent to <#{channel}>")

                await self.bot.get_channel(channel).send(showcase_str)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, (commands.MissingAnyRole, commands.MissingRole)):
            await ctx.send("Sorry, you don't have the necessary permissions to run this command.")

def setup(bot):
    bot.add_cog(ShowtimeCog(bot))