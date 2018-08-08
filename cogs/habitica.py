from asyncio import sleep
from configparser import ConfigParser
from datetime import datetime
from json import loads
from os.path import join

from aiohttp import ClientSession
from discord import Color, Embed
from discord.ext import commands

folder = join("data", "habitica")
config = ConfigParser()
api_url = "https://habitica.com/api/v3"
group_url = "https://habitica.com/groups/guild/{}"
party_url = "https://habitica.com/party"
tavern_url = "https://habitica.com/groups/tavern"
contrib_colors = [Color(5130839), Color(12855408), Color(11539733),
                  Color(14093844), Color(12733696), Color(10380559),
                  Color(2851683), Color(1474183), Color(2588331),
                  Color(6370228), Color(1710109)]


class ChatTracker:
    def __init__(self, name):
        self.channels = {}  # {channel ID: boolean all chats}
        self.name = name  # Name of the party/guild/tavern
        self.last_chat = None


class Habitica:
    def __init__(self, bot):
        self.bot = bot
        config.read(join(folder, "auth.nyx"))
        self.headers = {"x-api-user": config.get("Settings", "uid"),
                        "x-api-key": config.get("Settings", "token")}
        self.chats = {}  # {gid:ChatTracker}

    async def get_chats(self, gid):
        data = None
        url = "/".join([api_url, "groups", gid, "chat"])
        async with ClientSession(loop=self.bot.loop) as session, session.get(
                url, headers=self.headers) as req:
            if req.status == 200:
                data = loads((await req.read()).decode("utf-8"))
        return data

    @commands.command()
    async def addchat(self, ctx, gid):
        gid = gid.lower()
        # Need to run get to get group information as needed.
        if gid == "tavern":
            gid = "habitrpg"

    async def clock(self):
        await self.bot.wait_until_ready()
        last_minute = -1
        sent = 0
        while sent < 20:
            await sleep(1)
            d_time = datetime.now()
            if d_time.minute != last_minute:
                last_minute = d_time.minute
                final_chats = self.chats.copy()
                for gid in final_chats:
                    chats = await self.get_chats(gid)
                    if chats is not None and "data" in chats:
                        messages = chats["data"]
                        tracker = final_chats[gid]
                        if tracker.last_chat is not None:
                            to_send = []
                            for message in messages:
                                if message["id"] == tracker.last_chat:
                                    break
                                to_send.append(message)
                            for send in reversed(to_send):
                                text = send["text"].replace("` `", "\n").strip(
                                    "`")
                                timestamp = datetime.utcfromtimestamp(
                                    send["timestamp"] / 1000)
                                if gid == "habitrpg":
                                    url = tavern_url
                                elif gid == "party":
                                    url = party_url
                                else:
                                    url = group_url.format(gid)
                                embed = Embed(title=tracker.name,
                                              description=text,
                                              timestamp=timestamp, url=url)
                                if "user" in send:
                                    embed.set_author(name=send["user"])
                                    contrib = 0
                                    if "level" in send["contributor"]:
                                        contrib = send["contributor"]["level"]
                                    embed.colour = contrib_colors[contrib]
                                else:
                                    embed.colour = Color(0)
                                for channel in tracker.channels:
                                    dest = self.bot.get_channel(channel)
                                    await dest.send(embed=embed)
                                    sent += 1
                        tracker.last_chat = messages[0]["id"]
                # test = await self.get_chats("party")
                # if test is not None and "data" in test:
                # message = test["data"][0]
                # print("ID: {}".format(message.get("id")))
                # print("Time: {}".format(message.get("timestamp")))
                # print("User: {}".format(message.get("user", "None")))
                # if "uuid" in message:
                # print("User UID: {}".format(message.get("uuid")))
                # print("Message: {}".format(
                # message.get("text").replace("` `", "\n").strip("`")))


def setup(bot):
    habitica = Habitica(bot)
    bot.add_cog(habitica)
    bot.loop.create_task(habitica.clock())
