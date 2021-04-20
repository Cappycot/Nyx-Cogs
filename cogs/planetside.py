from aiohttp import ClientSession
from discord import Color, Embed
from discord.ext import commands
from discord.ext.commands import BucketType
from json import loads
from re import match

service_id = "s:example"  # Replace with an actual service ID.
# URL: https://www.planetside2.com/players/#!/
# Title: [TAG] Name
# Description: BR XXX
# Thumbnail: Faction Logo
# Color: Faction Color
# World: World
# Outfit: Outfit Name (if none, join one already!)
# Status: Online/Offline
# Creation: Date
# KDR: X.XX
colors = {1: Color.purple(), 2: Color.blue(), 3: Color.red()}
nc_logo = "https://www-cdn.planetside2.com/images/players/global/factions/" \
          "nc_70x70.png"
tr_logo = "https://www-cdn.planetside2.com/images/players/global/factions/" \
          "tr_56x68.png"
vs_logo = "https://www-cdn.planetside2.com/images/players/global/factions/" \
          "vs_70x70.png"
thumbnails = {1: vs_logo, 2: nc_logo, 3: tr_logo}
worlds = {1: "Connery", 10: "Miller", 13: "Cobalt", 17: "Emerald",
          19: "Jaeger", 25: "Briggs"}
head_url = "http://census.daybreakgames.com/{}/get/ps2:v2/".format(service_id)

player_url = "character?name.first_lower="
player_tail_url = "&c:resolve=stat_history,online_status,outfit,world"


class PlanetSide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def outfit(self, ctx, outfit):
        """Look up an outfit by full name.

        To look up by tag use the tag command.
        """
        pass

    @commands.command(rest_is_raw=True)
    @commands.cooldown(1, 3, BucketType.user)
    async def player(self, ctx, *, player):
        """Look up a player by name.

        No outfit tags.
        """
        player = player.strip()
        # All PS2 characters only have alphanumeric names.
        if match("^[0-9A-Za-z]*$", player) is None:
            await ctx.send("Please type a valid character name.")
            return
        message = await ctx.send("Looking up player {}...".format(player))
        url = "{}{}{}{}".format(head_url, player_url, player.lower(),
                                player_tail_url)
        async with ctx.channel.typing(), ClientSession(
                loop=ctx.bot.loop) as session, session.get(url) as req:
            if req.status == 200:
                result = loads((await req.read()).decode("utf-8"))
                if result["returned"] == 0:
                    await ctx.send("Could not find player {}.".format(player))
                    await message.delete()
                    return
                elif result["returned"] > 1:
                    await ctx.send(
                        "Returned multiple results for player {}.".format(
                            player))
                    await message.delete()
                    return
                character = result["character_list"][0]
                br = character["battle_rank"]["value"]
                f_id = int(character["faction_id"])
                link = "https://www.planetside2.com/players/#!/{}".format(
                    character["character_id"])
                online = "Offline" if character[
                                          "online_status"] == "0" else "Online"
                outfit = None
                tag = ""
                w_id = int(character["world_id"])
                if "outfit" in character:
                    outfit = character["outfit"]["name"]
                    tag = "[{}] ".format(character["outfit"]["alias"])
                name = "{}{}".format(tag, character["name"]["first"])
                embed = Embed(title=name, description="BR {}".format(br),
                              url=link, colour=colors[f_id])
                embed.set_thumbnail(url=thumbnails[f_id])
                embed.add_field(name="Server",
                                value=worlds.get(w_id, "Unknown"))
                if outfit is not None:
                    embed.add_field(name="Outfit", value=outfit)
                embed.add_field(name="Status", value=online)
                deaths = 1
                kills = 0
                for entry in character["stats"]["stat_history"]:
                    if entry["stat_name"] == "deaths":
                        deaths = int(entry["all_time"])
                    elif entry["stat_name"] == "kills":
                        kills = int(entry["all_time"])
                kdr = kills / deaths
                embed.add_field(name="K/D Ratio", value="%.2f" % kdr)
                await ctx.send(embed=embed)
            else:
                await ctx.send(
                    "An error occured. ({})".format(str(req.status)))
        await message.delete()

    @commands.command()
    @commands.cooldown(1, 3, BucketType.user)
    async def tag(self, ctx, outfit):
        """Look up an outfit by its tag.

        To look up by name use the outfit command.
        """
        pass


def setup(bot):
    bot.add_cog(PlanetSide(bot))
