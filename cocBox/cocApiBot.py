from urllib.parse import quote
import requests
import logging, discord

logging.basicConfig(level = logging.INFO)

from discord.ext.commands import Bot
coc_token = '<COC API Token>'
bot = Bot(command_prefix='-')

@bot.event
async def on_ready():
    print('Logged in')
    await bot.change_presence(game=discord.Game(name='testing'))

@bot.command()
async def claninfo(clantag):
    main_api = 'https://api.clashofclans.com/v1/clans/'
    url = main_api + quote(clantag)
    json_data = requests.get(url, headers = {'Authorization': 'Bearer %s' %coc_token}).json()
    
    location = json_data['location']['name']
    level = json_data['clanLevel']
    member_count = str(json_data['members'])
    wins = str(json_data['warWins'])
    desc = json_data['description']
    
    em = discord.Embed(title='Description', description = desc, colour=0x4286f4)
    em.set_author(name=json_data['name'], icon_url=json_data['badgeUrls']['small'])
    em.add_field(name = 'Location', value = location, inline = True)
    em.add_field(name = 'Level', value = level, inline = True)
    em.add_field(name = 'Members', value = member_count, inline = True)
    em.add_field(name = 'War Wins', value = wins, inline = True)
    em.set_thumbnail(url = json_data['badgeUrls']['large'])
    def check(reaction, user):
        return user != bot.user

    msg = await bot.say(content = '*Press :information_source: for a list of members of %s*'%json_data['name'], embed = em)
    await bot.add_reaction(msg, 'ℹ')
    res = await bot.wait_for_reaction(emoji = 'ℹ', message = msg, check = check)

    def members():
        url = main_api + quote(clantag) + '/members'
        json_data2 = requests.get(url, headers = {'Authorization': 'Bearer %s' %coc_token}).json()
        info = []
        info.append (discord.Embed(title = 'Members of %s'%json_data['name'], colour = 0x4286f4))
        info.append(discord.Embed(title = 'Members of %s'%json_data['name'], colour = 0x4286f4))
        for i in json_data2['items']:
            player_info = requests.get('https://api.clashofclans.com/v1/players/' + quote(i['tag']), headers = {'Authorization': 'Bearer %s' %coc_token}).json()
            town_hall = str(player_info['townHallLevel'])
            if (i['clanRank']<=25):
                info[0].add_field(name = '%s. %s'%(str(i['clanRank']), i['name']), value = '%s, %s in %s, TH%s'%(i['tag'], i['role'], json_data['name'], town_hall), inline = False)
            else:
                info[1].add_field(name = '%s. %s'%(str(i['clanRank']), i['name']), value = '%s, %s in %s, TH%s'%(i['tag'], i['role'], json_data['name'], town_hall), inline = False)    
        return info

    mem_info = members()
    await bot.say(content = '*Player info for %s*'%json_data['name'], embed = mem_info[0])
    if (json_data['members']>25):
        await bot.say(content = '*Player info for %s*'%json_data['name'], embed = mem_info[1])
    
@bot.command()
async def playerinfo(playertag):
    main_api = 'https://api.clashofclans.com/v1/players/'
    url = main_api + quote(playertag)
    json_data = requests.get(url, headers = {'Authorization': 'Bearer %s' %coc_token}).json()
    name = json_data['name'] 
    try:
        league = json_data['league']['name']
        league_badge = json_data['league']['iconUrls']['small']
    except:
        league = 'None'
        league_badge = 'http://clash-wiki.com/images/progress/leagues/no_league.png'
        
    try:
        clan = json_data['clan']['name']
        clan_tag = json_data['clan']['tag']
        role = json_data['role']
        desc = '%s in %s (%s)' % (role, clan, clan_tag)
    except:
        desc = 'clanless'
    heroes = ''
    for i in json_data['heroes']:
        if (i['name'] != 'Battle Machine'):
            heroes = heroes + str(i['level']) + '/'
    heroes = heroes[:-1]
    
    em = discord.Embed(title = name, description = desc, colour = 0x4286f4)
    em.add_field(name = 'Town Hall Level', value = json_data['townHallLevel'], inline = True)
    em.add_field(name = 'Experience Level', value = json_data['expLevel'], inline = True)
    em.add_field(name = 'Trophy count', value = '%s (highest: %s)'%(json_data['trophies'], json_data['bestTrophies']), inline = True)
    em.add_field(name = 'War stars', value = json_data['warStars'], inline = True)
    em.add_field(name = 'Heroes', value = heroes)
    em.add_field(name = 'Builder Hall info', value = 'BH info for %s'%name, inline = False)
    em.add_field(name = 'Builder Hall Level', value = str(json_data['builderHallLevel']), inline = True)
    em.add_field(name = 'Builder Hall Trophies', value = str(json_data['versusTrophies']), inline = True)
    
    em.set_thumbnail(url = league_badge)

    def check(reaction, user):
        return user != bot.user
        
    msg = await bot.say(content = '*press :information_source: for more info about the player*', embed = em)
    await bot.add_reaction(msg, 'ℹ')
    res = await bot.wait_for_reaction(emoji = 'ℹ', message = msg, check = check)

    def home_troops():
        info = discord.Embed(title = '*Home base troop info for %s*'%name, colour = 0x4286f4)
        for i in json_data['troops']:
            if (i['village'] != 'home'):
                break
            info.add_field(name = i['name'], value = i['level'], inline = True)
        return info

    def spell_info():
        info = discord.Embed(title = '*Spell info for %s*'%name, colour = 0x4286f4)
        for i in json_data['spells']:
            info.add_field(name = i['name'], value = i['level'], inline = True)
        return info

    def bb_troops():
        info = discord.Embed(title = '*Builder base troop info for %s*'%name, colour = 0x4286f4)
        for i in json_data['troops']:
            if (i['village'] == 'builderBase'):
                info.add_field(name = i['name'], value = i['level'], inline = True)
        return info
        
    await bot.say(content = '*Extra player info for %s*'%name, embed = home_troops())
    await bot.say(content = '*Extra player info for %s*'%name, embed = spell_info())
    await bot.say(content = '*Extra player info for %s*'%name, embed = bb_troops())

@bot.event
async def on_message(message):
    if message.content.startswith('-missing'):
        main_api = 'https://api.clashofclans.com/v1/clans/'
        await bot.send_message(message.channel, 'What clan is the war being held in?')
        clan = await bot.wait_for_message(author = message.author)
        clan = clan.content
        
        if (clan == 'awmino'):
            tag = quote('#2VY9RYQC')
        elif (clan == 'crolegion'):
            tag = quote('#VQCJR0G')
        else:
            tag = quote(clan)
            
        clanApi = main_api + tag
        clanData = requests.get(clanApi, headers = {'Authorization': 'Bearer %s' %coc_token}).json()
        members = []
        missing = []
        await bot.send_message(message.channel, 'Please post the war list')
        warList = await bot.wait_for_message(author  = message.author)
        warList = warList.content
        warList = warList.split('\n')
        
        for i in clanData['memberList']:
            members.append(i['name'])
            
        for i in warList:
            if (i not in members):
                missing.append(i)
                
        if (len(missing)>0):
            msg = discord.Embed(title = 'Missing members', description = 'If you are on this list join %s ASAP'%clan, colour = 0x4286f4)
            for i in missing:
                msg.add_field(name = i, value = '-', inline = True)

        await bot.send_message(message.channel, embed = msg)
    
bot.run('<Discord API Token>')
