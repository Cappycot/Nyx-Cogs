"""
Secure, Contain, Protect

This module requires Beautiful Soup 4.X.X and PIL 4.X.X to run!
"""

from io import BytesIO
from os.path import join
from re import compile, search

from PIL import Image, ImageDraw, ImageFont
from aiohttp import ClientSession
from bs4 import BeautifulSoup, PageElement, Tag
from discord import Color, Embed, File
from discord.ext import commands
from discord.ext.commands import BucketType

# Name of the directory to be used to store things...
folder = join("data", "scp")
# Hard-coded object classes for SCPs that have their object classes in images.
# e.g. some of djkaktus' more prominent SCPs have special header images.
c_580 = "(~~Keter~~) Due to a review of current documentation as of January " \
        "5, 2009, this SCP has been reclassified as Euclid."
c_2718 = "``Catastrophic abort at D09E2AD9: HANDLE_NOT_FOUND``"
object_classes = {580: c_580, 1241: "", 1254: "~~Neutralized~~ Euclid",
                  1730: "Neutralized", 1848: "~~Euclid~~ Safe",
                  2062: "Kronecker", 2161: "Euclid",
                  2212: " [MASSIVE DATABASE CORRUPTION]", 2237: "[WITHHELD]",
                  2254: "Realität-Brecher", 2316: "Keter", 2718: c_2718,
                  2845: "Keter", 2935: "Keter", 3000: "Thaumiel",
                  3125: "Keter", 3301: "Safe", 3340: "Keter", 3521: "Safe",
                  3785: "Euclid", 3813: "Keter", 3933: "Euclid",
                  3935: "Euclid"}
# Description titles are cached, but may require resetting from time to time.
# These SCPs need embed descriptions manually entered at the moment:
# 2235
# 2565
# 2769
# 2864
# 2930
# 3352 redirects to 3353 which may or may not be intentional?
# 3570
# 3942
hard_code_descriptions = {2235: "The Ozymandias Effect",
                          2565: "Allison Eckhart", 2769: "An Honest Buck",
                          2864: "Di Molte Voci",
                          2930: "Cross City City City City Hall",
                          3570: "Umbral Ultimatum", 3942: "``UNDEFINED``"}
# Make command that cleans description cache maybe?
descriptions = hard_code_descriptions.copy()


# Put SCPs that have format screws or special meta properties here...
# e.g. The haiku rice bowl.


def scp_732(embed: Embed):
    """lmao"""
    embed.colour = Color.red()
    embed.set_field_at(0, name="Object Class:",
                       value="Ke@#%^ SUPR1337KETER!!!!!!1!!!1!111!!#$%^")


def scp_931(embed: Embed):
    """Man did I have fun with this one lol."""
    n = "Its Item Number"
    v = "Is SCP Nine Three One;\n**Object Class** is Safe."
    embed.set_field_at(0, name=n, value=v)
    n = "Heed these Procedures,"
    v = """
To keep the item secure—
**Special Containment**.

Effects are triggered
By some images of it—
Depends on angle.

Writing about it
Will always be affected,
Despite ignorance.
"""
    embed.set_field_at(1, name=n, value=v)
    n = "A Description of"
    v = "SCP Nine Thirty-One:\nIt is a rice bowl."
    embed.set_field_at(2, name=n, value=v)


def scp_1241(embed: Embed):
    embed.set_field_at(0, name="Object Class:",
                       value="Neutralised (formerly Safe)")


def scp_1561(embed: Embed):
    d = "His Majesty's SCP-MDLXI is currently being worn by King Data the " \
        "Expunged within the Kingdom of Site Redacted and is to be guarded " \
        "by at least 10 Knights at all times."
    embed.set_field_at(1, name="Regal Containment Decree:", value=d)


def scp_1798(embed: Embed):
    embed.colour = Color.gold()
    embed.set_field_at(0, name="Object Type:", value="Ectoentrophic")


def scp_2062(_):
    return "*Die ganzen Zahlen hat der liebe Gott gemacht, alles andere ist " \
           "Menschenwerk.*"


def scp_2161(embed: Embed):
    embed.set_field_at(1, name="Special Containment Procedures:",
                       value="[DATA ERROR]")
    embed.set_field_at(2, name="Description:",
                       value="[DATA ERROR]")
    return "I'm  having  issues  with  this  one...  sorry."


