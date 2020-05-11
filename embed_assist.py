import discord
import time
from server_count import get_server_count


# Server class creates an embed to be updated with the status of a Minecraft server
class Server:
    def __init__(self, name, ip, version):
        self.name = name
        self.ip = ip
        self.version = version

    def get_server_embed(self):
        current_time = time.strftime("%b %d, %Y, %H:%M:%S EST")
        time_string = "Last Updated: {}".format(current_time)

        description = "IP: {} ({})".format(self.ip, self.version)
        server_embed = discord.Embed(title=self.name, description=description)
        players_online = get_server_count(self.ip)

        if players_online == -1:
            server_embed.add_field(name="Players Online:", value="Can't reach server")
        else:
            server_embed.add_field(name="Players Online:", value=players_online)

        server_embed.set_footer(text=time_string)
        return server_embed


def get_info_embed():
    embed = discord.Embed(title="Commands", description="All commands require the user's discord name, "
                                                        "not their nickname. Reasons should be in quotes, "
                                                        "or they won't work properly.", color=0x00ff00)
    embed.add_field(name="info", value="Lists the commands offered by the bot"
                                       "\nSyntax: !info", inline=False)
    embed.add_field(name="quote", value="Displays the specified quote. Chooses a random quote if no quote is specified."
                                        "\nSyntax: !quote [number]", inline=False)
    embed.add_field(name="timeout (admin only)", value="Times out a user and sends them a DM with the reason. "
                                                       "Duration is in hours.."
                                                       "\nSyntax: !timeout [user] [duration] [reason]", inline=False)
    embed.add_field(name="purge (admin only)", value="Deletes the last N messages by a user in a specified channel."
                                                     "\nSyntax: !purge [user] [channel] [number]", inline=False)
    embed.add_field(name="kick (admin only)", value="Kicks a user and sends them a DM with the reason."
                                                    "\nSyntax: !kick [user] [reason]", inline=False)
    embed.add_field(name="temp_ban (admin only)", value="Temporarily bans a user and sends them a DM with the reason. "
                                                        "Duration is in hours."
                                                        "\nSyntax: !tempban [user] [duration] [reason]", inline=False)
    embed.add_field(name="create_role (admin only)", value="Creates a role with the specified properties."
                                                           "\nSyntax: !create_role [name] [R, G, B] "
                                                           "[mentionable] [hoisted]", inline=False)
    embed.add_field(name="edit_role (admin only)", value="Edits a role to have the specified properties."
                                                         "\nSyntax: !edit_role [name] [position] "
                                                         "[mentionable] [hoisted] [R, G, B] (optional)", inline=False)
    embed.add_field(name="give_roles (admin only)", value="Gives roles to a user."
                                                          "\nSyntax: !give_roles [user] [roles]", inline=False)
    embed.add_field(name="remove_roles (admin only)", value="Removes roles from a user."
                                                            "\nSyntax: !remove_roles [user] [roles]", inline=False)
    embed.add_field(name="nick (admin only)", value="Sets a user's nickname. Removes nickname if no name is provided."
                                                    "\nSyntax: !nick [user] [name]", inline=False)
    embed.add_field(name="mass_rename (admin only)", value="Mass renames every user on the server, removes nicknames "
                                                           "if no name is provided. Use with caution."
                                                           "\nSyntax: !mass_rename [name] [is_prefix] [is_suffix]",
                    inline=False)
    embed.add_field(name="mute (admin only)", value="Temporarily mutes a user and sends them a DM with the reason."
                                                    " Duration is in minutes."
                                                    "\nSyntax: !temp_mute [user] [duration] [reason]",
                    inline=False)
    return embed
