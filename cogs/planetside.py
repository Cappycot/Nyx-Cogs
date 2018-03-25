from aiohttp import ClientSession
from discord import Color, Embed
from discord.ext import commands
from discord.ext.commands import BucketType
from json import loads

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
          19: "Jaeger"}
head_url = "http://census.daybreakgames.com/{}/get/ps2:v2/character/" \
           "?name.first_lower=".format(service_id)
tail_url = "&c:resolve=stat_history,online_status,outfit,world"


class PlanetSide:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(9, 60, BucketType.default)
    async def player(self, ctx, player):
        """Look up a player by name.

        No outfit tags.
        """
        message = await ctx.send("Looking up player {}...".format(player))
        url = "{}{}{}".format(head_url, player.lower(), tail_url)
        async with ctx.channel.typing(), ClientSession(
                loop=ctx.bot.loop) as session, session.get(url) as req:
            if req.status == 200:
                result = loads((await req.read()).decode("utf-8"))
                if result["returned"] == 0:
                    await ctx.send("Could not find player {}.".format(player))
                    await message.delete()
                    return
                character = result["character_list"][0]
                br = character["battle_rank"]["value"]
                f_id = int(character["faction_id"])
                link = "https://www.planetside2.com/players/#!/{}".format(
                    character["character_id"])
                online = "Online" if character[
                                         "online_status"] == "1" else "Offline"
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


def setup(bot):
    bot.add_cog(PlanetSide(bot))
