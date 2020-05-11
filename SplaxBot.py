import discord
from discord.ext.commands import Bot
import asyncio
import nest_asyncio
from dotenv import load_dotenv
import os
import traceback
import sys
from mcstatus import MinecraftServer
import string_assist
import embed_assist

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = Bot(command_prefix="!")

with open("bad_words.txt") as file:
    bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]

is_admin = False
admin_roles = []


def get_server_count(server):
    minecraft_server = MinecraftServer.lookup(server)
    try:
        server_status = minecraft_server.status()
        return server_status.players.online
    except:
        return -1


def get_mod_channel():
    mod_channel = client.get_channel(644010198662643712)
    return mod_channel


async def update_servers():
    while True:
        server_channel = client.get_channel(707985423053357145)
        messages = []  # List of messages, gotten from ids stored in servers.txt

        with open("servers.txt") as servers:
            for index, line in enumerate(servers.readlines()):
                server_name = line.split(",")[0].strip()  # File lines are of format name, ip, version, message id
                server_ip = line.split(",")[1].strip()
                server_version = line.split(",")[2].strip()
                id = line.split(",")[3].strip() 
                id_message = await server_channel.fetch_message(int(id))  # Need to convert id from string to int
                messages.append(id_message)

                server = embed_assist.Server(server_name, server_ip, server_version)
                server_embed = server.get_server_embed()
                message = messages[index]
                await message.edit(content=None, embed=server_embed)

        await asyncio.sleep(60)  # Updates once every minute
        nest_asyncio.apply()


async def initialize_admin_check():
    global admin_roles
    try:
        tesseract = await client.fetch_guild(381758822240485376)
        tesseract_admin = tesseract.get_role(381807012352229377)
        admin_roles.append(tesseract_admin)
    except discord.Forbidden:
        print("Error: Missing Access")

    splaxcord = await client.fetch_guild(491335494064406529)
    splaxcord_admin = splaxcord.get_role(491335846335610891)
    splaxcord_mod = splaxcord.get_role(647942566515441692)
    admin_roles.append(splaxcord_admin)
    admin_roles.append(splaxcord_mod)

    try:
        hypesquad = await client.fetch_guild(374694560984465408)
        hypesquad_admin = hypesquad.get_role(390289508362354689)
        hypesquad_mod = hypesquad.get_role(595983010252455946)
        admin_roles.append(hypesquad_admin)
        admin_roles.append(hypesquad_mod)
    except discord.Forbidden:
        print("Error: Missing Access")


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----')
    await initialize_admin_check()
    await update_servers()


@client.event
async def on_message(message):  # Bad word censorship
    message_content = message.content.strip().lower()
    for bad_word in bad_words:
        if bad_word in message_content:
            mod_channel = client.get_channel(644010198662643712)  # #event-log in the tesseract
            await mod_channel.send("{} was caught saying a bad word in {}. Their message has been censored."
                                   .format(message.author.mention, message.channel.mention))
            await message.delete()
            print("Deleted 1 message by {} in #{}".format(message.author, message.channel))

    if message.author == client.user:
        return
    else:
        try:
            author_id = message.author.id
            author = message.guild.get_member(author_id)
            for role in author.roles:
                global admin_roles
                global is_admin
                if role in admin_roles:
                    is_admin = True
                    break
                else:
                    is_admin = False
            # print(is_admin)

        except AttributeError:
            return
    await client.process_commands(message)


# @client.event  # Proof of concept for muting someone when they join a channel, not currently used
# async def on_voice_state_update(member, before, after):
#     tesseract = await client.fetch_guild(381758822240485376)
#     spammo = await tesseract.fetch_member(128871926499115008)
#     if before.channel is not after.channel and after.channel is not None:
#         if member == spammo:
#             await spammo.edit(mute=True)
#             await asyncio.sleep(5)
#             nest_asyncio.apply()
#             await spammo.edit(mute=False)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.CommandNotFound):
        return
    elif isinstance(error, discord.ext.commands.MissingRequiredArgument):
        await ctx.send("Error: not enough arguments provided")
    elif isinstance(error, discord.Forbidden):
        print("Error: missing permissions")
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


@client.command(pass_context=True)
async def test(ctx):  # The first command I made for the bot, now tests if you are an admin
    global is_admin
    if is_admin:
        await ctx.send("Admin test successful")
    else:
        await ctx.send("This is a test")


