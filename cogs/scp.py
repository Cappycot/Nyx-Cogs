"""
Secure, Contain, Protect

This module requires Beautiful Soup 4.X.X and PIL 4.X.X to run!

TODO: Change titling system to fetch and cache title rather than preload it.
    - That way we can update 404 [ACCESS DENIED] entries as they are asked for.
TODO: Manually enter information for all of djkaktus' skips.
    - djkaktus uses a formatted picture for object class, etc.
"""

from io import BytesIO
from os import mkdir
from os.path import isdir, join
from re import compile, search

from PIL import Image, ImageDraw, ImageFont
from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag
from discord import Color, Embed, File
from discord.ext import commands
from discord.ext.commands import BucketType

# Name of the directory to be used to store things...
folder = "scp"
titles_file = "titles.txt"
# SCP series 4 is the most current...
highest_scp = 3999
series_range = (highest_scp + 1) // 1000
# SCPs range from 001 to 3999...
titles = {(i + 1): None for i in range(highest_scp)}


def scp_2521(embed: Embed):
    embed.colour = Color.red()
    return "Are you trying to get me killed?!?"


def scp_2602(embed: Embed):
    """Did you know this thing used to be a library?"""
    embed.set_field_at(0, name="Library Class:", value="Former")
    embed.title = "SCP-2602, which used to be a library"


# TODO: Check titles for:
# 2565
# 2769 (61231)
# 2864
# 2930
# 2956
# 3942

def scp_2565(embed: Embed):
    embed.colour = Color.red()
    embed.description = "Allison Eckhart"
    embed.set_field_at(0, name="Allison Eckhart Class:", value="Keter")


def scp_61231(embed: Embed):
    """SCP-2769: It's a really shitty implementation of some infohazard and I
    don't really feel like figuring the thing out. Seriously.
    """
    embed.description = "An Honest Buck"
    url = "".join(["http://scp-wiki.wdfiles.com/local-",
                   "-files/scp-2769/1280px-Cardisoma_armatus-front.jpg"])
    embed.set_image(url=url)
    embed.title = "SCP-61231"


def scp_2864(embed: Embed):
    embed.description = "Di Molte Voci"


def sccp_2930(embed: Embed):
    """SCP-2930, except with most of the letter c c being repeated LOL"""
    object_class = embed.fields[0].value
    embed.description = "Cross City City City City Hall"
    embed.set_field_at(0, name="Object Class Class:", value=object_class)
    containment = embed.fields[1].value
    embed.set_field_at(1, name="Special Containment Containment Procedures:",
                       value=containment)
    embed.title = "SCCP-2930"


def scp_2956(embed: Embed):
    embed.description = "A film by SCP-2956, products of Natura Toys."
    embed.title = "TriStar Pictures"


def scp_3942(embed: Embed):
    embed.description = "UNDEFINED"
    embed.title = "UNDEFINED"


hard_code_specials = {"SCP-2521": scp_2521, "SCP-2602": scp_2602,
                      "SCP-2565": scp_2565, "SCP-2769": scp_61231,
                      "SCP-2864": scp_2864, "SCP-2930": sccp_2930,
                      "SCP-2956": scp_2956, "SCP-3942": scp_3942}


def read_component(thing):
    if isinstance(thing, Tag):
        if thing.name == "em":
            return "*" + read_component(thing.next_element) + "*"
        elif thing.name == "strong":
            return "**" + read_component(thing.next_element) + "**"
        elif thing.name == "u":
            return "__" + read_component(thing.next_element) + "__"
        elif thing.attrs.get("style") == "text-decoration: line-through;":
            return "~~" + read_component(thing.next_element) + "~~"
        elif thing.attrs.get("id") is not None and "footnoteref" in \
                thing.attrs["id"]:
            return ""
        else:
            return read_component(thing.next_element)
    else:
        return thing