def scp_2212(embed: Embed):
    embed.set_field_at(0, name="Object Class:",
                       value="[MASSIVE DATABASE CORRUPTION]")
    embed.set_field_at(1, name="Special Containment Procedures:",
                       value="[MASSIVE DATABASE CORRUPTION]")


def scp_2237(embed: Embed):
    """This SCP frequently changes between its Euclid and Thaumiel variant."""
    embed.set_field_at(1, name="Special Containment Procedures:",
                       value="[DATA ERROR]")
    embed.set_field_at(2, name="Description:",
                       value="[DATA ERROR]")


def scp_2316(_):
    return "**``Please repeat the following phrase slowly and clearly into " \
           "your terminal microphone:``**\n``I do not recognize the bodies " \
           "in the water.``"


def scp_2357(embed: Embed):
    v = "SCP-2357 poses no danger to anyone, although it very easily could " \
        "have been made that way."
    embed.set_field_at(0, name="Obj3ct Class:", value=v)


def scp_2521(embed: Embed):
    embed.colour = Color.red()
    return ":writing_hand: :desktop: :speech_balloon: :no_good:"


def scp_2565(embed: Embed):
    embed.colour = Color.red()
    embed.description = "Allison Eckhart"
    embed.set_field_at(0, name="Allison Eckhart Class:", value="Keter")


def scp_2576(_):
    return "Contained within the image below is a memetic entity that " \
           "appears to be a multi-colored goat. Properly inoculated " \
           "individuals should be able to perceive this goat."


def scp_2602(embed: Embed):
    """Did you know this thing used to be a library?"""
    embed.set_field_at(0, name="Library Class:", value="Former")


def scp_2718(embed: Embed):
    embed.set_field_at(2, name="Description:", value="DAMMERUNG EYES ONLY")


def scp_2769(embed: Embed):
    """SCP-2769: It's an implementation of some weird infohazard and I don't
    really feel like figuring the thing out. Seriously.
    """
    embed.description = "An Honest Buck"
    url = "".join(["http://scp-wiki.wdfiles.com/local-",
                   "-files/scp-2769/1280px-Cardisoma_armatus-front.jpg"])
    embed.set_image(url=url)


def scp_2851(embed: Embed):
    embed.colour = Color.red()
    return "I like this embed's color. Very powerful. Good work."


def scp_2839(embed: Embed):
    embed.set_field_at(0, name="Name:", value="Octavius Weppler")
    o = "Field researcher, member of Cognitohazardous Research Division, " \
        "Archivist."
    embed.set_field_at(1, name="Occupation", value=o)
    embed.set_field_at(2, name="Security Clearance Level:", value="3")
    return "If you've ended up on this page by accessing the document for " \
           "SCP-2839, sorry to tell you but you've ended up here by " \
           "mistake. We currently have no idea why this keeps happening, " \
           "probably IT maintenance bull or something like that, but since " \
           "there is no current item actually designated as SCP-2839, " \
           "sorting this problem out is currently low-priority. Sorry for " \
           "the inconvenience.\n\n*- Dr. Weppler*"


def scp_2864(embed: Embed):
    """How about "Di Molte Voci"? Italian for "out of many voices".- Grimes"""
    embed.description = "Di Molte Voci"
    q = "*Not assigning an object class. It's not going to stay put, and " \
        "the database search will probably choke on it somehow.*"
    embed.set_field_at(0, name="Russo Sr.:", value=q)
    q = "*For the Voci itself, I see no reason a standard lockbox wouldn't " \
        "work. Should definitely stay at Site-82, since transport risks " \
        "incidental contamination.*"
    embed.set_field_at(1, name="Kingham:", value=q)
    q = "*The central anomaly involves the disruption of certain " \
        "information, randomizing some pieces and replacing others with " \
        "whatever discussions went into it.*"
    embed.set_field_at(2, name="Grimes:", value=q)
    q = "*Seems to me that it's specifically affecting consensus-based " \
        "information (like standard anomaly summaries), which is why " \
        "there's nothing close to a real containment report here — just the " \
        "stuff that's supposed to stay behind the scenes. Things like " \
        "titles, protocols, object classes, explicit statements of " \
        "authority, and a few other identifiers switch around at random " \
        "too. Not sure why our names are unaffected.*"
    embed.add_field(name="Kingham:", value=q)
    q = "*Anyways, I was checking out an antique shop in Sicily (which is " \
        "to say, I was asking for trouble) when I find an extremely pretty " \
        "glass mask that looks like it belongs to a jester.*"
    embed.add_field(name="Strunk:", value=q)


