from discord.ext.commands import Bot
from discord.ext import commands
from mcstatus import MinecraftServer
from dotenv import load_dotenv
from datetime import datetime, timedelta
import aiohttp
import asyncio
import nest_asyncio
import discord
import os
import traceback
import sys
import string_assist
import embed_assist
import xml.etree.ElementTree as ET

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = Bot(command_prefix="!")

with open("bad_words.txt") as file:
    bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]


def get_server_count(server):
    minecraft_server = MinecraftServer.lookup(server)
    try:
        server_status = minecraft_server.status()
        return server_status.players.online
    except:
        return -1


def format_xml(elem, level=0):  # Some code I found from a google search
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            format_xml(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def add_remake_xml(name, ip, version, id, invite):
    tree = ET.parse("remakes.xml")
    root = tree.getroot()
    remakes = root.find("./remakes")
    name_split = name.split()
    tag_name = name_split[0]
    new_remake = ET.SubElement(remakes, tag_name)

    remake_name = ET.SubElement(new_remake, "name")
    remake_ip = ET.SubElement(new_remake, "ip")
    remake_version = ET.SubElement(new_remake, "version")
    remake_id = ET.SubElement(new_remake, "id")
    remake_invite = ET.SubElement(new_remake, "invite")

    remake_name.text = name
    remake_ip.text = ip
    remake_version.text = version
    remake_id.text = id
    remake_invite.text = invite

    format_xml(root)
    tree.write("remakes.xml", xml_declaration=True, encoding="utf-8", method="xml")


def remove_remake_xml(name):
    tree = ET.parse("remakes.xml")
    root = tree.getroot()
    remakes = root.find("./remakes")
    tag_name = name.split()[0]
    target_remake = root.find("./remakes/{}".format(tag_name))
    remakes.remove(target_remake)

    format_xml(root)
    tree = ET.ElementTree(root)
    tree.write("remakes.xml", xml_declaration=True, encoding="utf-8", method="xml")


def get_remake_info(remake_index):
    tree = ET.parse("remakes.xml")
    root = tree.getroot()
    name = root[0][remake_index][0].text
    ip = root[0][remake_index][1].text
    version = root[0][remake_index][2].text
    id = int(root[0][remake_index][3].text)
    return name, ip, version, id


async def remove_spammo_roles():
    while True:
        tesseract = client.get_guild(381758822240485376)
        spammo = tesseract.get_member(128871926499115008)
        roles = spammo.roles
        if len(roles) > 4:
            for role in roles[1:]:
                try:
                    await spammo.remove_roles(role)
                except discord.Forbidden:  # This is not a good way to handle errors, but for my specific case it works
                    pass
        else:
            pass

        await asyncio.sleep(1800)
        nest_asyncio.apply()


async def update_servers():
    while True:
        server_channel = client.get_channel(707985423053357145)
        tree = ET.parse("remakes.xml")
        root = tree.getroot()
        remakes = root.find("./remakes")
        for remake_index, remake in enumerate(remakes):
            try:
                name, ip, version, id = get_remake_info(remake_index)
                message = await server_channel.fetch_message(id)
                server = embed_assist.Server(name, ip, version)
                server_embed = server.get_server_embed()
                await message.edit(content=None, embed=server_embed)
            except IndexError:
                print("Remake not found")
                pass
            except discord.NotFound:
                print("Message not found")
                pass
            except OSError:
                print("Timeout error")
                pass
            except discord.HTTPException:
                print("Service unavailable")
                pass
            except aiohttp.ServerDisconnectedError:
                print("Server disconnected")
            except Exception as error:
                print('Ignoring exception in update_servers', file=sys.stderr)
                traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
                pass

        await asyncio.sleep(60)  # Updates once every minute
        nest_asyncio.apply()


def admin_check():
    def predicate(ctx):
        return ctx.author.guild_permissions.manage_guild
    return commands.check(predicate)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----')
    await update_servers()


# @client.event
# async def on_message(message):  # Bad word censorship, not currently used
#     message_content = message.content.strip().lower()
#     for bad_word in bad_words:
#         if bad_word in message_content:
#             mod_channel = client.get_channel(644010198662643712)  # #event-log in the tesseract
#             await mod_channel.send("{} was caught saying a bad word in {}. Their message has been censored."
#                                    .format(message.author.mention, message.channel.mention))
#             await message.delete()
#             print("Deleted 1 message by {} in #{}".format(message.author, message.channel))
#
#     if message.author == client.user:
#         return
#     await client.process_commands(message)


@client.event
async def on_bulk_message_delete(messages):
    mod_channel = client.get_channel(695334610200035388)
    await mod_channel.send("{} messages bulk deleted".format(len(messages)))
    for message in messages:
        await mod_channel.send("{}: {}".format(message.author, message.content))


@client.event
async def on_member_join(member):  # Only autorole if account is older than week
    hypesquad = await client.fetch_guild(374694560984465408)
    if member.guild == hypesquad:
        dvz = discord.utils.get(member.guild.roles, name="DvZ")
        creation_time = member.created_at
        one_week_ago = datetime.now() - timedelta(weeks=1)

        if creation_time >= one_week_ago:
            print("User too young")
        else:
            await member.add_roles(dvz)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.CommandNotFound):
        return
    elif isinstance(error, discord.ext.commands.MissingRequiredArgument):
        await ctx.send("Error: not enough arguments provided")
    elif isinstance(error, discord.Forbidden):
        print("Error: missing permissions")
    elif isinstance(error, commands.CheckFailure):
        print("User has insufficient permissions to use command")
    elif isinstance(error, OSError):
        print("Timeout error")
    else:  # Traceback code from StackOverflow
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


