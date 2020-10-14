import discord

#Check whether the user can actually use the specified command
def userHasPermission(user: discord.Member, command: str, botSettings, cmdRanks):
    roles = user.roles
    neededRole = botSettings["checkRole"]

    if command in cmdRanks["lowerRank"]:
        return True

    for role in roles:
        if role.name == neededRole:
            return True
    return False

#Check whether the message was sent in the correct channel and with proper checkSign
def validContext(message: discord.Message, settings):
    if message.content.find(settings["checkSign"]) != 0:
        return False
    if message.channel.name != settings["standardChannel"]:
        return False
    return True

#Check whether the given command is one included in the bot
def validCommand(command: str, cmdRanks):
    for key,item in cmdRanks:
        if command in item.values():
            return True
    return False

#Convert the string to a list of strings for better argument handling
def asList(message: str, settings):
    checkSign = settings["checkSign"]

    parts = message.split(" ")
    parts[0].replace(checkSign,"",1)
    
    return parts