def fetch_level(element, limit=1024):
    length = 0
    parts = []
    if element is None:
        return "[DATA ERROR]"
    for thing in [element] + list(element.next_siblings):
        # component = read_component(thing)
        if isinstance(thing, Tag):
            if thing.name == "em":
                component = "*" + fetch_level(thing.next_element) + "*"
            elif thing.name == "strong":
                component = "**" + fetch_level(thing.next_element) + "**"
            elif thing.name == "u":
                component = "__" + fetch_level(thing.next_element) + "__"
            elif thing.attrs.get("style") == "text-decoration: line-through;":
                component = "~~" + fetch_level(thing.next_element) + "~~"
            elif thing.attrs.get("id") is not None and "footnoteref" in \
                    thing.attrs["id"]:
                return ""
            else:
                component = fetch_level(thing.next_element)
        else:
            component = thing
        if component:
            length += len(component)
            if length > limit - 3:
                if not component.endswith(".") or length > limit:
                    break
            else:
                parts.append(component)
    if len(parts) == 0:
        return "[WITHHELD]"
    return "".join(parts).strip("-:, ")


def save_titles():
    try:
        if not isdir(folder):
            mkdir(folder)
        data = open(join(folder, titles_file), "w")
        print("The following SCPs may need manual title entries:")
        for num in titles:
            if titles[num] is not None:
                data.write("".join([str(num), "=", titles[num], "\n"]))
            else:
                print(str(num))
        data.flush()
        data.close()
        return True
    except FileExistsError:
        return False


async def get_titles(loop):
    async with ClientSession(loop=loop) as session:
        for series in range(series_range):
            url = "http://scp-wiki.wikidot.com/scp-series"
            if series > 0:
                url += "-" + str(series + 1)
            print(url)
            async with session.get(url) as req:
                if req.status == 200:
                    soup = BeautifulSoup(await req.read(), "html.parser")
                    for num in range(1000):
                        num += series * 1000
                        if num < 10:
                            number = "00" + str(num)
                        elif num < 100:
                            number = "0" + str(num)
                        else:
                            number = str(num)
                        element = soup.find("a", string="SCP-" + number)
                        if element is not None:
                            titles[num] = fetch_level(element.next_sibling)
                else:
                    return False
    return save_titles()


async def load_titles(loop, force_fetch=False):
    if not force_fetch:
        try:
            data = open(join(folder, titles_file), "r")
            for line in data:
                args = line.split("=", 1)
                titles[int(args[0])] = args[1]
        except FileNotFoundError or IndexError or ValueError:
            force_fetch = True
    if force_fetch:
        return await get_titles(loop)
    return True