@client.command(pass_context=True)
@admin_check()
async def test(ctx):  # The first command I made for the bot, now tests if you are an admin
    await ctx.send("Admin test successful")


@test.error
async def test_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Error: You do not have permission to use this command")


@client.command(pass_context=True)
@admin_check()
async def spammo(ctx):
    await ctx.send("Starting up the Spammo auto-role remover")
    await remove_spammo_roles()


@spammo.error
async def spammo_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Error: You do not have permission to use this command")


@client.command(pass_context=True)
async def message(ctx, id):
    for guild in client.guilds:
        for channel in guild.text_channels:
            try:
                message = await channel.fetch_message(id)

                user_name = message.author.name
                user_avatar = await message.author.avatar_url.read()

                webhook = await ctx.channel.create_webhook(name=user_name, avatar=user_avatar,
                                                           reason="Splax Bot Message Displayer")
                await webhook.send(content=message.content)
                await webhook.delete()

            except discord.NotFound:
                pass
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass


@client.command(pass_context=True)
@admin_check()
async def add_remake(ctx, *, args):
    name = ""
    args = args.split(" ")
    for arg in args[:-3]:
        name += " " + arg
    name = name.strip()
    invite = args[-1]
    version = args[-2]
    ip = args[-3]

    original_name = name
    if "'" in name:
        name.replace("'", "")
    if "’" in name:
        name.replace("’", "")

    server_channel = client.get_channel(707985423053357145)
    server = embed_assist.Server(name, ip, version)
    server_embed = server.get_server_embed()
    server_message = await server_channel.send(content=None, embed=server_embed)
    id_string = str(server_message.id)
    add_remake_xml(name, ip, version, id_string, invite)
    await ctx.send("Successfully added remake: {}".format(original_name))


@add_remake.error
async def add_remake_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Error: You do not have permission to use this command")