def scp_2930(embed: Embed):
    """SCP-2930, except with most of the letter c c being repeated LOL"""
    object_class = embed.fields[0].value
    embed.description = "Cross City City City City Hall"
    embed.set_field_at(0, name="Object Class Class:", value=object_class)
    containment = embed.fields[1].value
    embed.set_field_at(1, name="Special Containment Containment Procedures:",
                       value=containment)


def scp_3340(_):
    return "This page is undergoing deletion."


hard_code_specials = {732: scp_732, 931: scp_931, 1241: scp_1241,
                      1561: scp_1561, 1798: scp_1798, 2062: scp_2062,
                      2161: scp_2161, 2212: scp_2212, 2237: scp_2237,
                      2316: scp_2316, 2357: scp_2357, 2521: scp_2521,
                      2565: scp_2565, 2576: scp_2576, 2602: scp_2602,
                      2718: scp_2718, 2769: scp_2769, 2839: scp_2839,
                      2851: scp_2851, 2864: scp_2864, 2930: scp_2930}


def fetch_level(element, limit=1024):
    length = 0
    parts = []
    if element is None:
        return "[DATA ERROR]"
    for thing in [element] + list(element.next_siblings):
        if isinstance(thing, Tag):
            if thing.name == "br":
                component = "\n"
            elif thing.name == "em":
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