async def parse_scp(ctx, number: str, post_image=False):
    url = "http://scp-wiki.wikidot.com/scp-" + number
    message = await ctx.send("Fetching SCP information...")
    async with ctx.channel.typing(), ClientSession(
            loop=ctx.bot.loop) as session, session.get(url) as req:
        if req.status == 200:
            embed = Embed(title="SCP-" + number,
                          description=titles[int(number)],
                          url=url)
            source = BeautifulSoup(await req.read(), "html.parser")

            # Get the SCP class...
            object_class = source.find(
                string=compile("Object (Class[ ]?)+[:]?$")) or source.find(
                string=compile("Classification[:]?$"))
            # If you're the person who uses "Classification" f*ck off pls...
            if object_class is None:
                object_class = "[WITHHELD]"
            elif not object_class.next_element.strip():
                classes = []
                for sibling in object_class.next_element.next_siblings:
                    if sibling is not None:
                        if isinstance(sibling, Tag) and \
                                sibling.next_element is not None:
                            element = sibling.next_element.strip(": ")
                            classes.append("~~" + element + "~~")
                        elif sibling.strip():
                            classes.append(sibling.strip())
                object_class = " ".join(classes)
            else:
                object_class = object_class.next_element.strip(": ")
            embed.add_field(name="Object Class:", value=object_class)

            # Color the embed based on class...
            object_class = object_class.lower()
            if search("safe$", object_class) or search("safe[^~]+",
                                                       object_class):
                embed.colour = Color.green()
            elif search("euclid$", object_class) or search("euclid[^~]+",
                                                           object_class):
                embed.colour = Color.gold()
            elif search("keter$", object_class) or search("keter[^~]+",
                                                          object_class):
                embed.colour = Color.red()
            elif search("thaumiel$", object_class) or search("thaumiel[^~]+",
                                                             object_class):
                embed.colour = Color.blue()
            elif search("apollyon$", object_class) or search("apollyon[^~]+",
                                                             object_class):
                embed.colour = Color.red()

            # Fetch the containment procedures and description...
            containment = source.find(
                string=compile("Special (Containment )+Procedure[s]?[:]?$"))
            if containment is None or containment.next_element is None:
                containment = "[DATA ERROR]"
            else:
                containment = fetch_level(containment.next_element)
                if search("[.][~*_'\"]*$", containment) is None:
                    containment += "..."
            embed.add_field(name="Special Containment Procedures:",
                            value=containment)
            description = source.find(string=compile("Description[:]?$"))
            if description is None or description.next_element is None:
                description = "[DATA ERROR]"
            else:
                description = fetch_level(description.next_element)
                if search("[.][~*_'\"]*$", description) is None:
                    description += "..."
            embed.add_field(name="Description:", value=description)

            # Locate the image...
            image = source.find("div", compile("scp-image-block"))
            if post_image and image is not None:
                image = image.next_element
                if image is not None and isinstance(image, Tag):
                    image = image.get("src")
                    if image is not None:
                        embed.set_image(url=image)

            # Post-processing embed...
            addendum = None
            process = hard_code_specials.get("SCP-" + number)
            if process is not None:
                addendum = process(embed)
            await ctx.send(addendum, embed=embed)
        elif req.status == 404:
            await ctx.send(
                "Such an SCP is either classified or does not exist...")
        else:
            await ctx.send("An error occurred. ({})".format(str(req.status)))
    await message.delete()


class SCPFoundation:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def scp(self, ctx, number: int):
        """Retrieves information on a particular SCP."""
        if number <= 0:
            return
        elif number < 10:
            number = "00" + str(number)
        elif number < 100:
            number = "0" + str(number)
        else:
            number = str(number)
        await parse_scp(ctx, number, post_image=True)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, attach_files=True)
    @commands.cooldown(1, 5, BucketType.user)
    async def ohno(self, ctx, *words):
        """Generates your very own SCP-3078 cognitohazardous shitpost.

        e.g. "when you inhale the devil's mary jane smoke"
        """
        # Damn I tried to imitate the SCP-3078 instances but they don't follow
        # the same layout in different imitations, so the first one is followed
        # the best here.
        async with ctx.channel.typing():
            font = ImageFont.truetype(join(folder, "Calibri.ttf"), 19)
            append = None
            width = 256
            x_start = 22
            y_cur = 13
            y_pad = 3

            image = Image.open(join(folder, "SCP-3078.png"))
            draw = ImageDraw.Draw(image)

            for word in words:
                if append is None:
                    append = word
                else:
                    prev = append
                    append = " ".join([append, word])
                    w, h = draw.textsize(append, font=font)
                    if w > width:
                        append = word
                        draw.text((x_start, y_cur), prev, fill=(0, 0, 0),
                                  font=font)
                        y_cur += h + y_pad
            if append is not None:
                draw.text((x_start, y_cur), append, fill=(0, 0, 0), font=font)

            image_bytes = BytesIO()
            image.save(image_bytes, format="png")
            image_bytes.seek(0)
            await ctx.send(file=File(image_bytes, filename="SCP-3078.png"))
            image_bytes.close()


def setup(bot):
    bot.loop.run_until_complete(load_titles(bot.loop))
    bot.add_cog(SCPFoundation(bot))
