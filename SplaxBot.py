import discord
from discord.ext.commands import Bot
import asyncio
import nest_asyncio
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = Bot(command_prefix="!")
with open("bad_words.txt") as file:
    bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----')


@client.command(pass_context=True)
async def test(ctx):
    await ctx.send("This is a test")


@client.command(pass_context=True)
async def timeout(ctx, member: discord.Member, duration="", reason=""):
    admin = discord.utils.get(ctx.guild.roles, id=491335846335610891)
    mod = discord.utils.get(ctx.guild.roles, id=381807012352229377)
    role_timeout = discord.utils.get(ctx.guild.roles, name="Timeout")
    role_jimmy = discord.utils.get(ctx.guild.roles, name="Jimmy")

    async def remove_timeout(seconds):
        await asyncio.sleep(seconds)
        await member.add_roles(role_jimmy)
        await member.remove_roles(role_timeout)

    if admin or mod in ctx.author.roles:
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
    admin = discord.utils.get(ctx.guild.roles, id=491335846335610891)
    mod = discord.utils.get(ctx.guild.roles, id=381807012352229377)
    if admin or mod in ctx.author.roles:
        def by_member(message):
            return message.author == member

        deleted = await channel.purge(limit=number, check=by_member)
        await ctx.channel.send("Deleted {} messages by {}".format(len(deleted), member))
    else:
        await ctx.send("Error: The purge command is for admins only.")


@client.command(pass_context=True)
async def kick(ctx, member: discord.Member, reason=""):
    admin = discord.utils.get(ctx.guild.roles, id=491335846335610891)
    mod = discord.utils.get(ctx.guild.roles, id=381807012352229377)
    if admin or mod in ctx.author.roles:
        await ctx.send("{} kicked {} for reason: {}".format(ctx.author, str(member), reason))
        message = "You have been kicked from " + str(ctx.guild) + ". Reason: " + reason
        channel = await member.create_dm()
        await channel.send(message)
        await member.kick(reason=reason)
    else:
        await ctx.send("Error: The kick command is for admins only.")


@client.command(pass_context=True)
async def tempban(ctx, member: discord.Member, duration="", reason=""):
    admin = discord.utils.get(ctx.guild.roles, id=491335846335610891)
    mod = discord.utils.get(ctx.guild.roles, id=381807012352229377)

    async def remove_ban(seconds):
        await asyncio.sleep(seconds)
        await channel.send("You have been unbanned from " + str(ctx.guild) + ".")
        await member.unban()

    if admin or mod in ctx.author.roles:
        channel = await member.create_dm()
        if duration[-1] == "D": # Checking for the days suffix
            duration = duration[:-1]
            ban_duration = int(duration)*86400

            if int(duration) == 1:  # Send a message to the user and the channel, singular case
                await ctx.send("{} banned {} for reason: {}. "
                               "\nLength of ban: {} day".format(ctx.author, str(member), reason, duration))
                message = "You have been banned from " + str(ctx.guild) + ". Reason: " + reason \
                          + "\nLength of ban: " + duration + " day"
                await channel.send(message)
            else:  # Send a message to the user and the channel, plural case
                await ctx.send("{} banned {} for reason: {}. "
                               "\nLength of ban: {} days".format(ctx.author, str(member), reason, duration))
                message = "You have been banned from " + str(ctx.guild) + ". Reason: " + reason \
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
                message = "You have been banned from " + str(ctx.guild) + ". Reason: " + reason \
                          + "\nLength of ban: " + duration + " hour"
                await channel.send(message)
            else:  # Send a message to the user and the channel, plural case
                await ctx.send("{} banned {} for reason: {}. "
                               "\nLength of ban: {} hours".format(ctx.author, str(member), reason, duration))
                message = "You have been banned from " + str(ctx.guild) + ". Reason: " + reason \
                          + "\nLength of ban: " + duration + " hours"
                await channel.send(message)
            await member.ban(reason=reason, delete_message_days=0)
            await remove_ban(ban_duration)
            nest_asyncio.apply()

    else:
        await ctx.send("Error: The ban command is for admins only.")


@client.command(pass_context=True)
async def info(ctx):
    await ctx.send("Splax Bot is a bot to help automate some moderation tasks. Written with the discord.py library.")
    embed = discord.Embed(title="Commands", description="All commands require the user's discord name,"
                                                        " not their nickname.", color=0x00ff00)
    embed.add_field(name="timeout (admin only)", value="Times out a user and sends them a DM with the reason."
                                                       "\nSyntax: !timeout [user] [duration] [reason]", inline=False)
    embed.add_field(name="purge (admin only)", value="Searches through the last N messages in a channel to delete by a "
                                                     "specified user."
                                                     "\nSyntax: !purge [user] [channel] [number]", inline=False)
    embed.add_field(name="kick (admin only)", value="Kicks a user and sends them a DM with the reason."
                                                    "\nSyntax: !kick [user] [reason]", inline=False)
    embed.add_field(name="tempban (admin only)", value="Temporarily bans a user and sends them a DM with the reason. "
                                                       "Duration is in hours by default, days if appended by D."
                                                   "\nSyntax: !tempban [user] [duration] [reason]", inline=False)
    embed.add_field(name="info", value="Lists the commands offered by the bot"
                                       "\nSyntax: !info", inline=False)

    await ctx.send(embed=embed)


@client.event
async def on_message(message):
    message_content = message.content.strip().lower()
    mod_channel = client.get_channel(644010198662643712)
    if any(bad_word in message_content for bad_word in bad_words):
        await mod_channel.send(f"{message.author.mention} "
                                   "was caught saying a bad word in #" + str(message.channel) +
                               ". Their message has been censored.")
        await message.delete()
        print("Deleted 1 message by {} in #{}".format(message.author, message.channel))
    await client.process_commands(message)

client.run(token)