@client.command(pass_context=True)
@admin_check()
async def remove_remake(ctx, *, args):
    name = ""
    args = args.split(" ")
    for arg in args:
        name += " " + arg
    name = name.strip()

    original_name = name
    if "'" in name:
        name.replace("'", "")
    if "’" in name:
        name.replace("’", "")

    tree = ET.parse("remakes.xml")
    root = tree.getroot()
    tag_name = args[0]
    id_element = root.find("./remakes/{}/id".format(tag_name))
    id = int(id_element.text)

    server_channel = client.get_channel(707985423053357145)
    remake_message = await server_channel.fetch_message(id)
    await remake_message.delete()

    remove_remake_xml(name)
    await ctx.send("Successfully removed remake: {}".format(original_name))


@remove_remake.error
async def remove_remake_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Error: You do not have permission to use this command")


@client.command(pass_context=True)
@admin_check()
async def refresh_remakes(ctx):  # Sorts the remakes and then refreshes the messages
    server_channel = client.get_channel(707985423053357145)
    tree = ET.parse("remakes.xml")
    root = tree.getroot()
    remakes = root.find("./remakes")
    remake_dict = {}
    id_list = []

    # First half of the process - sort the remakes
    for remake_index, remake in enumerate(remakes):  # Load the remakes into a dictionary to be sorted
        remake_element = root[0][remake_index]
        message_id = int(root[0][remake_index][3].text)
        remake_invite_text = root[0][remake_index][4].text

        remake_invite = await client.fetch_invite(remake_invite_text)
        remake_members = remake_invite.approximate_member_count

        remake_dict[remake_element] = remake_members
        id_list.append(message_id)

    for remake in list(remakes):
        remakes.remove(remake)

    # Sorting code from StackOverflow
    sorted_remake_dict = {key: value for key, value in sorted(remake_dict.items(), key=lambda item: item[1])}
    for remake in sorted_remake_dict:
        remakes.append(remake)
    for index, id in enumerate(id_list):
        root[0][index][3].text = str(id)

    format_xml(root)
    tree.write("remakes.xml", xml_declaration=True, encoding="utf-8", method="xml")

    # Second half of the process, refresh the messages
    for remake_index, remake in enumerate(remakes):
        name, ip, version, id = get_remake_info(remake_index)

        message = await server_channel.fetch_message(id)
        await message.delete()
        server = embed_assist.Server(name, ip, version)
        server_embed = server.get_server_embed()
        new_message = await server_channel.send(content=None, embed=server_embed)

        id_element = root[0][remake_index][3]
        id_element.text = str(new_message.id)

    format_xml(root)
    tree.write("remakes.xml", xml_declaration=True, encoding="utf-8", method="xml")

    await ctx.send("Successfully refreshed remake messages")


@refresh_remakes.error
async def refresh_remakes_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Error: You do not have permission to use this command")


@client.command(pass_context=True)
async def welcome(ctx):
    await ctx.send("**For server IPs and info, check <#582980469444968475> and <#707985423053357145>.**\n"
                   "There are no DvZ servers that are active 24/7, but you will find the most activity on weekends."
                   "\nThe most active servers are The Gazebo and Nightfall, join their discord servers "
                   "and sign up for their game alert roles to be notified when games are starting.")


@client.command(pass_context=True)  # Used to test for when discord.py implements role mention for bots
@admin_check()
async def jimmy(ctx):
    role_jimmy = discord.utils.get(ctx.guild.roles, name="Jimmy")
    await ctx.send(role_jimmy.mention)


@jimmy.error
async def jimmy_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Error: You do not have permission to use this command")


@client.command(pass_context=True)
@admin_check()
async def timeout(ctx, member: discord.Member, duration=1, *, reason):
    async def process_timeout(seconds):
        await asyncio.sleep(seconds)
        await member.add_roles(role_jimmy)
        await member.remove_roles(role_timeout)

    role_timeout = discord.utils.get(ctx.guild.roles, name="Timeout")
    role_jimmy = discord.utils.get(ctx.guild.roles, name="Jimmy")
    timeout_duration = duration
    duration *= 3600
    channel = await member.create_dm()
    await member.add_roles(role_timeout)
    await member.remove_roles(role_jimmy)

    timeout = string_assist.Timeout(ctx.guild, ctx.author, member, timeout_duration, reason)
    mod_string = timeout.get_mod_channel_string()
    user_string = timeout.get_user_dm_string()

    await ctx.send(mod_string)
    await channel.send(user_string)

    await process_timeout(duration)
    nest_asyncio.apply()

    await channel.send("Your timeout from {} has been removed.".format(ctx.guild))
    await ctx.send("The timeout on {} has been removed.".format(member))


