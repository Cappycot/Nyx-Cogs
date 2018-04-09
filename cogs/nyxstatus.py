from discord import Activity, ActivityType, Status
from discord.enums import try_enum
from discord.ext import commands

import nyx.nyxcommands as nyxcommands
from nyx.nyxcommands import ModuleExclusiveCommand
from nyx.nyxutils import respond

green = ["g", "green", "online"]
yellow = ["idle", "y", "yellow"]
red = ["busy", "dnd", "r", "red"]
gray = ["gray", "grey", "off", "offline"]


# 0: Playing
# 1: Streaming
# 2: Listening
# 3: Watching

class Presence:
    def __init__(self, nyx):
        self.nyx = nyx
        self.status = Status.online
        self.game = None
        self.url = None

    async def update_status(self, ctx=None):
        """Calls to update the displayed presence and confirms this if
        needed.
        """
        if self.game is not None:
            self.game.url = self.url
            if ctx is not None:
                await respond(ctx, "I changed my status to {}...".format(
                    self.game.name))
        elif ctx is not None:
            await respond(ctx, "I changed my status to nothing.")
        await self.nyx.change_presence(activity=self.game, status=self.status)

    async def change_status(self, ctx, action, name):
        """Modifies the parameters of the Discord Game to display."""
        # print(action)
        # print(name)
        if len(name) > 0:
            mention = self.nyx.user.mention
            if ctx.guild is not None:
                mention = ctx.guild.get_member(self.nyx.user.id).mention
            name = name.replace(mention, "@{}".format(self.nyx.user.name))
        if self.game is None:
            self.game = Activity(name=name, type=action)
        else:
            self.game.name = name
            self.game.type = try_enum(ActivityType, action)
        await self.update_status(ctx)

    @commands.command(cls=ModuleExclusiveCommand)
    @nyxcommands.has_privilege(privilege=-1)
    async def clear(self, ctx):
        self.game = None
        await self.update_status(ctx)

    @commands.command(cls=ModuleExclusiveCommand)
    @nyxcommands.has_privilege(privilege=-1)
    async def color(self, ctx, color):
        """Changes the status color to the specified status/color."""
        if any(color == a for a in green):
            self.status = Status.online
        elif any(color == a for a in yellow):
            self.status = Status.idle
        elif any(color == a for a in red):
            self.status = Status.dnd
        elif any(color == a for a in gray):
            self.status = Status.offline
        else:
            self.status = None
        await self.update_status()
        await respond(ctx,
                      "I changed my status to {}.".format(self.status))

    @commands.command(cls=ModuleExclusiveCommand)
    @nyxcommands.has_privilege(privilege=-1)
    async def playing(self, ctx, *, words):
        """Changes the status to "Playing" followed by a string."""
        await self.change_status(ctx, 0, words)

    @commands.command(cls=ModuleExclusiveCommand)
    @nyxcommands.has_privilege(privilege=-1)
    async def streaming(self, ctx, *, words):
        """Changes the status to "Streaming" followed by a string."""
        await self.change_status(ctx, 1, words)

    @commands.command(cls=ModuleExclusiveCommand, aliases=["listeningto"])
    @nyxcommands.has_privilege(privilege=-1)
    async def listening(self, ctx, *, words):
        """Changes the status to "Listening to" followed by a string."""
        await self.change_status(ctx, 2, words)

    @commands.command(cls=ModuleExclusiveCommand)
    @nyxcommands.has_privilege(privilege=-1)
    async def watching(self, ctx, *, words):
        """Changes the status to "Watching" followed by a string."""
        await self.change_status(ctx, 3, words)

    @commands.command(aliases=["url"], cls=ModuleExclusiveCommand)
    @nyxcommands.has_privilege(privilege=-1)
    async def streamurl(self, ctx, url):
        """Sets the URL for streaming status."""
        self.url = url
        await self.update_status(ctx)

    async def on_ready(self):
        await self.update_status()


def setup(nyx):
    ns = Presence(nyx)
    nyx.add_cog(ns)
    nyx.add_listener(ns.on_ready)