@client.command(pass_context=True)
async def sendmessages(ctx, number):
    number = int(number)
    global is_admin
    if is_admin:
        for num in range(number):
            await ctx.send("Placeholder {}".format(num))
        await ctx.send("Sent {} placeholder messages".format(number))
    else:
        await ctx.send("Error: the sendmessages command is for admins only.")


@client.command(pass_context=True)
async def add_remake(ctx, name, ip, version):
    server_channel = client.get_channel(707985423053357145)
    server = embed_assist.Server(name, ip, version)
    server_embed = server.get_server_embed()
    server_message = await server_channel.send(content=None, embed=server_embed)
    server_string = "{}, {}, {}, {}".format(name, ip, version, server_message.id)

    with open("servers.txt", "r+") as server_file:  # Puts new remake at top of file
        content = server_file.read()
        server_file.seek(0, 0)
        server_file.write(server_string + '\n' + content)

    await ctx.send("Successfully added remake {}".format(name))


@client.command(pass_context=True)
async def remove_remake(ctx, name):
    server_channel = client.get_channel(707985423053357145)
    lines_skipped = False
    servers_file = "servers.txt"
    dummy_file = "serversdummy.txt"

    # All this code is to safely copy the file one line at a time, then remove the original
    with open(servers_file, "r") as read_file, open(dummy_file, "w") as write_file:
        for line in read_file:
            # If current line number matches the given line then skip copying
            if line.split(",")[0].strip() != name:
                write_file.write(line)
            else:
                lines_skipped = True
                message_id = int(line.split(",")[3].strip())
                remake_message = await server_channel.fetch_message(message_id)
                await remake_message.delete()

    if lines_skipped:
        try:
            os.remove(servers_file)
            os.rename(dummy_file, servers_file)
        except PermissionError:  # If the file is still in use, wait 5 seconds and try again
            await asyncio.sleep(5)
            nest_asyncio.apply()
            os.remove(servers_file)
            os.rename(dummy_file, servers_file)
    else:
        os.remove(dummy_file)

    await ctx.send("Successfully removed remake {}".format(name))


@client.command(pass_context=True)
async def gazebo(ctx):
    await ctx.send("Tomlough is best gazebo admin")


@client.command(pass_context=True)
async def activity(ctx):
    await ctx.send("To see the activity of the DvZ remakes, check <#707985423053357145>")


@client.command(pass_context=True)
async def jimmy(ctx):
    role_jimmy = discord.utils.get(ctx.guild.roles, name="Jimmy")
    await ctx.send(role_jimmy.mention)


@client.command(pass_context=True)
async def timeout(ctx, member: discord.Member, duration=1, reason=""):
    role_timeout = discord.utils.get(ctx.guild.roles, name="Timeout")
    role_jimmy = discord.utils.get(ctx.guild.roles, name="Jimmy")
    timeout_duration = duration
    duration *= 3600

    async def process_timeout(seconds):
        await asyncio.sleep(seconds)
        await member.add_roles(role_jimmy)
        await member.remove_roles(role_timeout)

    global is_admin
    if is_admin:
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
    else:
        await ctx.send("Error: The timeout command is for admins only.")


@client.command(pass_context=True)
async def purge(ctx, member: discord.Member, channel: discord.TextChannel, number=1):
    deleted = 0

    global is_admin
    if is_admin:
        async for message in channel.history(limit=1000):
            if message.author == member:
                await message.delete()
                deleted += 1
            if deleted >= number:
                break
        mod_channel = client.get_channel(644010198662643712)
        await mod_channel.send("Purged {} messages by {} in {}".format(str(number), member, channel.mention))
        await ctx.message.delete()
    else:
        await ctx.send("Error: The purge command is for admins only.")


@client.command(pass_context=True)
async def kick(ctx, member: discord.Member, reason=""):
    global is_admin
    if is_admin:
        await ctx.send("{} kicked {} for reason: {}".format(ctx.author, str(member), reason))
        message = "You have been kicked from " + str(ctx.guild) + ". Reason: " + reason
        channel = await member.create_dm()
        await channel.send(message)
        await member.kick(reason=reason)
    else:
        await ctx.send("Error: The kick command is for admins only.")


@client.command(pass_context=True)
async def ban(ctx, member: discord.Member, duration=1, reason=""):
    async def process_ban(seconds):
        await asyncio.sleep(seconds)
        await member.unban()

    global is_admin
    if is_admin:
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

    else:
        await ctx.send("Error: The temp ban command is for admins only.")


