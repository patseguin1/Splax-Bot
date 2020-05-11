import discord


class Timeout:
    def __init__(self, guild: discord.Guild, author: discord.Member,
                 member: discord.Member, duration, reason):
        self.guild = guild
        self.author = author
        self.member = member
        self.duration = duration
        self.reason = reason

    def get_mod_channel_string(self):
        if self.duration == 1:
            mod_channel_string = "{} timed out {} for reason: {}. \nLength of timeout: {} hour"\
                .format(self.author, self.member, self.reason, self.duration)
            return mod_channel_string
        else:
            mod_channel_string = "{} timed out {} for reason: {}. \nLength of timeout: {} hours"\
                .format(self.author, self.member, self.reason, self.duration)
            return mod_channel_string

    def get_user_dm_string(self):
        if self.duration == 1:
            user_dm_string = "You have been timed out from {}. Reason: {} \nLength of timeout: {} hour."\
                .format(self.guild, self.reason, self.duration)
            return user_dm_string
        else:
            user_dm_string = "You have been timed out from {}. Reason: {} \nLength of timeout: {} hours."\
                .format(self.guild, self.reason, self.duration)
            return user_dm_string


class Ban:
    def __init__(self, guild: discord.Guild, author: discord.Member,
                 member: discord.Member, duration, reason):
        self.guild = guild
        self.author = author
        self.member = member
        self.duration = duration
        self.reason = reason

    def get_mod_channel_string(self):
        if self.duration == 1:
            mod_channel_string = "{} banned {} for reason: {}. \nLength of ban: {} hour"\
                .format(self.author, self.member, self.reason, self.duration)
            return mod_channel_string
        else:
            mod_channel_string = "{} banned {} for reason: {}. Length of ban: {} hours"\
                .format(self.author, self.member, self.reason, self.duration)
            return mod_channel_string

    def get_user_dm_string(self):
        if self.duration == 1:
            user_dm_string = "You have been banned from {}. Reason: {} \nLength of ban: {} hour."\
                .format(self.guild, self.reason, self.duration)
            return user_dm_string
        else:
            user_dm_string = "You have been banned from {}. Reason: {} \nLength of ban: {} hours."\
                .format(self.guild, self.reason, self.duration)
            return user_dm_string
