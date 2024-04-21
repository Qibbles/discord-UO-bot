#################
### Changelog ###
#################
# 2.1 - Added timer for lich khan and arch demon with sleep
# 2.2 (1/6/18) - Added hardcodes for manual setting of timer
# 2.2.1 (2/6/18) - Reformatted status reporting and added Adramalech
# 2.3 (3/6/18) - Added MOTM
# 2.4 (3/6/18) - Added Help file
# 2.4.1 (3/6/18) - Formating of help text
# 2.4.2 (4/6/18) - Adding author checks
# 2.5 (5/6/18) - Rewrite of code to allow parameters
# 2.6 (5/6) - Arguments for dynamic manual offset
# 2.6.1 (6/6) - Rewrote MOTM codes
# 2.7 (7/6) - Added time query
# 2.8 (7/6) - Event scheduler
# 2.8.1 (8/6) - Logic to separate ready champs
# 2.9 (9/6) - Player point system
# 2.9.1 (10/6) - Player point system code cleanup
# 2.9.2 (12/6) - Added class for Champ timers to clean up code
# 2.9.3 (12/6) - Added class for Status to clean up code
    # Consider using decorators for db update and playerScore functions
# 2.9.4 (15/6/18) - Added Champs Ready
# 2.9.5 (16/6/18) - Added points awarded announcement
# 2.10 (21/6/18) - Event '#list'
    # Consider adding '#event join'
# 2.10.1 (3/7/18) - Added roles ID variables
# 2.11 (12/7/18) - Added checked timer for champs

import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform
from datetime import datetime, timedelta
import sqlite3

# Here you can modify the bot's prefix and description and wether it sends help in direct messages or not.
client = Bot(description="Kibble's Champ Timer Bot by Kibbles#9429", command_prefix="", pm_help=False)

# This is what happens everytime the bot launches. In this case, it prints information like server count, user count the bot is connected to, and the bot id in the console.
# Do not mess with it because the bot can break, if you wish to do so, please consult me or someone trusted.

prefix = '#'

guild = "N Guild"

# Channel IDs
normal = ''
secret = ''
main = ''

# Role IDs
owner = ''
leader = ['', '']
member = ''

# Banned IDs
banned = ['', '']

############################
### SQLite db statements ###
############################
# Establish connection
conn = sqlite3.connect('champtimer.db')
c = conn.cursor()

# Create the table if it doesn't exist and initialize data
def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS champs (name TEXT, status TEXT, time REAL, checked REAL)')
    c.execute('SELECT COUNT(*) FROM champs')
    count = c.fetchall()
    if count[0][0] == 0:
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Abyss', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Covetous', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Deceit', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Despise', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Destard', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Fafnir', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Orc', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Shame', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Terathan', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Wrong', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Akor', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Arch Demon', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Adramalech', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Fafnir', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Lich Khan', 'Unknown', 0, 0)")
        c.execute("INSERT INTO champs (name, status, time) VALUES ('Warlock', 'Unknown', 0, 0)")

    c.execute('CREATE TABLE IF NOT EXISTS points (name TEXT, points INT, up INT, down INT)')
    c.execute('CREATE TABLE IF NOT EXISTS event (eventID INTEGER PRIMARY KEY AUTOINCREMENT, organizer TEXT, eventTime REAL, eventTitle TEXT)')

    conn.commit()

# Event module
def createEvent(organizer, eventTime, eventTitle):
    c.execute("INSERT INTO event (organizer, eventTime, eventTitle) VALUES (?, ?, ?)", (organizer, eventTime, eventTitle))
    conn.commit()
    
def getEvent(eventID):
    if eventID == 0:
        c.execute("SELECT * FROM event ORDER BY eventTime ASC")
        select = c.fetchall()
    else:
        c.execute("SELECT * FROM event WHERE eventID = (?)", (eventID,))
        select = c.fetchone()
    return select

# Timer module
def update(champ, champstatus, champtime, check):
    c.execute("UPDATE champs SET status = (?), time = (?), checked = (?) WHERE name = (?)", (champstatus, champtime, check, champ))
    conn.commit()

def retrieve(champ):
    c.execute("SELECT * FROM champs WHERE name = (?)", (champ,))
    select = c.fetchall()
    return select

# Points module 
def givePoints(player, points, up, down):
    c.execute("UPDATE points SET points = (?), up = (?), down = (?) WHERE name = (?)", (points, up, down, player))
    conn.commit()

def getPoints(player):
    c.execute("SELECT * FROM points WHERE name = (?)", (player,))
    select = c.fetchone()
    return select

def createPoints(player, points, up, down):
    c.execute("INSERT INTO points (name, points, up, down) VALUES (?, ?, ?, ?)", (player, points, up, down))
    conn.commit()

create_table()

@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + ' (ID:' + client.user.id + ') | Connected to ' + str(
        len(client.servers)) + ' servers | Connected to ' + str(len(set(client.get_all_members()))) + ' users')
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__,
                                                                               platform.python_version()))
    print('--------')
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    print('--------')
    print("You are running Kibble's Champ Timer Bot version 2.9.1")
    print('Created by Kibbles#9429')

    await client.change_presence(game=discord.Game(name='with Kibbles...'))
    