async def parse_scp(ctx, number, debug=False):
    # Gonna fuck with y'all with SCCP-2930 here.
    if number == 931:
        message = await ctx.send("Going to fetch your\nSCP information.\n"
                                 "Got it! Here you go...")
    elif number == 2930:
        message = await ctx.send("Fetching SCCP information...")
    else:
        message = await ctx.send("Fetching SCP information...")
    if number < 10:
        scp_number = "SCP-00{}".format(number)
    elif number < 100:
        scp_number = "SCP-0{}".format(number)
    else:
        scp_number = "SCP-{}".format(number)
    url = "http://scp-wiki.wikidot.com/{}".format(scp_number)
    # Make request for SCP entry page.
    async with ctx.channel.typing(), ClientSession(
            loop=ctx.bot.loop) as session, session.get(url) as req:
        if req.status == 200:
            source = BeautifulSoup(await req.read(), "html.parser")
            # Get the title from the accessed page. This is always consistent.
            title = source.find(id="page-title").next_element.strip()
            # Get title description either by hard code or searching series.
            description = descriptions.get(number, None)
            if description is None and not debug:
                desc_url = "http://scp-wiki.wikidot.com/scp-series"
                if number > 999:
                    desc_url = "{}-{}".format(desc_url, number // 1000 + 1)
                async with session.get(desc_url) as req2:
                    if req2.status == 200:
                        source2 = BeautifulSoup(await req2.read(),
                                                "html.parser")
                        element = source2.find("a", string=scp_number)
                        if element is not None:
                            description = fetch_level(element.next_sibling)
                            descriptions[number] = str(description)
            embed = Embed(title=title, description=description,
                          url=url.lower())
            # Get the SCP class.
            object_class = object_classes.get(number, None)
            if object_class is None:
                object_class = source.find(
                    string=compile(
                        "Object ([Cc]lass[ ]?)+[:]?$"))
            if object_class is None:
                # If you're the person who uses "Classification" f*ck off.
                object_class = source.find(
                    string=compile("Anomaly [Cc]lass[:]?$")) or source.find(
                    string=compile("Classification[:]?$")) or source.find(
                    string=compile("Item ([Cc]lass[ ]?)+[:]?$"))
            # Hunt down object class from element.
            if object_class is None:
                object_class = "[WITHHELD]"
            elif isinstance(object_class, PageElement):
                try:
                    if not object_class.next_element.strip(": "):  # Added :
                        classes = []
                        for sibling in object_class.next_element.next_siblings:
                            if sibling is not None:
                                if isinstance(sibling, Tag) and \
                                        sibling.next_element is not None:
                                    element = sibling.next_element
                                    classes.append("~~" + element + "~~")
                                elif sibling.strip(": "):  # Added :
                                    classes.append(
                                        sibling.strip(": "))  # Added :
                        object_class = " ".join(classes)
                    else:
                        object_class = object_class.next_element.strip(": ")
                except (AttributeError, TypeError):
                    object_class = "[DATA ERROR]"
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
            elif debug:
                print("No proper color attribution for class {}.".format(
                    object_class))
            # Fetch the containment procedures and description...
            scp1 = compile(
                "(Special )?([Cc]ontainment )+[Pp]rocedure[s]?[:]?$")
            scp2 = compile(
                "(Special )?([Cc]ontainment )+[Pp]rocedure[s]?.*[:]$")
            # For the one f*cker who writes "Protocols" instead of "Procedures"
            scp3 = compile("(Special )?([Cc]ontainment )+[Pp]rotocol[s]?[:]?$")
            containment = source.find(string=scp1)
            if containment is None:
                containment = source.find(string=scp2) or source.find(
                    string=scp3)
            if containment is None or containment.next_element is None:
                containment = "[DATA ERROR]"
                if debug:
                    print("Could not find containment procedures.")
            else:
                containment = fetch_level(containment.next_element)
                if search("[.][~*_'\"]*$", containment) is None:
                    containment += "..."
            embed.add_field(name="Special Containment Procedures:",
                            value=containment)
            description = source.find(
                string=compile("Description[:]?$")) or source.find(
                string=compile("Description.*[:]$"))
            if description is None or description.next_element is None:
                description = "[DATA ERROR]"
                if debug:
                    print("Could not find description.")
            else:
                description = fetch_level(description.next_element)
                if search("[.][~*_'\"]*$",
                          description) is None and description != "[WITHHELD]":
                    description += "..."
            embed.add_field(name="Description:", value=description)
            # Locate the image...
            image = source.find("div", compile("scp-image-block"))
            if image is not None:
                image = image.next_element
                if image is not None and isinstance(image, Tag):
                    image = image.get("src")
                    if image is not None:
                        embed.set_image(url=image)
            # Post-process embed.
            addendum = None
            process = hard_code_specials.get(number)
            if process is not None:
                addendum = process(embed)
            await ctx.send(addendum, embed=embed)
        # If no SCP exists with such a number.
        elif req.status == 404:
            await ctx.send(
                "Such an SCP is either classified or does not exist...")
            if debug:
                print("(Doesn't exist.)")
        # Cover other web errors.
        else:
            await ctx.send(
                "An error occured. ({})".format(str(req.status)))
            if debug:
                print("Hit server error {}.".format(str(req.status)))
                ctx.flag = True
    await message.delete()


class SCPFoundation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, BucketType.user)
    async def scp(self, ctx, number: int):
        """Retrieves information on a particular SCP."""
        await parse_scp(ctx, number)

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
            # Write image to byte stream and send.
            image_bytes = BytesIO()
            image.save(image_bytes, format="png")
            image_bytes.seek(0)
            await ctx.send(file=File(image_bytes, filename="SCP-3078.png"))
            image_bytes.close()


def setup(bot):
    bot.add_cog(SCPFoundation(bot))


async def get_titles(loop, titles):
    async with ClientSession(loop=loop) as session:
        for series in range(4):
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
    print("The following SCPs may need manual title entries:")
    for num in titles:
        if titles[num] is None:
            print(str(num))


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    test_titles = False
    if test_titles:
        titles = {(i + 1): None for i in range(3999)}
        loop.run_until_complete(get_titles(loop, titles))
    else:
        class TestBot:
            def __init__(self):
                self.loop = loop

            async def __aenter__(self):
                pass

            async def __aexit__(self, *_):
                pass


        class TestChannel:
            def typing(self):
                return self

            async def __aenter__(self):
                pass

            async def __aexit__(self, *_):
                pass


        class TestContext:
            def __init__(self):
                self.bot = TestBot()
                self.channel = TestChannel()
                self.flag = False

            async def send(self, *_, **__):
                return self

            async def delete(self):
                pass

            async def __aenter__(self):
                pass

            async def __aexit__(self, *_):
                pass


        ctx = TestContext()

        for i in range(2000, 3000):
            print(i)
            loop.run_until_complete(parse_scp(ctx, i, debug=True))
            if ctx.flag:
                break