@timeout.error
async def timeout_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Error: You do not have permission to use this command")


@client.command(pass_context=True)
@admin_check()
async def purge(ctx, member: discord.Member, channel: discord.TextChannel, number=1):
    deleted = 0
    async for message in channel.history(limit=1000):
        if message.author == member:
            await message.delete()
            deleted += 1
        if deleted >= number:
            break
    await ctx.send("Purged {} messages by {} in {}".format(str(number), member, channel.mention))
    await ctx.message.delete()


@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Error: You do not have permission to use this command")


@client.command(pass_context=True)
@admin_check()
async def kick(ctx, member: discord.Member, *, reason):
    await ctx.send("{} kicked {} for reason: {}".format(ctx.author, str(member), reason))
    message = "You have been kicked from " + str(ctx.guild) + ". Reason: " + reason
    channel = await member.create_dm()
    await channel.send(message)
    await member.kick(reason=reason)


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Error: You do not have permission to use this command")


@client.command(pass_context=True)
@admin_check()
async def ban(ctx, member: discord.Member, duration=1, *, reason):
    async def process_ban(seconds):
        await asyncio.sleep(seconds)
        await member.unban()

    channel = await member.create_dm()

    ban = string_assist.Ban(ctx.guild, ctx.author, member, duration, reason)
    mod_string = ban.get_mod_channel_string()
    user_string = ban.get_user_dm_string()

    await ctx.send(mod_string)
    await channel.send(user_string)

    await member.ban(reason=reason, delete_message_days=0)
    await process_ban(duration)
    nest_asyncio.apply()

    await channel.send("Your ban from {} has been removed".format(ctx.guild))
    await ctx.send("The ban on {} has been removed.".format(member))


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Error: You do not have permission to use this command")


@client.command(pass_context=True)
@admin_check()
async def nick(ctx, member: discord.Member, *, name):
    await member.edit(nick=name)
    if name:
        await ctx.send("Successfully changed {}'s nickname to {}.".format(str(member), name))
    else:
        await ctx.send("Successfully removed {}'s nickname.".format(str(member)))


@nick.error
async def nick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Error: You do not have permission to use this command")


@client.command(pass_context=True)
@admin_check()
async def mute(ctx, member: discord.Member, duration=1, *, reason):
    await member.edit(mute=True)
    channel = await member.create_dm()
    minute_duration = duration
    duration *= 60

    if minute_duration == 1:
        await channel.send("You have been temporarily muted from {} for {} minute. Reason: {}"
                           .format(str(ctx.guild), minute_duration, reason))
        await ctx.send("{} was temporarily muted for {} minute. Reason: {}"
                       .format(member, minute_duration, reason))
    else:
        await channel.send("You have been temporarily muted from {} for {} minutes. Reason: {}"
                           .format(str(ctx.guild), minute_duration, reason))
        await ctx.send("{} was temporarily muted for {} minutes. Reason: {}"
                       .format(member, minute_duration, reason))

    await asyncio.sleep(duration)
    nest_asyncio.apply()
    await member.edit(mute=False)
    await channel.send("You have been unmuted from {}".format(str(ctx.guild)))


@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("Error: You do not have permission to use this command")


@client.command(pass_context=True)
async def info(ctx):
    await ctx.send("Splax Bot is the bot of Splax, checking for activity in DvZ remakes"
                   " and offering many moderation commmands")
    embed = embed_assist.get_info_embed()
    await ctx.send(embed=embed)


client.run(token)
