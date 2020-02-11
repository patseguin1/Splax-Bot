import discord
from discord.ext.commands import Bot
import asyncio
import nest_asyncio
from dotenv import load_dotenv
import os
import random

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = Bot(command_prefix="!")
with open("bad_words.txt") as file:
    bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]

with open("quotes.txt") as quote_file:
    quotes = [quote.strip() for quote in quote_file.readlines()]

mod_channel = client.get_channel(644010198662643712)
is_admin = False
admin_roles = []


async def initialize_admin_check():
    tesseract = await client.fetch_guild(381758822240485376)
    tesseract_admin = tesseract.get_role(381807012352229377)
    splaxcord = await client.fetch_guild(491335494064406529)
    splaxcord_admin = splaxcord.get_role(491335846335610891)
    splaxcord_mod = splaxcord.get_role(647942566515441692)
    global admin_roles
    admin_roles = [tesseract_admin, splaxcord_admin, splaxcord_mod]


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----')
    await initialize_admin_check()


@client.event
async def on_message(message):  # Bad word censorship
    message_content = message.content.strip().lower()
    for bad_word in bad_words:
        if bad_word in message_content:
            await mod_channel.send("{} was caught saying a bad word in {}. Their message has been censored."
                                   .format(message.author.mention, message.channel.mention))
            await message.delete()
            print("Deleted 1 message by {} in #{}".format(message.author, message.channel))

    if message.author == client.user:
        return
    else:
        for role in message.author.roles:
            if role in admin_roles:
                global is_admin
                is_admin = True
                break

    await client.process_commands(message)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.CommandNotFound):
        print("Error: Invalid command detected")


@client.command(pass_context=True)
async def test(ctx):
    if is_admin:
        await ctx.send("Admin test successful")
    else:
        await ctx.send("This is a test")


@client.command(pass_context=True)
async def gazebo(ctx):
    await ctx.send("Tomlough is best gazebo admin")


@client.command(pass_context=True)
async def quote(ctx, number=None):
    if number:
        quote_index = int(number)-1
        quote = quotes[quote_index]
        await ctx.send("Quote #{}: {}".format(number, quote))
    else:
        quote_index = random.randint(0, len(quotes))
        quote = quotes[quote_index]
        await ctx.send("Quote #{}: {}".format(quote_index+1, quote))


@client.command(pass_context=True)
async def join_channel(ctx, channel: discord.VoiceChannel, password=""):
    test_vc = client.get_channel(574393571432726528)
    if channel == test_vc:
        if password == "Stream":
            await ctx.author.edit(voice_channel=channel)
        else:
            await ctx.send("Error: incorrect password")
    else:
        await ctx.send("Error: channel is not password protected")


@client.command(pass_context=True)
async def timeout(ctx, member: discord.Member, duration="1", reason=""):
    role_timeout = discord.utils.get(ctx.guild.roles, name="Timeout")
    role_jimmy = discord.utils.get(ctx.guild.roles, name="Jimmy")

    async def remove_timeout(seconds):
        await asyncio.sleep(seconds)
        await member.add_roles(role_jimmy)
        await member.remove_roles(role_timeout)

    if is_admin:
        channel = await member.create_dm()
        await member.add_roles(role_timeout)
        await member.remove_roles(role_jimmy)
        if duration[-1] == "D":  # Checking for the days suffix
            duration = duration[:-1]
            timeout_duration = int(duration) * 86400

            if int(duration) == 1:  # Send a message to the user and the channel, singular case
                await ctx.send("{} timed out {} for reason: {}. "
                               "\nLength of timeout: {} day".format(ctx.author, str(member), reason, duration))
                message = "You have been timed out from " + str(ctx.guild) + ". Reason: " + reason \
                          + "\nLength of timeout: " + duration + " day"
                await channel.send(message)
            else:  # Send a message to the user and the channel, plural case
                await ctx.send("{} timed out {} for reason: {}. "
                               "\nLength of timeout: {} days".format(ctx.author, str(member), reason, duration))
                message = "You have been timed out from " + str(ctx.guild) + ". Reason: " + reason \
                          + "\nLength of timeout: " + duration + " days"
                await channel.send(message)

            await remove_timeout(timeout_duration)
            nest_asyncio.apply()

        else:  # Defaults to hours
            timeout_duration = int(duration)*3600
            if int(duration) == 1:  # Sends a message to the user and the channel, singular case
                await ctx.send("{} timed out {} for reason: {}. "
                               "\nLength of timeout: {} hour".format(ctx.author, str(member), reason, duration))
                message = "You have been timed out from " + str(ctx.guild) + ". Reason: " + reason \
                          + "\nLength of timeout: " + duration + " hour"
                await channel.send(message)
            else:  # Sends a message to the user and the channel, plural case
                await ctx.send("{} timed out {} for reason: {}. "
                               "\nLength of timeout: {} hours".format(ctx.author, str(member), reason, duration))
                message = "You have been timed out from " + str(ctx.guild) + ". Reason: " + reason \
                          + "\nLength of timeout: " + duration + " hours"
                await channel.send(message)

            await remove_timeout(timeout_duration)
            nest_asyncio.apply()

        message = "Your timeout from " + str(ctx.guild) + " has been removed"
        await channel.send(message)
    else:
        await ctx.send("Error: The timeout command is for admins only.")