@client.command(pass_context=True)
async def create_role(ctx, name="", color="255, 255, 255", mentionable=False, hoist=False):
    global is_admin
    if is_admin:
        color_tuple = eval(color)
        r = color_tuple[0]
        g = color_tuple[1]
        b = color_tuple[2]
        role_color = discord.Color.from_rgb(r, g, b)
        role = await ctx.guild.create_role(name=name, color=role_color, mentionable=mentionable, hoist=hoist)
        position = role.position
        await ctx.send("Successfully created role {} with the following properties:"
                       "\nPosition: {} \nMentionable: {} \nHoisted: {}"
                       "\nRGB: {}, {}, {}".format(str(role), position, mentionable, hoist,
                                                  r, g, b))
    else:
        await ctx.send("Error: the create role command is for admins only.")


@client.command(pass_context=True)
async def give_roles(ctx, member: discord.Member, roles=""):
    global is_admin
    if is_admin:
        roles_list = []
        roles_tuple = tuple(map(str, roles.split(", ")))
        for role_name in roles_tuple:
            roles_list.append(discord.utils.get(ctx.guild.roles, name=role_name))
        for role in roles_list:
            await member.add_roles(role)
            await ctx.send("Successfully gave role {} to {}".format(str(role), str(member)))
    else:
        await ctx.send("Error: the give roles command is for admins only.")


@client.command(pass_context=True)
async def edit_role(ctx, role: discord.Role, position=0, mentionable=False, hoist=False, color=None):
    global is_admin
    if is_admin:
        if color:
            color_tuple = eval(color)
            r = color_tuple[0]
            g = color_tuple[1]
            b = color_tuple[2]
            role_color = discord.Color.from_rgb(r, g, b)
            await role.edit(position=position, mentionable=mentionable, hoist=hoist, color=role_color)
            await ctx.send("Successfully edited role {} to have the following properties:"
                           "\nPosition: {} \nMentionable: {} \nHoisted: {}"
                           "\nRGB: {}, {}, {}".format(str(role), position, mentionable, hoist,
                                                      r, g, b))
        else:
            await role.edit(position=position, mentionable=mentionable, hoist=hoist)
            await ctx.send("Successfully edited role {} to have the following properties:"
                           "\nPosition: {} \nMentionable: {} \nHoisted: {}"
                           .format(str(role), position, mentionable, hoist))
    else:
        await ctx.send("Error: the edit role command is for admins only.")


@client.command(pass_context=True)
async def remove_roles(ctx, member: discord.Member, roles=""):
    if is_admin:
        roles_list = []
        roles_tuple = tuple(map(str, roles.split(", ")))
        for role_name in roles_tuple:
            roles_list.append(discord.utils.get(ctx.guild.roles, name=role_name))
        for role in roles_list:
            await member.remove_roles(role)
            await ctx.send("Successfully removed role {} from {}".format(str(role), str(member)))
    else:
        await ctx.send("Error: the remove roles command is for admins only.")


@client.command(pass_context=True)
async def nick(ctx, member: discord.Member, name=None):
    global is_admin
    if is_admin:
        await member.edit(nick=name)
        if name:
            await ctx.send("Successfully changed {}'s nickname to {}.".format(str(member), name))
        else:
            await ctx.send("Successfully removed {}'s nickname.".format(str(member)))
    else:
        await ctx.send("Error: the nick command is for admins only")


@client.command(pass_context=True)
async def mass_rename(ctx, name=None, is_prefix=False, is_suffix=False):
    global is_admin
    if is_admin:
        members = await ctx.guild.fetch_members().flatten()
        renamed = 0
        for member in members:
            try:
                if is_prefix:
                    nickname = name + member.display_name
                    await member.edit(nick=nickname)
                    renamed += 1
                elif is_suffix:
                    nickname = member.display_name + name
                    await member.edit(nick=nickname)
                    renamed += 1
                else:
                    await member.edit(nick=name)
                    renamed += 1
            except discord.Forbidden:
                await ctx.send("Error: missing permissions to edit user {}".format(str(member)))
        if name:
            await ctx.send("Successfully renamed {} users.".format(renamed))
        else:
            await ctx.send("Successfully removed nickname on {} users.".format(renamed))
    else:
        await ctx.send("Error: the mass rename command is for admins only")


@client.command(pass_context=True)
async def mute(ctx, member: discord.Member, duration=1, reason=""):
    global is_admin
    if is_admin:
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

    else:
        await ctx.send("Error: The temp mute command is for admins only.")


@client.command(pass_context=True)
async def info(ctx):
    await ctx.send("Splax Bot is the automated minion of the Tesseract Police State, built to boomer standards.")
    embed = embed_assist.get_info_embed()
    await ctx.send(embed=embed)


client.run(token)