@client.event
async def on_message(message):

    ####################
    ### Broadcasting ###
    ####################
    if prefix + 'bc' in message.content.lower():
    #if authorRole == 'owner' or authorRole == 'leader':
        bcItem = message.content.split(" ")
        await client.send_message(client.get_channel(main), "%s" % (" ".join(bcItem[1:])))
    #else:
    #    await client.send(message.author, "You do not have sufficient priviledges to make a broadcast!")

    ##########
    # help ###
    ##########
    if prefix + '도움' in message.content.lower():
        await client.send_message(message.author, "여러분의 짱친절한 베프 **" + guild + "** 봇이 왓어요!")
        await asyncio.sleep(2)
        helpMsg = '```ini' + '\n'
        helpMsg += '제가 지금 수행하는 4가지 일은:' + '\n'
        helpMsg += '---------------------------------------------' + '\n'
        helpMsg += '1. 챔, 던전 그리고 보스 타이머를 갱신하고 알려드립니다!' + '\n'
        helpMsg += '2. 현재 열리거나 닫힌 챔들의 실황을 알려드려요!' + '\n'
        helpMsg += '3. 달몹에 대한 정보도 드려요!' + '\n'
        helpMsg += '4. 키블 주인님의 차 심부름은 덤 ㅠㅠ' + '\n'
        helpMsg += '' + '\n' + '\n'
        helpMsg += '가능한 명령어는:' + '\n'
        helpMsg += '---------------------------' + '\n'
        helpMsg += '- 챔이나 보스 업이나 다운 시 [# + (챔 이나 보스 이름 / 위치) + 업 / 다운] 을 입력하세요' + '\n'
        helpMsg += '- 모든 현황을 보시려면  [#status 나 #상황] 을 입력하세요.' + '\n'
        helpMsg += '- 달몹이 무엇인지 알고 싶으시면 [#motm] 을,' + '\n'
        helpMsg += '- 특정 달의 달몹을 알고 싶으시면 [#motm + (달을 3글자로)] 입력하세요.' + '\n'
        helpMsg += '```'
        await client.send_message(message.author, helpMsg)
        await asyncio.sleep(2)
        await client.send_message(message.author, "개선할 점에 대해 질문이나 피드백이 있으면 주저하지 말고 키블(Kibbles)에게 메시지를 주시고 **" + guild + "** 에서 즐온하시길 바래요!")
        
    if prefix + 'help' in message.content.lower():
        helpMsg = "Welcome to **" + guild + "'s** friendliest neighbourhood bot! For Korean help, please type __#도움말__"
        helpMsg += '```ini' + '\n'
        helpMsg += '-------------------' + '\n'
        helpMsg += 'AVAILABLE COMMANDS:' + '\n'
        helpMsg += '-------------------' + '\n'
        helpMsg += '\n'
        helpMsg += '---------------' + '\n'
        helpMsg += 'Champs & Bosses' + '\n'
        helpMsg += '---------------' + '\n'
        helpMsg += '- To report a Champ or Boss spawn or death, type [#(champ or boss location) + up/down]. For example: [#abyss up].' + '\n'
        helpMsg += '- To manually set the time on death of a Champ, type [#(champ or boss name/location) + (number of minutes ago)]. For example: to report Abyss killed 1 hour 11 minutes ago (71 minutes), type [#abyss 71].' + '\n'
        helpMsg += '- If a boss is not ready to spawn, you may report the time you last checked it with [#(champ location) + check]. For example: [#abyss check].' + '\n'
        helpMsg += '- For a full status board, type [#status].' + '\n'
        helpMsg += '\n'
        helpMsg += '-------------' + '\n'
        helpMsg += 'POINTS SYSTEM' + '\n'
        helpMsg += '-------------' + '\n'
        helpMsg += '- Points are awarded for reporting Champs Up/Down (Up = 20 points, Down = 10 points). To check your current score, type [#points]' + '\n'
        helpMsg += '\n'
        helpMsg += '----' + '\n'
        helpMsg += 'MOTM' + '\n'
        helpMsg += '----' + '\n'
        helpMsg += '- For curent Month\'s MOTM, type [#motm] for the current Month\'s Monster or,' + '\n'
        helpMsg += '- For a specific Month\'s, type [#motm + (3 letter month)] for specific Month\'s Monster. For example: to check the MOTM for October, type [#motm oct].' + '\n'
        helpMsg += '\n'
        helpMsg += '---------------' + '\n'
        helpMsg += 'Event Scheduler' + '\n'
        helpMsg += '---------------' + '\n'
        helpMsg += '- To create an event, type - [#event (number of minutes later the event will begin) (event title)]. For example: [#event no-cut-pvp 2] (To set an event for "no cut pvp" 2 hours later).' + '\n'
        helpMsg += '- To delete an event (for event organizer only), type - [#delete (event ID)]. For example: [#delete 7] To delete an \
        D 7. To view a list of event IDs, refer to command below.' + '\n'
        helpMsg += '- To view a list of all upcoming events, type - [#list]' + '\n'
        helpMsg += '\n'
        helpMsg += '---------------' + '\n'
        helpMsg += 'Timezone Module' + '\n'
        helpMsg += '---------------' + '\n'
        helpMsg += '- To check the current time in different timezones, type [#time]' + '\n'
        helpMsg += '- To check what the time will be in N number of hours later, type [#time (number of hours)]. For example: [#time 10]' + '\n'
        helpMsg += '\n'
        #if authorRole == 'owner':
        #    helpMsg += '-------------------' + '\n'
        #    helpMsg += 'Leadership Commands' + '\n'
        #    helpMsg += '-------------------' + '\n'
        #    helpMsg += 'As a leader of the guild, you have access to these additional commands!' + '\n'
        #    helpMsg += '\n'
        #    helpMsg += '- To make a broadcast to general chatroom, tpe [#bc (your message)]. For example: [#bc @everyone Join voice channel!]' + '\n'
        #    helpMsg += '- To reset the player scoreboard, type [#reset]' + '\n'
        helpMsg += '```'
        helpMsg += "If you have any questions or feedbacks on how I might improve, please feel free to drop **Kibbles** a message and I hope you enjoy your stay here at **" + guild + "**."
        await client.send_message(message.author, helpMsg)

    authorRole = ''
    if member in [role.id for role in message.author.roles]:
        authorRole = 'member'
    elif message.author.id in owner:
        authorRole = 'owner'
    for id in leader:
        if id in [role.id for role in message.author.roles]:
            authorRole = 'leader'
    if message.author.id in banned:
        authorRole = 'banned'
    #if message.author.id == owner or leader in [role.id for role in message.author.roles] or member in [role.id for role in message.author.roles] and message.author.id not in banned:
    
    if authorRole != '' and authorRole != 'banned':
        if not message.author.bot:
            FMT = '%H:%M:%S'
    
    
            ################
            ### Time now ###
            ################
            if prefix + 'time' in message.content.lower() or prefix + "시간" in message.content.lower():
                timeItem = message.content.lower().split(" ")
                timeNow = datetime.utcnow().replace(microsecond=0)
                serverTime = timeNow - timedelta(hours=5)
                estTime = timeNow - timedelta(hours=4)
                cestTime = timeNow + timedelta(hours=2)
                sgTime = timeNow + timedelta(hours=8)
                koreaTime = timeNow + timedelta(hours=9)
                russiaTime = timeNow + timedelta(hours=3)
                if len(timeItem) <= 1:
                    timeMsg = 'The time now is:' + '\n'
                    timeMsg += '```ml' + '\n'
                    timeMsg += 'UTC (+0):' + str(timeNow) + '\n'
                    timeMsg += '\n'
                    timeMsg += 'Game Server Time (-5): ' + str(serverTime) + '\n'
                    timeMsg += 'US EST (-4): ' + str(estTime) + '\n'
                    timeMsg += 'CEST (+2): ' + str(cestTime) + '\n'
                    timeMsg += 'Russia, Moscow (+3): ' + str(russiaTime) + '\n'
                    timeMsg += 'Hong Kong / Singapore (+8): ' + str(sgTime) + '\n'
                    timeMsg += 'South Korea (+9): ' + str(koreaTime) + '\n'
                    timeMsg += '```'
                else:
                    timeOffset = int(timeItem[1])
                    timeNow += timedelta(hours=timeOffset)
                    serverTime += timedelta(hours=timeOffset)
                    estTime += timedelta(hours=timeOffset)
                    cestTime += timedelta(hours=timeOffset)
                    sgTime += timedelta(hours=timeOffset)
                    koreaTime += timedelta(hours=timeOffset)
                    russiaTime += timedelta(hours=timeOffset)
                    timeMsg = 'The time in __**' + str(timeOffset) + ' hours**__ is:' + '\n'
                    timeMsg += '```ml' + '\n'
                    timeMsg += 'UTC (+0):' + str(timeNow) + '\n'
                    timeMsg += '\n'
                    timeMsg += 'Server Time (-5): ' + str(serverTime) + '\n'
                    timeMsg += 'US EST (-4): ' + str(estTime) + '\n'
                    timeMsg += 'CEST (+2): ' + str(cestTime) + '\n'
                    timeMsg += 'Russia, Moscow (+3): ' + str(russiaTime) + '\n'
                    timeMsg += 'Hong Kong / Singapore (+8): ' + str(sgTime) + '\n'
                    timeMsg += 'South Korea (+9): ' + str(koreaTime) + '\n'
                    timeMsg += '```'
    
                await client.send_message(message.channel, timeMsg)
            
            #######################
            ### Event Scheduler ###
            #######################
            if prefix + 'event' in message.content.lower():
                eventItem = message.content.split(" ")
                eventOffset = int(eventItem[1])
                eventOffsetSeconds = eventOffset * 60
                eventTime = datetime.utcnow().replace(microsecond=0) + timedelta(minutes=eventOffset)
                eventType = str(" ".join(eventItem[2:]))
                eventOrganizer = str(message.author)
                createEvent(eventOrganizer, eventTime, eventType)
                await client.send_message(message.channel, '@everyone ' + eventOrganizer + ' scheduled an event __' + eventType + '__ at __' + str(eventTime) + '(UTC)__ **(' + str(eventOffset) + ' minutes later)**')
                if (eventOffsetSeconds - 7200) > 0:
                    await asyncio.sleep(eventOffsetSeconds - 3600)
                    await client.send_message(message.channel, '@everyone ' +
                                              eventType + ' organized by ' + eventOrganizer + ' will begin in __**2 hours**__!')
                elif (eventOffsetSeconds - 3600) > 0:
                    await asyncio.sleep(eventOffsetSeconds - 3600)
                    await client.send_message(message.channel, '@everyone ' +
                                              eventType + ' organized by ' + eventOrganizer + ' will begin in __**1 hour**__!')
                elif (eventOffsetSeconds - 600) > 0:
                    await asyncio.sleep(eventOffsetSeconds - 600)
                    await client.send_message(message.channel, '@everyone ' +
                                              eventType + ' organized by ' + eventOrganizer + ' will begin in __**10 minutes**__!')
                await asyncio.sleep(eventOffsetSeconds)
                await client.send_message(message.channel, '@everyone ' + eventType
                                          + ' organized by ' + eventOrganizer + ' __**commences now**__!')
    
            if prefix + 'list' in message.content.lower():
                currentTime = datetime.utcnow().replace(microsecond=0)
                eventList = getEvent(0)
                eventMsg = '```ini' + '\n'
                eventMsg += 'Upcoming Event List:' + '\n'
                eventMsg += '\n'
                eventMsg += '[ Event ID | Organizer | Date & Time (UTC) | Title ]' + '\n'
                eventMsg += '\n'
                for row in eventList:
                    eventTime = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
                    timeDiff = eventTime - currentTime
                    hours, remainder = divmod(timeDiff.total_seconds(), 3600)
                    minutes, remainder = divmod(remainder, 60)
                    timeUntil = " (%s Hours %s Minutes Later) " % (round(hours), round(minutes))
                    if currentTime < eventTime:
                        eventMsg += '[ ' + str(row[0]) + ' | ' + str(row[1]) + ' | ' + str(row[2]) + str(timeUntil) + ' | ' + str(row[3]) + ' ]' + '\n'
                        eventMsg += '\n'
                eventMsg += '```'                    
                await client.send_message(message.channel, eventMsg)
    
            if prefix + 'delete' in message.content.lower():
                msgObj = message.content.lower().split(" ")
                print(msgObj[1])
                eventItem = getEvent(msgObj[1]) 
                if str(message.author) == eventItem[1] or message.author.id == owner or leader in [role.id for role in message.author.roles]:
                    c.execute("DELETE FROM event WHERE eventID = (?)", (msgObj[1],))
                    conn.commit()
                    await client.send_message(message.channel, str(message.author) + " has cancelled event ID __**# " + str(msgObj[1]) + '**__.')
                else:
                    await client.send_message(message.channel, "You do not have sufficient priviledges to delete that event")
    
            ############
            ### MOTM ###
            ############
            if prefix + 'motm' in message.content.lower():
                month = message.content.lower().split(" ")
                if len(month) <= 1:
                    currentMonth = datetime.now().month
                    # Month Messages
                    if currentMonth == 1:
                        motmMsg = 'The Monster-of-the-Month for January are Snow Elementals **__(Elemental Ban)__**.' + '\n'
                        motmMsg += 'They drop Besotted items (Hue 1986) and "Yeti" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452666886178471956/unknown.png'
                        await client.send_message(message.channel, motmMsg)
                        
                    if currentMonth == 2:
                        motmMsg = 'The Monster-of-the-Month for Feburary are Ogre Lords **__(Repond)__**.' + '\n'
                        motmMsg += 'They drop Fetid items (Hue 2514) and "The Foul" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452673710080393236/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if currentMonth == 3:
                        motmMsg = 'The Monster-of-the-Month for March are Lizardmen **__(Reptilian Death)__**.' + '\n'
                        motmMsg += 'They drop Hue 2527 items and "Herpetologist" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674089459646464/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if currentMonth == 4:
                        motmMsg = 'The Monster-of-the-Month for April are Liches **__(Silver)__**.' + '\n'
                        motmMsg += 'They drop Forsaken Tears items (Hue 1366) and "The Crier" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674429785210880/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if currentMonth == 5:
                        motmMsg = 'The Monster-of-the-Month for May are Balrons **__(Exorcism)__**.' + '\n'
                        motmMsg += 'They drop Hue 1771 items (Hue 1986) and "Hallowed" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674607669968917/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if currentMonth == 6:
                        motmMsg = 'The Monster-of-the-Month for June are Elder Gazers __(No Slayer Types)__**.' + '\n'
                        motmMsg += 'They drop Hue 1978 Cloth and "Visionary" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674692466343947/unknown.png' + '\n'
                        await client.send_message(message.channel, motmMsg)
    
                    if currentMonth == 7:
                        motmMsg = 'The Monster-of-the-Month for July are Daemons **__(Exorcism)__**.' + '\n'
                        motmMsg += 'They drop Hue 1982 items and "Infernal" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674756383211531/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if currentMonth == 8:
                        motmMsg = 'The Monster-of-the-Month for August are Vampires **__(Silver)__**.' + '\n'
                        motmMsg += 'They drop Hue 2622 items.' + '\n'
                        motmMsg += 'https://puu.sh/xhoYq/12a1d98837.png'
                        await client.send_message(message.channel, motmMsg)

                    if currentMonth == 9:
                        motmMsg = 'The Monster-of-the-Month for September are Ettins **__(Repond)__**.' + '\n'
                        motmMsg += 'They drop Hue 2519 items and "Ettin Greaser" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674882317189120/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if currentMonth == 10:
                        motmMsg = 'The Monster-of-the-Month for October are Earth Elementals **__(Elemental Ban)__**.' + '\n'
                        motmMsg += 'They drop Hue 2708 items and "Mud Dauber" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674932225343490/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if currentMonth == 11:
                        motmMsg = 'The Monster-of-the-Month for November are Terathan Warriors **__(Arachnid Doom)__**.' + '\n'
                        motmMsg += 'They drop Hue 2709 items and "Spider Stomper" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674981042585600/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if currentMonth == 12:
                        motmMsg = 'The Monster-of-the-Month for December are Ratmen **__(Repond)__**.' + '\n'
                        motmMsg += 'They drop Hue 1932 items and "Splintered" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452675036487352335/unknown.png'
                        await client.send_message(message.channel, motmMsg)
                else:
                    if month[1] == "jan":
                        motmMsg = 'The Monster-of-the-Month for January are Snow Elementals **__(Elemental Ban)__**.' + '\n'
                        motmMsg += 'They drop Besotted items (Hue 1986) and "Yeti" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452666886178471956/unknown.png'
                        await client.send_message(message.channel, motmMsg)
                        
                    if month[1] == "feb":
                        motmMsg = 'The Monster-of-the-Month for Feburary are Ogre Lords **__(Repond)__**.' + '\n'
                        motmMsg += 'They drop Fetid items (Hue 2514) and "The Foul" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452673710080393236/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if month[1] == "mar":
                        motmMsg = 'The Monster-of-the-Month for March are Lizardmen **__(Reptilian Death)__**.' + '\n'
                        motmMsg += 'They drop Hue 2527 items and "Herpetologist" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674089459646464/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if month[1] == "apr":
                        motmMsg = 'The Monster-of-the-Month for April are Liches **__(Silver)__**.' + '\n'
                        motmMsg += 'They drop Forsaken Tears items (Hue 1366) and "The Crier" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674429785210880/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if month[1] == "may":
                        motmMsg = 'The Monster-of-the-Month for May are Balrons **__(Exorcism)__**.' + '\n'
                        motmMsg += 'They drop Hue 1771 items (Hue 1986) and "Hallowed" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674607669968917/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if month[1] == "jun":
                        motmMsg = 'The Monster-of-the-Month for June are Elder Gazers **__(No Slayer Types)__**.' + '\n'
                        motmMsg += 'They drop Hue 1978 Cloth and "Visionary" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674692466343947/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if month[1] == "jul":
                        motmMsg = 'The Monster-of-the-Month for July are Daemons **__(Exorcism)__**.' + '\n'
                        motmMsg += 'They drop Infernal items (Hue 1982) and "Infernal" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674756383211531/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if month[1] == "aug":
                        motmMsg = 'The Monster-of-the-Month for August are Vampires **__(Silver)__**.' + '\n'
                        motmMsg += 'They drop Suckered items (Hue 2622).' + '\n'
                        motmMsg += 'https://puu.sh/xhoYq/12a1d98837.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if month[1] == "sep":
                        motmMsg = 'The Monster-of-the-Month for September are Ettins **__(Repond)__**.' + '\n'
                        motmMsg += 'They drop Hue 2519 items and "Ettin Greaser" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674882317189120/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if month[1] == "oct":
                        motmMsg = 'The Monster-of-the-Month for October are Earth Elementals **__(Elemental Ban)__**.' + '\n'
                        motmMsg += 'They drop Hue 2708 items and "Mud Dauber" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674932225343490/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if month[1] == "nov":
                        motmMsg = 'The Monster-of-the-Month for November are Terathan Warriors **__(Arachnid Doom)__**.' + '\n'
                        motmMsg += 'They drop Hue 2709 items and "Spider Stomper" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452674981042585600/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
                    if month[1] == "dec":
                        motmMsg = 'The Monster-of-the-Month for December are Ratmen **__(Repond)__**.' + '\n'
                        motmMsg += 'They drop Hue 1932 items and "Splintered" titles.' + '\n'
                        motmMsg += 'https://cdn.discordapp.com/attachments/403597340713156621/452675036487352335/unknown.png'
                        await client.send_message(message.channel, motmMsg)
    
            ###########################
            ### Player Point Module ###
            ###########################
    
            if prefix + 'points' in message.content.lower():
                pointMsg = '```ini' + '\n'
                pointMsg += 'Player Scores Leaderboard:' + '\n'
                pointMsg += '\n'
                pointMsg += '[ Discord ID | Total Points | Up | Down ]' + '\n'
                c.execute("SELECT * FROM points ORDER BY points DESC")
                select = c.fetchall()
                for idx, row in enumerate(select, start = 1):
                    pointMsg += '[ ' + str(idx) + '. ' + str(row[0]) + ' | ' + str(row[1]) + ' | ' + str(row[2]) + ' | ' + str(row[3]) + ' ]' '\n'
                pointMsg += '```'
                await client.send_message(message.channel, pointMsg)
    
            if prefix + 'reset' in message.content.lower():
                    if message.author.id == '165663747652845578' or '388017480490024966' in [role.id for role in message.author.roles] or '357919453721395200' in [role.id for role in message.author.roles]:
                        c.execute("DELETE FROM points")
                        await client.send_message(client.get_channel(main), 'The score board has been resetted by ' + str(message.author))
                    else:
                        await client.send_message(message.author, 'You do not have sufficient priviledges to reset the leader board.')
    
            upPoint = 20
            downPoint = 10
    
            def scoreStatus(champ):
                champReady = 'false'
                results = retrieve(champ)
                if results[0][1] == 'Unknown':
                    champReady = 'true'
                elif results[0][1] == 'Down':
                    downtime = datetime.strptime(results[0][2], '%Y-%m-%d %H:%M:%S')
                    curtime = datetime.utcnow().replace(microsecond=0)
                    interval = curtime - downtime
                    if interval >= timedelta(hours=4):
                        champReady = 'true'
                elif results[0][1] == 'Up':
                    uptime = datetime.strptime(results[0][2], '%Y-%m-%d %H:%M:%S')
                    curtime = datetime.utcnow().replace(microsecond=0)
                    interval = curtime - uptime
                    if interval >= timedelta(minutes=15):
                        champReady = 'true'
                return champReady
    
            def playerScore(champ, messageauthor, status):
                champReady = scoreStatus(champ)
                player = str(messageauthor)
                pointItem = getPoints(player)
                if pointItem is None and champReady == 'true':
                    createPoints(player, upPoint, 1, 0)
                    champReady = 'false'
                elif champReady == 'true':
                    currentUpScore = pointItem[2]
                    currentDownScore = pointItem[3]
                    currentPoint = pointItem[1]
                    if status == 'Up':
                        currentPoint += upPoint
                        currentUpScore += 1
                        givePoints(player, currentPoint, currentUpScore, currentDownScore)
                        champReady = 'false'
                        return upPoint
                    elif status == 'Down':
                        currentPoint += downPoint
                        currentDownScore += 1
                        givePoints(player, currentPoint, currentUpScore, currentDownScore)
                        champReady = 'false'
                        return downPoint
    
            #######################  
            #### Champ updates ####
            #######################
            
            class Champ:
    
                def __init__(self, champ, messageauthor, status):
                    self.status = status
                    if status == 'Up':
                        self.uptime = datetime.utcnow().replace(microsecond=0)
                        self.downtime = self.uptime - timedelta(seconds=1)
                        if messageauthor != 0:
                            self.points = playerScore(champ, messageauthor, status)
                        update(champ, 'Up', self.uptime, self.uptime)
                    if status == 'Down':
                        self.downtime = datetime.utcnow().replace(microsecond=0)
                        self.uptime = self.downtime - timedelta(seconds=1)
                        if messageauthor != 0:
                            self.points = playerScore(champ, messageauthor, status)
                        update(champ, 'Down', self.downtime, self.downtime) 
                    if status == 'Check':
                        current = retrieve(champ)
                        self.checktime = datetime.utcnow().replace(microsecond=0)
                        update(champ, current[0][1], current[0][2], self.checktime) 
                    if status != 'Up' and status != 'Down' and status != 'Check':
                        offset = int(status)
                        self.downtime = datetime.utcnow().replace(microsecond=0) - timedelta(seconds=offset)
                        self.uptime = self.downtime - timedelta(seconds=1)
                        update(champ, 'Down', self.downtime, self.downtime)
                        self.status = 'Down'
                        self.points = 0
    
                def pointAwarded(self):
                    if self.points != None:
                        pointMsg = ' has been awarded __**' + str(self.points) + '**__ points for reporting!' 
                    else: 
                        pointMsg = ""
                    return pointMsg
    
            # Abyss
            if prefix + 'abyss up' in message.content.lower() or prefix + '어비스 업' in message.content.lower():
                abyss = Champ('Abyss', message.author, 'Up')
                await client.send_message(client.get_channel(normal), '@everyone Abyss (어비스) Champ - Semidar __**(Exorcism 퇴마)**__ started at ' + abyss.uptime.strftime(FMT) + ' (UTC). Please remember to report when boss is killed')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if abyss.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(abyss.pointAwarded()))
    
            if prefix + 'abyss down' in message.content.lower() or prefix + '어비스 다운' in message.content.lower():
                abyss = Champ('Abyss', message.author, 'Down')
                await client.send_message(client.get_channel(normal), '@everyone Abyss (어비스) Champ - Semidar killed at ' + abyss.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if abyss.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(abyss.pointAwarded()))
    
            if prefix + 'abyss check' in message.content.lower():
                abyss = Champ('Abyss', message.author, 'Check')
                await client.send_message(client.get_channel(normal), '@everyone Abyss (어비스) Champ - Semidar has been checked at ' + abyss.checktime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))

            if prefix + 'abyss' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up" and args[1] != "check":
                    offset = int(args[1]) * 60
                    abyss = Champ('Abyss', 0, offset)
                    await client.send_message(client.get_channel(normal), '@everyone Abyss Champ killed __' + args[1] + ' minutes ago__ at ' + abyss.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
    
            # Covetous
            if prefix + 'cove up' in message.content.lower() or prefix + 'covetous up' in message.content.lower() or prefix + '코브 업' in message.content.lower():
                cove = Champ('Covetous', message.author, 'Up')
                await client.send_message(client.get_channel(secret), '@everyone Covetous (코브) Champ - Corpse Devourer __**(Silver 언데드)**__ started at ' + cove.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                if cove.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(cove.pointAwarded()))
    
            if prefix + 'cove down' in message.content.lower() or prefix + 'cove dead' in message.content.lower() or prefix + 'covetous down' in message.content.lower() or prefix + 'covetous dead' in message.content.lower() or prefix + '코브 다운' in message.content.lower():
                cove = Champ('Covetous', message.author, 'Down')
                await client.send_message(client.get_channel(secret), '@everyone Covetous (코브) Champ - Corpse Devourer killed at ' + cove.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                if cove.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(cove.pointAwarded()))
    
            if prefix + 'cove check' in message.content.lower():
                abyss = Champ('Covetous', message.author, 'Check')
                await client.send_message(client.get_channel(secret), '@everyone Covetous (코브) Champ - Corpse Devourer has been checked at ' + cove.checktime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))

            if prefix + 'cove' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    cove = Champ('Covetous', 0, offset)
                    await client.send_message(client.get_channel(secret), '@everyone Covetous (코브) Champ - Corpse Devourer killed __' + args[1] + ' minutes ago__ at ' + cove.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
    
            # Deceit
            if prefix + 'deceit up' in message.content.lower() or prefix + '디싯 업' in message.content.lower():
                deceit = Champ('Deceit', message.author, 'Up')
                await client.send_message(client.get_channel(normal), '@everyone Deceit (디싯) Champ - Neira __**(Silver 언데드)**__ started at ' + deceit.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if deceit.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(deceit.pointAwarded()))
    
            if prefix + 'deceit down' in message.content.lower() or prefix + '디싯 다운' in message.content.lower():
                deceit = Champ('Deceit', message.author, 'Down')
                await client.send_message(client.get_channel(normal), '@everyone Deceit (디싯) Champ - Neira killed at ' + deceit.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if deceit.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(deceit.pointAwarded()))
    
            if prefix + 'deceit check' in message.content.lower():
                abyss = Champ('Deceit', message.author, 'Check')
                await client.send_message(client.get_channel(normal), '@everyone Deceit (디싯) Champ - Neira has been checked at ' + deceit.checktime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))

            if prefix + 'deceit' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    deceit = Champ('Deceit', 0, offset)
                    await client.send_message(client.get_channel(normal), '@everyone Deceit (디싯) Champ - Neira killed __' + args[1] + ' minutes ago__ at ' + deceit.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
    
            # Despise
            if prefix + 'despise up' in message.content.lower() or prefix + '디스파이스 업' in message.content.lower():
                despise = Champ('Despise', message.author, 'Up')
                await client.send_message(client.get_channel(normal), '@everyone Despise (디스파이스) Champ - Barracoon __**(Repond 인간형)**__ started at ' + despise.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if despise.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(despise.pointAwarded()))
    
            if prefix + 'despise down' in message.content.lower() or prefix + '디스파이스 다운' in message.content.lower():
                despise = Champ('Despise', message.author, 'Down')
                await client.send_message(client.get_channel(normal), '@everyone Despise (디스파이스) Champ - Barracoon killed at ' + despise.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if despise.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(despise.pointAwarded()))
    
            if prefix + 'despise check' in message.content.lower():
                abyss = Champ('Despise', message.author, 'Check')
                await client.send_message(client.get_channel(normal), '@everyone Despise (디스파이스) Champ - Barracoon has been checked at ' + despise.checktime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))

            if prefix + 'despise' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    despise = Champ('Despise', 0, offset)
                    await client.send_message(client.get_channel(normal), '@everyone Despise (디스파이스) Champ - Barracoon killed __' + args[1] + ' minutes ago__ at ' + despise.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
    
            # Destard
            if prefix + 'destard up' in message.content.lower() or prefix + '데스타드 업' in message.content.lower():
                destard = Champ('Destard', message.author, 'Up')
                await client.send_message(client.get_channel(normal), '@everyone Destard (데스타드) Champ - Rikktor __**(Reptilian Death 파충류)**__ started at ' + destard.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if destard.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(destard.pointAwarded()))
    
            if prefix + 'destard down' in message.content.lower() or prefix + '데스타드 다운' in message.content.lower():
                destard = Champ('Destard', message.author, 'Down')
                await client.send_message(client.get_channel(normal), '@everyone Destard (데스타드) Champ - Rikktor killed at ' + destard.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if destard.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(destard.pointAwarded()))
    
            if prefix + 'destard check' in message.content.lower():
                abyss = Champ('Destard', message.author, 'Check')
                await client.send_message(client.get_channel(normal), '@everyone Destard (데스타드) Champ - Rikktor has been checked at ' + Destard.checktime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))

            if prefix + 'destard' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    destard = Champ('Destard', 0, offset)
                    await client.send_message(client.get_channel(normal), '@everyone Destard (데스타드) Champ - Rikktor killed __' + args[1] + ' minutes ago__ at ' + destard.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
    
            # Orc
            if prefix + 'orc up' in message.content.lower() or prefix + '오크 업' in message.content.lower():
                orc = Champ('Orc', message.author, 'Up')
                await client.send_message(client.get_channel(normal), '@everyone Orc (오크) Champ - Grummsh __**(Repond 인간형)**__ started at ' + orc.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if orc.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(orc.pointAwarded()))
    
            if prefix + 'orc down' in message.content.lower() or prefix + '오크 다운' in message.content.lower():
                orc = Champ('Orc', message.author, 'Down')
                await client.send_message(client.get_channel(normal), '@everyone Orc (오크) Champ - Grummsh killed at ' + orc.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if orc.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(orc.pointAwarded()))
    
            if prefix + 'orc check' in message.content.lower():
                abyss = Champ('Orc', message.author, 'Check')
                await client.send_message(client.get_channel(normal), '@everyone Orc (오크) Champ - Grummsh has been checked at ' + orc.checktime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))

            if prefix + 'orc' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    orc = Champ('Orc', 0, offset)
                    await client.send_message(client.get_channel(normal), '@everyone Orc (오크) Champ - Grummsh killed __' + args[1] + ' minutes ago__ at ' + orc.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
    
            # Shame
            if prefix + 'shame up' in message.content.lower() or prefix + '쉐임 업' in message.content.lower():
                shame = Champ('Shame', message.author, 'Up')
                await client.send_message(client.get_channel(normal), '@everyone Shame (쉐임) Champ - Gorde __**(Elemantal Ban 정령)**__ started at ' + shame.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if shame.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(shame.pointAwarded()))
    
            if prefix + 'shame down' in message.content.lower() or prefix + '쉐임 다운' in message.content.lower():
                shame = Champ('Shame', message.author, 'Down')
                await client.send_message(client.get_channel(normal), '@everyone Shame (쉐임) Champ - Gorde killed at ' + shame.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if shame.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(shame.pointAwarded()))
    
            if prefix + 'shame check' in message.content.lower():
                abyss = Champ('Shame', message.author, 'Check')
                await client.send_message(client.get_channel(normal), '@everyone Shame (쉐임) Champ - Gorde has been checked at ' + shame.checktime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))

            if prefix + 'shame' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    shame = Champ('Shame', 0, offset)
                    await client.send_message(client.get_channel(normal), '@everyone Shame (쉐임) Champ - Gorde killed __' + args[1] + ' minutes ago__ at ' + shame.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
    
            # Terathan
            if prefix + 'tera up' in message.content.lower() or prefix + 'terathan up' in message.content.lower() or prefix + '테라 업' in message.content.lower():
                tera = Champ('Terathan', message.author, 'Up')
                await client.send_message(client.get_channel(normal), '@everyone Terathan (테라) Champ - Mephitis __**(Arachnid Doom 거미류)**__ started at ' + tera.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if tera.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(tera.pointAwarded()))
    
            if prefix + 'tera down' in message.content.lower() or prefix + 'terathan down' in message.content.lower() or prefix + '테라 다운' in message.content.lower():
                tera = Champ('Terathan', message.author, 'Down')
                await client.send_message(client.get_channel(normal), '@everyone Terathan (테라) Champ - Mephitis killed at ' + tera.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
                if tera.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(tera.pointAwarded()))
    
            if prefix + 'tera check' in message.content.lower():
                abyss = Champ('Terathan', message.author, 'Check')
                await client.send_message(client.get_channel(normal), '@everyone Terathan (테라) Champ - Mephitis has been checked at ' + tera.checktime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))

            if prefix + 'tera' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    tera = Champ('Terathan', 0, offset)
                    await client.send_message(client.get_channel(normal), '@everyone Terathan (테라) Champ - Mephitis killed __' + args[1] + ' minutes ago__ at ' + tera.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(normal), 'Reported by: ' + str(message.author))
    
            # Wrong
            if prefix + 'wrong up' in message.content.lower() or prefix + 'oaks up' in message.content.lower() or prefix + '롱 업' in message.content.lower():
                wrong = Champ('Wrong', message.author, 'Up')
                await client.send_message(client.get_channel(secret), '@everyone Wrong (롱) Champ - Lord Oaks __**(Fey Slayer 페어리)**__ started at ' + wrong.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                if wrong.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(wrong.pointAwarded()))
    
            if prefix + 'wrong down' in message.content.lower() or prefix + '롱 다운' in message.content.lower():
                wrong = Champ('Wrong', message.author, 'Down')
                await client.send_message(client.get_channel(secret), '@everyone Wrong (롱) Champ - Lord Oaks killed at ' + wrong.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                if wrong.pointAwarded() != "":
                    await client.send_message(message.channel, str(message.author) + str(wrong.pointAwarded()))
                    
            if prefix + 'wrong check' in message.content.lower():
                abyss = Champ('Wrong', message.author, 'Check')
                await client.send_message(client.get_channel(secret), '@everyone Wrong (롱) Champ - Lord Oaks has been checked at ' + wrong.checktime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
    
            if prefix + 'wrong' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    wrong = Champ('Wrong', 0, offset)
                    await client.send_message(client.get_channel(secret), '@everyone Wrong (롱) Champ - Lord Oaks killed __' + args[1] + ' minutes ago__ at ' + wrong.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
    
            ######################
            ### Dungeon Bosses ###
            ######################
    
            # Adramalech
            if prefix + 'adra up' in message.content.lower() or prefix + 'adramalech up' in message.content.lower() or prefix + 'hythloth up' in message.content.lower() or prefix + '히보 업' in message.content.lower():
                adra = Champ('Adramalech', message.author, 'Up')
                await client.send_message(client.get_channel(secret), '@everyone Hythloth Boss - Adramalech (히보) started at ' + adra.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(secret), 'For more information, please visit: http://bit.ly/adramalech')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
    
            if prefix + 'adra down' in message.content.lower() or prefix + 'adramalech down' in message.content.lower() or prefix + 'hythloth down' in message.content.lower() or prefix + '히보 다운' in message.content.lower():
                adra = Champ('Adramalech', message.author, 'Down')
                await client.send_message(client.get_channel(secret), '@everyone Adramalech (히보) killed at ' + adra.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                await asyncio.sleep(27000)
                await client.send_message(client.get_channel(secret), '@everyone Adramalech (히보) altar will accept crystals in 30 mins!')
                await asyncio.sleep(28800)
                await client.send_message(client.get_channel(secret), '@everyone Adramalech (히보) altar is now accepting crystals!')
    
            if prefix + 'adra' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    adra = Champ('Adramalech', 0, offset)
                    await client.send_message(client.get_channel(secret), '@everyone Adramalech (히보) killed __' + args[1] + ' minutes ago__ at ' + adra.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                    await asyncio.sleep(27000)
                    await client.send_message(client.get_channel(secret), '@everyone Adramalech (히보) altar will accept crystals in 30 mins!')
                    await asyncio.sleep(28800)
                    await client.send_message(client.get_channel(secret), '@everyone Adramalech (히보) altar is now accepting crystals!')
    
            # Akor
            if prefix + 'akor up' in message.content.lower() or prefix + '아코르 업' in message.content.lower():
                akor = Champ('Akor', message.author, 'Up')
                await client.send_message(client.get_channel(secret), '@everyone Akor (아코르) __**(Reptilian Death 파충류)**__ started at ' + akor.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(secret), 'For more information, please visit: http://bit.ly/uo_akor')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
    
            if prefix + 'akor down' in message.content.lower() or prefix + 'akor down' in message.content.lower() or prefix + '아코르 다운' in message.content.lower():
                akor = Champ('Akor', message.author, 'Down')
                await client.send_message(client.get_channel(secret), '@everyone Akor (아코르) killed at ' + akor.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                await asyncio.sleep(27000)
                await client.send_message(client.get_channel(secret), '@everyone Akor (아코르) altar will accept crystals in 30 mins!')
                await asyncio.sleep(28800)
                await client.send_message(client.get_channel(secret), '@everyone Akor (아코르) altar is now accepting crystals!')
    
            if prefix + 'akor' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    akor = Champ('Akor', 0, offset)
                    await client.send_message(client.get_channel(secret), '@everyone Akor (아코르) killed __' + args[1] + ' minutes ago__ at ' + akor.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                    await asyncio.sleep(27000)
                    await client.send_message(client.get_channel(secret), '@everyone Akor (아코르) altar will accept crystals in 30 mins!')
                    await asyncio.sleep(28800)
                    await client.send_message(client.get_channel(secret), '@everyone Akor (아코르) altar is now accepting crystals!')
    
            # Arch Demon
            if prefix + 'arch up' in message.content.lower() or prefix + 'arch demon up' in message.content.lower() or prefix + '아크 업' in message.content.lower() or prefix + '아크 데몬 업' in message.content.lower() or prefix + '아크데몬 업' in message.content.lower():
                arch = Champ('Arch Demon', message.author, 'Up')
                await client.send_message(client.get_channel(secret), '@everyone Arch Demon (아크 데몬) started at ' + arch.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(secret), 'For more information, please visit: http://bit.ly/arch_demon')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
    
            if prefix + 'arch down' in message.content.lower() or prefix + 'arch demon down' in message.content.lower() or prefix + '아크 다운' in message.content.lower() or prefix + '아크 데몬 다운' in message.content.lower() or prefix + '아크데몬 다운' in message.content.lower():
                arch = Champ('Arch Demon', message.author, 'Down')
                await client.send_message(client.get_channel(secret), '@everyone Arch Demon (아크 데몬) killed at ' + arch.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                await asyncio.sleep(12600)
                await client.send_message(client.get_channel(secret), '@everyone Arch Demon (아크 데몬) Window opens in 30 minutes!')
                await asyncio.sleep(1800)
                await client.send_message(client.get_channel(secret), '@everyone Arch Demon (아크 데몬) Window begins! Boss may spawn anytime within the hour!')
    
            if prefix + 'arch' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    arch = Champ('Arch Demon', 0, offset)
                    await client.send_message(client.get_channel(secret), '@everyone Arch Demon (아크 데몬) killed __' + args[1] + ' minutes ago__ at ' + arch.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                    await asyncio.sleep(12600)
                    await client.send_message(client.get_channel(secret), '@everyone Arch Demon (아크 데몬) Window opens in 30 minutes!')
                    await asyncio.sleep(1800)
                    await client.send_message(client.get_channel(secret), '@everyone Arch Demon (아크 데몬) Window begins! Boss may spawn anytime within the hour!')
    
            # Fafnir
            if prefix + 'fafnir up' in message.content.lower() or prefix + 'faf up' in message.content.lower() or prefix + '파프 업' in message.content.lower():
                fafnir = Champ('Fafnir', message.author, 'Up')
                await client.send_message(client.get_channel(secret), '@everyone Fafnir (파프) __**(Reptilian Death 파충류)**__ started at ' + fafnir.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(secret), 'For more information, please visit: http://bit.ly/destard_fafnir')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
    
            if prefix + 'fafnir down' in message.content.lower() or prefix + 'faf down' in message.content.lower()  or prefix + '파프 다운' in message.content.lower():
                fafnir = Champ('Fafnir', message.author, 'Down')
                await client.send_message(client.get_channel(secret), '@everyone Fafnir (파프) killed at ' + fafnir.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                await asyncio.sleep(27000)
                await client.send_message(client.get_channel(secret), '@everyone Fafnir (파프) altar will accept crystals in 30 mins!')
                await asyncio.sleep(28800)
                await client.send_message(client.get_channel(secret), '@everyone Fafnir (파프) altar is now accepting crystals!')
    
            if prefix + 'fafnir' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    fafnir = Champ('Fafnir', 0, offset)
                    await client.send_message(client.get_channel(secret), '@everyone Fafnir (파프) killed __' + args[1] + ' minutes ago__ at ' + fafnir.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                    await asyncio.sleep(27000)
                    await client.send_message(client.get_channel(secret), '@everyone Fafnir (파프) altar will accept crystals in 30 mins!')
                    await asyncio.sleep(28800)
                    await client.send_message(client.get_channel(secret), '@everyone Fafnir (파프) altar is now accepting crystals!')
    
            # Lich Khan
            if prefix + 'lich up' in message.content.lower() or prefix + 'lich khan up' in message.content.lower() or prefix + '리치 업' in message.content.lower() or prefix + '리치칸 업' in message.content.lower() or prefix + '리치칸 업' in message.content.lower():
                lich = Champ('Lich Khan', message.author, 'Up')
                await client.send_message(client.get_channel(secret), '@everyone Lich Khan (리치 칸) started at ' + lich.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(secret), 'For more information, please visit: http://bit.ly/lich_khan')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
    
            if prefix + 'lich down' in message.content.lower() or prefix + 'lich khan down' in message.content.lower() or prefix + '리치 다운' in message.content.lower() or prefix + '리치칸 다운' in message.content.lower() or prefix + '리치칸 다운' in message.content.lower():
                lich = Champ('Lich Khan', message.author, 'Down')
                await client.send_message(client.get_channel(secret), '@everyone Lich Khan (리치 칸) killed at ' + lich.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                await asyncio.sleep(12600)
                await client.send_message(client.get_channel(secret), '@everyone Lich Khan (리치 칸)  Window opens in 30 minutes!')
                await asyncio.sleep(1800)
                await client.send_message(client.get_channel(secret), '@everyone Lich Khan (리치 칸) Window begins! Boss may spawn anytime within the hour!')
    
            if prefix + 'lich' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    lich = Champ('Lich Khan', 0, offset)
                    await client.send_message(client.get_channel(secret), '@everyone Lich Khan (리치 칸) killed __' + args[1] + ' minutes ago__ at ' + lich.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
                    await asyncio.sleep(12600)
                    await client.send_message(client.get_channel(secret), '@everyone Lich Khan (리치 칸)  Window opens in 30 minutes!')
                    await asyncio.sleep(1800)
                    await client.send_message(client.get_channel(secret), '@everyone Lich Khan (리치 칸) Window begins! Boss may spawn anytime within the hour!')
    
            # Warlock
            if prefix + 'warlock up' in message.content.lower() or prefix + '워록 업' in message.content.lower():
                warlock = Champ('Warlock', message.author, 'Up')
                await client.send_message(client.get_channel(secret), '@everyone Warlock (워록) started at ' + warlock.uptime.strftime(FMT) + ' (UTC).  Please remember to report when boss is killed')
                await client.send_message(client.get_channel(secret), 'For more information, please visit: http://bit.ly/uo_warlock')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
    
            if prefix + 'warlock down' in message.content.lower() or prefix + '워록 다운' in message.content.lower():
                warlock = Champ('Warlock', message.author, 'Down')
                await client.send_message(client.get_channel(secret), '@everyone Warlock (워록) killed at ' + warlock.downtime.strftime(FMT) + ' (UTC)')
                await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
    
            if prefix + 'warlock' in message.content.lower():
                args = message.content.lower().split(" ")
                if args[1] != "down" and args[1] != "up":
                    offset = int(args[1]) * 60
                    warlock = Champ('Warlock', 0, offset)
                    await client.send_message(client.get_channel(secret), '@everyone Warlock (워록) killed __' + args[1] + ' minutes ago__ at ' + warlock.downtime.strftime(FMT) + ' (UTC)')
                    await client.send_message(client.get_channel(secret), 'Reported by: ' + str(message.author))
    
            # All status
    
            if prefix + 'status' in message.content.lower() or prefix + '상황' in message.content.lower():
    
                readyMsg = {}
    
                class Status:
    
                    def __init__(self, champ, boss):
                        results = retrieve(champ)
                        self.champ = champ
                        if results[0][1] == 'Unknown':
                            self.status = unknown
                        elif results[0][1] == 'Down':
                            checked = datetime.strptime(results[0][3], '%Y-%m-%d %H:%M:%S')
                            downtime = datetime.strptime(results[0][2], '%Y-%m-%d %H:%M:%S')
                            curtime = datetime.utcnow().replace(microsecond=0)
                            self.interval = curtime - downtime
                            self.checkedinterval = curtime - checked
                            checkedhours, checkedremainder = divmod(self.checkedinterval.total_seconds(), 3600)
                            checkedminutes, remainder = divmod(checkedremainder, 60)
                            hours, remainder = divmod(self.interval.total_seconds(), 3600)
                            minutes, remainder = divmod(remainder, 60)
                            self.status = "'Down' %s Hours %s Minutes Ago. [Checked: %s Hours %s Minutes Ago]" % (round(hours), round(minutes),
                                                                                                                   round(checkedhours),
                                                                                                                   round(checkedminutes))
                            if self.interval >= timedelta(hours=4) and boss != "Yes":
                                # self.readyMsg += champ + ' - ' + self.status + '\n'
                                readyMsg[champ] = self.status
                        elif results[0][1] == 'Up':
                            checked = datetime.strptime(results[0][3], '%Y-%m-%d %H:%M:%S')
                            uptime = datetime.strptime(results[0][2], '%Y-%m-%d %H:%M:%S')
                            curtime = datetime.utcnow().replace(microsecond=0)
                            self.interval = curtime - uptime
                            self.checkedinterval = curtime - checked
                            checkedhours, checkedremainder = divmod(self.checkedinterval.total_seconds(), 3600)
                            checkedminutes, remainder = divmod(checkedremainder, 60)
                            hours, remainder = divmod(self.interval.total_seconds(), 3600)
                            minutes, remainder = divmod(remainder, 60)
                            self.status = '"Up" %s Hours %s Minutes Ago. [Checked: %s Hours %s Minutes Ago]' % (round(hours), round(minutes),
                                                                                                                   round(checkedhours),
                                                                                                                   round(checkedminutes))
                            if boss != "Yes":
                                readyMsg[champ] = self.status
    
                abyss = Status('Abyss', "No")
                cove = Status('Covetous', "No")
                deceit = Status('Deceit', "No")
                despise = Status('Despise', "No")
                destard = Status('Destard', "No")
                orc = Status('Orc', "No")
                shame = Status('Shame', "No")
                tera = Status('Terathan', "No")
                wrong = Status('Wrong', "No")
                adra = Status('Adramalech', "Yes")
                akor = Status('Akor', "Yes")
                arch = Status('Arch Demon', "Yes")
                fafnir = Status('Fafnir', "Yes")
                lich = Status('Lich Khan', "Yes")
                warlock = Status('Warlock', "Yes")
    
                status_msg = '```ml' + '\n'
                status_msg += "'Champs'" + '\n'
                status_msg += '- Abyss (어비스) - ' + abyss.status + '\n'
                status_msg += '- Deceit (디싯) - ' + deceit.status + '\n'
                status_msg += '- Despise (디스파이스) - ' + despise.status + '\n'
                status_msg += '- Destard (데스타드) - ' + destard.status + '\n'
                status_msg += '- Orc (오크) - ' + orc.status + '\n'
                status_msg += '- Shame (쉐임) - ' + shame.status + '\n'
                status_msg += '- Terathan (테라) - ' + tera.status + '\n'
                status_msg += '```'
    
                await client.send_message(client.get_channel(normal), status_msg)
    
                status_msg = '```ml' + '\n'
                status_msg += "'Champs'" + '\n'
                status_msg += '- Abyss (어비스) - ' + abyss.status + '\n'
                status_msg += '- Covetous (코브) - ' + cove.status + '\n'
                status_msg += '- Deceit (디싯) - ' + deceit.status + '\n'
                status_msg += '- Despise (디스파이스) - ' + despise.status + '\n'
                status_msg += '- Destard (데스타드) - ' + destard.status + '\n'
                status_msg += '- Orc (오크) - ' + orc.status + '\n'
                status_msg += '- Shame (쉐임) - ' + shame.status + '\n'
                status_msg += '- Terathan (테라) - ' + tera.status + '\n'
                status_msg += '- Wrong (롱) - ' + wrong.status + '\n'
                status_msg += '```'
                status_msg += '```ml' + '\n'
                status_msg += "'Dungeon_Bosses'" + '\n'
                status_msg += '- Adramalech (히보) - ' + adra.status + '\n'
                status_msg += '- Akor (아코르) - ' + adra.status + '\n'
                status_msg += '- Arch Demon (아크 데몬) - ' + arch.status + '\n'
                status_msg += '- Fafnir (파프) - ' + fafnir.status + '\n'
                status_msg += '- Lich Khan (리치 칸) - ' + lich.status + '\n'
                status_msg += '- Warlock (워록) - ' + warlock.status + '\n'
                status_msg += '```'
    
                if len(readyMsg) > 0:
                    ready_msg = '```ml' + '\n'
                    ready_msg += '"Champs Ready"' + '\n'
                    for champ, status in readyMsg.items():
                        ready_msg += '- ' + champ + ' - ' + status + '\n'
                    ready_msg += '```'
                    await client.send_message(client.get_channel(secret), ready_msg)
    
                await client.send_message(client.get_channel(secret), status_msg)

client.run('') #discord bot token needed
conn.close()
c.close()