@client.command(pass_context=True)
async def purge(ctx, member: discord.Member, channel: discord.TextChannel, number=1):
    deleted = 0

    if is_admin:
        async for message in channel.history(limit=1000):
            if message.author == member:
                await message.delete()
                deleted += 1
            if deleted >= number:
                break
        await ctx.channel.send("Purged {} messages by {} in {}".format(str(number), member, channel.mention))
    else:
        await ctx.send("Error: The purge command is for admins only.")


@client.command(pass_context=True)
async def kick(ctx, member: discord.Member, reason=""):
    if is_admin:
        await ctx.send("{} kicked {} for reason: {}".format(ctx.author, str(member), reason))
        message = "You have been kicked from " + str(ctx.guild) + ". Reason: " + reason
        channel = await member.create_dm()
        await channel.send(message)
        await member.kick(reason=reason)
    else:
        await ctx.send("Error: The kick command is for admins only.")


@client.command(pass_context=True)
async def temp_ban(ctx, member: discord.Member, duration="", reason=""):
    async def remove_ban(seconds):
        await asyncio.sleep(seconds)
        await channel.send("You have been unbanned from " + str(ctx.guild) + ".")
        await member.unban()

    if is_admin:
        channel = await member.create_dm()
        if duration[-1] == "D":  # Checking for the days suffix
            duration = duration[:-1]
            ban_duration = int(duration)*86400

            if int(duration) == 1:  # Send a message to the user and the channel, singular case
                await ctx.send("{} banned {} for reason: {}. "
                               "\nLength of ban: {} day".format(ctx.author, str(member), reason, duration))
                message = "You have been temporarily banned from " + str(ctx.guild) + ". Reason: " + reason \
                          + "\nLength of ban: " + duration + " day"
                await channel.send(message)
            else:  # Send a message to the user and the channel, plural case
                await ctx.send("{} banned {} for reason: {}. "
                               "\nLength of ban: {} days".format(ctx.author, str(member), reason, duration))
                message = "You have been temporarily banned from " + str(ctx.guild) + ". Reason: " + reason \
                          + "\nLength of ban: " + duration + " days"
                await channel.send(message)
            await member.ban(reason=reason, delete_message_days=0)
            await remove_ban(ban_duration)
            nest_asyncio.apply()

        else:  # Defaults to hours
            ban_duration = int(duration)*3600
            if int(duration) == 1:  # Send a message to the user and the channel, singular case
                await ctx.send("{} banned {} for reason: {}. "
                               "\nLength of ban: {} hour".format(ctx.author, str(member), reason, duration))
                message = "You have been temporarily banned from " + str(ctx.guild) + ". Reason: " + reason \
                          + "\nLength of ban: " + duration + " hour"
                await channel.send(message)
            else:  # Send a message to the user and the channel, plural case
                await ctx.send("{} banned {} for reason: {}. "
                               "\nLength of ban: {} hours".format(ctx.author, str(member), reason, duration))
                message = "You have been temporarily banned from " + str(ctx.guild) + ". Reason: " + reason \
                          + "\nLength of ban: " + duration + " hours"
                await channel.send(message)
            await member.ban(reason=reason, delete_message_days=0)
            await remove_ban(ban_duration)
            nest_asyncio.apply()

    else:
        await ctx.send("Error: The temp ban command is for admins only.")


@client.command(pass_context=True)
async def create_role(ctx, name="", color="255, 255, 255", mentionable=False, hoist=False):
    if is_admin:
        color_tuple = eval(color)
        r = color_tuple[0]
        g = color_tuple[1]
        b = color_tuple[2]
        role_color = discord.Color.from_rgb(r, g, b)
        await ctx.guild.create_role(name=name, color=role_color, mentionable=mentionable, hoist=hoist)
        await ctx.send("Successfully created role {}.".format(name))
    else:
        ctx.send("Error: the create role command is for admins only.")


