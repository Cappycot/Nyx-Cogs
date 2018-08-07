from re import match as rematch

import nyx.nyxcommands as nyxcommands
from discord import CategoryChannel, Embed, Member, TextChannel
from discord.ext import commands
from discord.utils import get
from nyx.nyxutils import reply


class Diagnostics:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command(aliases=["bigmoji"])
    async def emoji(self, ctx, emoji):
        """Gives as much information on a custom emoji as possible."""
        # Use Rapptz's EmojiConverter code for first leg.
        match = rematch(r'([0-9]{15,21})$', emoji) or rematch(
            r'<a?:[a-zA-Z0-9_]+:([0-9]+)>$', emoji)
        result = None
        emoji_guild = "Unknown"
        emoji_id = None
        bot = ctx.bot
        guild = ctx.guild

        if match is None:
            # Try to get the emoji by name. Try local guild first.
            if guild:
                result = get(guild.emojis, name=emoji)
            if result is None:
                result = get(bot.emojis, name=emoji)
        else:
            for g in match.groups():
                print(g)
            emoji_id = int(match.group(1))
            # Try to look up emoji by id.
            if guild:
                result = get(guild.emojis, id=emoji_id)
            if result is None:
                result = get(bot.emojis, id=emoji_id)

        # We should hotlink at least the ID and URL of all emojis.
        if result is not None:
            emoji_guild = result.guild
            emoji_id = result.id
            emoji_name = result.name
            emoji_type = "gif" if result.animated else "png"
        elif emoji_id is not None:
            # Should work because Discord disallows ":" in emoji names.
            emoji_name = emoji.split(":", 1)[1].split(":")[0]
            emoji_type = "gif" if emoji.startswith("<a:") else "png"
        else:
            await reply(ctx, "I couldn't find such a custom emoji...")
            return
        url = "https://cdn.discordapp.com/emojis/{}.{}?v=1".format(emoji_id,
                                                                   emoji_type)
        embed = Embed(title=emoji_name, url=url)
        embed.add_field(name="Guild:", value=emoji_guild)
        embed.add_field(name="ID:", value=str(emoji_id))
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @nyxcommands.has_privilege_or_permissions(privilege=-1, manage_guild=True)
    async def permissions(self, ctx, member: Member = None):
        """Runs permission diagnostics on the guild this command is called in.
        """
        if member is None:
            member = ctx.guild.get_member(self.nyx.user.id)
        message_block = ["```Markdown", "\n", ctx.guild.name, "\n",
                         "=" * (len(ctx.guild.name))]
        # Length of beginning and end of code block, plus two newlines, plus
        # the guild name repeated twice.
        message_length = 16 + len(ctx.guild.name) * 2
        perms = member.guild_permissions
        # List Roles
        index = len(member.roles) - 1
        for role in ctx.guild.role_hierarchy[:-1]:
            role_name = str(role)
            if index > 0 and member.roles[index] == role:
                role_name = "\n**{}**".format(role_name)
                index -= 1
            else:
                role_name = "\n- {}  ".format(role_name)
            if message_length + len(role_name) >= 1903:
                message_block.append("```")
                await ctx.author.send("".join(message_block))
                message_block = ["```Markdown"]
                message_length = 14
            message_block.append(role_name)
            message_length += len(role_name)
        # Get general guild permissions.
        message_block.append("\n\nPermissions\n===========")
        message_length += 25
        if perms.administrator:
            message_block.append("\nAdministrator")
            message_length += 14
        else:
            if perms.manage_guild:
                message_block.append("\nManage Server")
                message_length += 14
            if perms.kick_members:
                message_block.append("\nKick Members")
                message_length += 13
            if perms.ban_members:
                message_block.append("\nBan Members")
                message_length += 12
            if perms.change_nickname:
                message_block.append("\nChange Nickname")
                message_length += 16
            if perms.manage_nicknames:
                message_block.append("\nManage Nicknames")
                message_length += 17
        if perms.administrator:
            message_block.append("\n\nChannels\n========")
            message_length += 19
        # List channels.
        for channel in ctx.guild.channels:
            if isinstance(channel, CategoryChannel):
                continue
            if isinstance(channel, TextChannel):
                channel_type = "NSFW" if channel.nsfw else "Text"
            else:
                channel_type = "Voice"

            channel_block = "\n{} ({})".format(channel.name, channel_type)
            if not perms.administrator:
                channel_block = "\n{}".format(channel_block)
                channel_block = [channel_block, "\n",
                                 "=" * (len(channel_block) - 2)]
                perms = member.permissions_in(channel)
                # Get channel permissions.
                if perms.create_instant_invite:
                    channel_block.append("\nCreate Instant Invite")
                if perms.manage_channels:
                    channel_block.append("\nManage Channel")
                if perms.manage_roles:
                    channel_block.append("\nManage Permissions")
                if perms.manage_webhooks:
                    channel_block.append("\nManage Webhooks")
                # Type-specific permissions for text and voice.
                if isinstance(channel, TextChannel):
                    if not perms.read_messages:
                        channel_block.append("\nCannot Access")
                    else:
                        if perms.send_messages:
                            channel_block.append("\nSend Messages")
                        if perms.send_tts_messages:
                            channel_block.append("\nSend TTS Messages")
                        if perms.manage_messages:
                            channel_block.append("\nManage Messages")
                        if perms.embed_links:
                            channel_block.append("\nEmbed Links")
                        if perms.attach_files:
                            channel_block.append("\nAttach Files")
                        if perms.read_message_history:
                            channel_block.append("\nRead Message History")
                        if perms.mention_everyone:
                            channel_block.append("\nMention Everyone")
                        if perms.external_emojis:
                            channel_block.append("\nUse External Emojis")
                        if perms.add_reactions:
                            channel_block.append("\nAdd Reactions")
                else:  # if VoiceChannel
                    no_access = True
                    if perms.connect:
                        channel_block.append("\nConnect")
                        no_access = False
                    if perms.speak:
                        channel_block.append("\nSpeak")
                        no_access = False
                    if perms.mute_members:
                        channel_block.append("\nMute Members")
                        no_access = False
                    if perms.deafen_members:
                        channel_block.append("\nDeafen Members")
                        no_access = False
                    if perms.move_members:
                        channel_block.append("\nMove Members")
                        no_access = False
                    # Use Voice Activity is irrelevant for bots.
                    if no_access:
                        channel_block.append("\nCannot Access")
            channel_block = "".join(channel_block)
            if len(channel_block) + message_length >= 2000:
                message_block.append("```")
                await ctx.author.send("".join(message_block))
                message_block = ["```Markdown"]
                message_length = 14
            message_block.append(channel_block)
            message_length += len(channel_block)
        message_block.append("```")
        await ctx.author.send("".join(message_block))

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit: int):
        check = lambda a: a.id != ctx.message.id
        deleted = await ctx.channel.purge(limit=limit + 1, check=check)
        deleted = len(deleted)
        res = "Deleted {} message{}.".format(deleted,
                                             "" if deleted == 1 else "s")
        await ctx.send(res)


def setup(nyx):
    nyx.add_cog(Diagnostics(nyx))
