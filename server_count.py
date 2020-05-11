from mcstatus import MinecraftServer


def get_server_count(server):
    minecraft_server = MinecraftServer.lookup(server)
    try:
        server_status = minecraft_server.status()
        return server_status.players.online
    except:
        return -1