@client.command(pass_context=True)
async def give_roles(ctx, member: discord.Member, roles=""):
    if is_admin:
        roles_list = []
        roles_tuple = tuple(map(str, roles.split(", ")))
        for role_name in roles_tuple:
            roles_list.append(discord.utils.get(ctx.guild.roles, name=role_name))
        for role in roles_list:
            await member.add_roles(role)
            await ctx.send("Successfully gave role {} to {}".format(str(role), str(member)))
    else:
        ctx.send("Error: the give roles command is for admins only.")


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
        ctx.send("Error: the give roles command is for admins only.")


@client.command(pass_context=True)
async def nick(ctx, member: discord.Member, name=None):
    if is_admin:
        await member.edit(nick=name)
        if name:
            await ctx.send("Successfully changed {}'s nickname to {}".format(str(member), name))
        else:
            await ctx.send("Successfully removed {}'s nickname.".format(str(member)))
    else:
        await ctx.send("Error: the nick command is for admins only")


@client.command(pass_context=True)
async def mass_rename(ctx, name=None, is_prefix=False, is_suffix=False):
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
async def temp_mute(ctx, member: discord.Member, duration=1, reason=""):
    if is_admin:
        await member.edit(mute=True)
        channel = await member.create_dm()

        if duration == 1:
            await channel.send("You have been temporarily muted from {} for {} second. Reason: {}"
                         .format(str(ctx.guild), duration, reason))
            await ctx.send("{} was temporarily muted for {} second. Reason: {}"
                                   .format(member, duration, reason))
        else:
            await channel.send("You have been temporarily muted from {} for {} seconds. Reason: {}"
                               .format(str(ctx.guild), duration, reason))
            await ctx.send("{} was temporarily muted for {} seconds. Reason: {}"
                           .format(member, duration, reason))

        await asyncio.sleep(duration)
        nest_asyncio.apply()
        await member.edit(mute=False)
        await channel.send("You have been unmuted from {}".format(str(ctx.guild)))

    else:
        await ctx.send("Error: The temp mute command is for admins only.")


@client.command(pass_context=True)
async def info(ctx):
    await ctx.send("Splax Bot is the automated minion of the Tesseract Police State, built to boomer standards.")
    embed = discord.Embed(title="Commands", description="All commands require the user's discord name,"
                                                        " not their nickname. Arguments appended by B are boolean "
                                                        "and only accept True or False.", color=0x00ff00)
    embed.add_field(name="info", value="Lists the commands offered by the bot"
                                       "\nSyntax: !info", inline=False)
    embed.add_field(name="quote", value="Displays the specified quote. Chooses a random quote if no quote is specified."
                                        "\nSyntax: !quote [number]", inline=False)
    embed.add_field(name="join_channel", value="Joins a password protected channel."
                                               "\nSyntax: !join_channel [channel] [password]")
    embed.add_field(name="timeout (admin only)", value="Times out a user and sends them a DM with the reason. "
                                                       "Duration is in hours by default, days if appended by D."
                                                       "\nSyntax: !timeout [user] [duration] [reason]", inline=False)
    embed.add_field(name="purge (admin only)", value="Deletes the last N messages by a user in a specified channel."
                                                     "\nSyntax: !purge [user] [channel] [number]", inline=False)
    embed.add_field(name="kick (admin only)", value="Kicks a user and sends them a DM with the reason."
                                                    "\nSyntax: !kick [user] [reason]", inline=False)
    embed.add_field(name="temp_ban (admin only)", value="Temporarily bans a user and sends them a DM with the reason. "
                                                       "Duration is in hours by default, days if appended by D."
                                                   "\nSyntax: !tempban [user] [duration] [reason]", inline=False)
    embed.add_field(name="create_role (admin only)", value="Creates a role with the specified properties."
                                                           "\nSyntax: !create_role [name] [R, G, B] "
                                                           "[mentionable]B [hoisted]B", inline=False)
    embed.add_field(name="give_roles (admin only)", value="Gives roles to a user."
                                                          "\nSyntax: !give_roles [user] [roles]", inline=False)
    embed.add_field(name="remove_roles (admin only)", value="Removes roles from a user."
                                                          "\nSyntax: !remove_roles [user] [roles]", inline=False)
    embed.add_field(name="nick (admin only)", value="Sets a user's nickname. Removes nickname if no name is provided."
                                                    "\nSyntax: !nick [user] [name]", inline=False)
    embed.add_field(name="mass_rename (admin only)", value="Mass renames every user on the server, removes nicknames "
                                                           "if no name is provided. Use with caution."
                                                           "\nSyntax: !mass_rename [name] [is_prefix]B [is_suffix]B",
                    inline=False)
    embed.add_field(name="temp_mute (admin only)", value="Temporarily mutes a user and sends them a DM with the reason."
                                                         "\nSyntax: !temp_mute [user] [duration] [reason]")
    await ctx.send(embed=embed)


client.run(token)
