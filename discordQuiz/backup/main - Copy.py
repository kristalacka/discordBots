import discord, asyncio, json, logging, random
from discord.ext.commands import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dateutil.parser import parse
from datetime import datetime, timedelta

sched = AsyncIOScheduler()
logging.basicConfig(level = logging.INFO)
bot = Bot(command_prefix='!')
quiz ={
    'q1': 'a1',
    'q2': 'a2',
    'q3': 'a3',
    'q4': 'a4',
    'q5': 'a5',
    'q6': 'a6'
    }

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')
    
@bot.event
async def on_ready():
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)

@bot.event
async def on_server_join(server):
    for i in server.roles:
        if (i.name == 'joining'):
            break;
    else:
        await bot.create_role(server, name = 'joining')

    for i in server.roles:
        if (i.name == 'restricted'):
            break;
    else:
        await bot.create_role(server, name = 'restricted')

    new_data = {str(server.id): {'lockdown': False}}
    with open('serverState.json', 'r') as f:
        data = json.load(f)

    data.update(new_data)
    with open('serverState.json', 'w') as f:
        json.dump(data, f)

async def give_role(member, old_role):
    await bot.remove_roles(member, old_role)
    for i in member.server.roles:
        if (i.name.lower() == 'community'):
            new_role = i
    try:
        return await bot.add_roles(member, new_role)
    except:
        return
    
@bot.event
async def on_member_join(member):
    with open('serverState.json', 'r') as f:
        data = json.load(f)
    
    if (data[member.server.id]['lockdown']):
        return await bot.kick(member)
    
    for i in member.server.roles:
        if (i.name == 'joining'):
            role = i
            break
        
    await bot.add_roles(member, role)
    await bot.start_private_message(member)
    rules = await bot.send_message(member, content = 'Rules of the server: \
Lorem ipsum dolor sit amet, consectetur adipiscing elit. \
Type !start to begin your quiz.')
    await bot.wait_for_message(timeout=300, content='!start')
    await bot.send_message(member, content = 'Quiz started!')
    await bot.delete_message(rules)
    questions = random.sample(quiz.keys(), 3)
    def notBot(m):
        return m.author != bot.user
    
    for q in questions:
        await bot.send_message(member, content = q)
        answer = await bot.wait_for_message(timeout=300, check = notBot)
        if (answer.content.lower()!=quiz[q]):
            await bot.send_message(member, content = 'Incorrect answer, please reenter the server to start the quiz again: https://discord.gg/RTJWURr')
            return await bot.kick(member)
    else:
        await bot.send_message(member, content = 'Congratulations, you have passed!')
        await bot.remove_roles(member, role)
        for i in member.server.roles:
            if (i.name.lower() == 'new'):
                roleN = i
                break
        await bot.add_roles(member, roleN)
        sched.add_job(give_role, 'date', run_date = datetime.now()+timedelta(weeks=1), args=[member, roleN]) 
    return

@bot.command(pass_context=True)
async def lockdown(ctx, state):
    for j in ctx.message.author.roles:
        if (j.permissions.manage_roles):
            break
    else:
        return await bot.say('You are not an administrator')

    with open('serverState.json', 'r') as f:
        data = json.load(f)
        
    if (state=='begin'):
        data[ctx.message.server.id]['lockdown'] = True
        await bot.say('Lockdown has been initiated to figure out permission issues. Stay tuned to news channel for more info.')
    elif (state=='end'):
        data[ctx.message.server.id]['lockdown'] = False
        await bot.say('Lockdown is now over.')
    else:
        return await bot.say('invalid state')
    
    with open ('serverState.json', 'w') as f:
        json.dump(data, f)
    return;

@bot.command(pass_context=True)
async def kick(ctx, member):
    for j in ctx.message.author.roles:
        if (j.permissions.manage_roles):
            break
    else:
        return await bot.say('You are not an administrator')

    if (member[:2] == '<@'):
        member = ctx.message.mentions[0]
    else:
        member = ctx.message.server.get_member_named(member)
        
    await bot.say("%s has been kicked"%member.name)
    return await bot.kick(member)

@bot.command(pass_context=True)
async def ban(ctx, member):
    for j in ctx.message.author.roles:
        if (j.permissions.manage_roles):
            break
    else:
        return await bot.say('You are not an administrator')

    if (member[:2] == '<@'):
        member = ctx.message.mentions[0]
    else:
        member = ctx.message.server.get_member_named(member)
        
    await bot.say("%s has been banned"%member.name)
    return await bot.ban(member)

@bot.command(pass_context=True)
async def unban(ctx, member):
    for j in ctx.message.author.roles:
        if (j.permissions.manage_roles):
            break
    else:
        return await bot.say('You are not an administrator')

    server = ctx.message.server
    
    if (member[:1] == '@'):
        member = member[:-1]
    bans = await bot.get_bans(server)
    
    for i in bans:
        if (i.name[:-5] == member or i.name == member):
            member = i
            break
        
    await bot.say("%s has been unbanned"%member.name)
    return await bot.unban(server, member)

@bot.command(pass_context = True)
async def report(ctx, member, *args):
    message = ''
    if (member[:2] == '<@'):
        member = ctx.message.mentions[0]
    else:
        member = ctx.message.server.get_member_named(member)

    for i in args:
        message+=i+' '
    message = message[:-1]
    
    with open ('reports.json', 'r') as f:
        data = json.load(f)

    if (member.id not in data.keys()):
        data.update({member.id: {'reports':{ctx.message.author.name: message}, 'name': member.name}})
    else:
        for key, val in data[member.id]['reports'].items():
            if ctx.message.author.name == key:
                return await bot.say('You have already reported this person')
        data[member.id]['reports'][ctx.message.author.name] = message
    await bot.say('Thank you for the report, the admins will investigate if we keep getting negative feedback about the user')
      
    if (len(data[member.id]['reports'])==5):
        em = discord.Embed(title = 'User reports', description = 'for %s'%data[member.id]['name'], colour = 0x003087)
        for name, val in data[member.id]['reports'].items():
            em.add_field(name = name, value = val, inline=True)

        with open ('serverState.json', 'r') as f:
            data1 = json.load(f)
        channel = bot.get_channel(data1[ctx.message.server.id]['channel'])
        await bot.send_message(channel, content = '%s has 5 reports'%data[member.id]['name'], embed = em)
        for role in ctx.message.server.roles:
            if (role.name.lower() == 'restricted'):
                roleId = role
                break
        else:
            return await bot.say('error, no role called "restricted"')
        await bot.add_roles(member, roleId)
        data[member.id]['reports'] = {}
   
    with open ('reports.json', 'w') as f:
        json.dump(data, f)
    return

async def gend(message_id, msg_channel, server_id, desc, code):
    with open ('serverState.json', 'r') as f:
        data = json.load(f)

    server = bot.get_server(server_id)
    channel = bot.get_channel(data[server_id]['channel'])
    message = await bot.get_message(msg_channel, message_id)
    reactions = message.reactions
    for i in reactions:
        if (i.emoji == '✅'):
            reaction = i

    entries = await bot.get_reaction_users(reaction)
    entries = entries[:-1]
    for i, entry in enumerate(entries):
        entry = server.get_member(entry.id)
        roles = entry.roles
        for j in roles:
            if (j.name.lower() == 'epics'):
                break
        else:
            del entries[i]
        
    if (len(entries)>0):
        winner = random.choice(entries)
        msg = await bot.send_message(channel, content = 'everyone The giveaway for %s has ended! The winner is %s, congratulations! *Total number of valid entries:* `%s`'%(desc, winner.mention, len(entries)))
    else:
        await bot.send_message(channel, content = 'everyone no winner selected for giveaway %s: noone entered'%desc)

    msg = 'You\'ve won the giveaway %s!'%desc
    if (code != None):
        msg += ' Here\'s your code: %s'%code
        
    await bot.send_message(winner, content=msg)
    return

async def timer(end_time, message, desc, icon, name):
    em = discord.Embed(title = 'Giveaway', description = desc, colour = 0x003087)
    em.set_footer(text = 'By %s'%name, icon_url=icon)
    time = end_time-datetime.now()
    time = time - timedelta(microseconds=time.microseconds)
    if (time<=timedelta(minutes = 5)):
        time = 'ended'
    em.add_field(name = 'Time left:', value = str(time), inline=True)
    return await bot.edit_message(message, embed = em)
    
@bot.command(pass_context=True)
async def gcreate(ctx, *args):
    for j in ctx.message.author.roles:
        if (j.permissions.manage_roles):
            break
    else:
        return await bot.say('You are not an administrator')
        
    with open('serverState.json', 'r') as f:
        data = json.load(f)

    time = ''
    for i in args:
        time+=i + ' '

    time = time[:-1] #removed ws
    if (time[-1:] == 'h'):
        parsed_time = datetime.now()+timedelta(hours=float(time[:-1]))
    else:
        parsed_time = parse(time)

    if (parsed_time < datetime.now()):
        return await bot.say('I cannot travel back in time, it is %s UTC right now'%datetime.now())

    await bot.say('Is the giveaway a code or service?')
    g_type = await bot.wait_for_message(author = ctx.message.author, timeout=300)

    if (g_type.content.lower()=='code'):
        await bot.say('Enter the code for the giveaway.')
        code = await bot.wait_for_message(author = ctx.message.author, timeout=300)
        code = code.content
    else:
        code = None

    await bot.say('Enter the giveaway description.')
    desc = await bot.wait_for_message(author = ctx.message.author, timeout=300)
    desc = desc.content
    channel = bot.get_channel(data[ctx.message.server.id]['channel'])
    em = discord.Embed(title = 'Giveaway', description = desc, colour = 0x003087)
    em.set_footer(text = 'By %s'%ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    time = parsed_time-datetime.now()
    time = time - timedelta(microseconds=time.microseconds)
    em.add_field(name = 'Time left:', value = str(time), inline=True)

    message = await bot.send_message(channel, content = 'everyone new giveaway: %s! React to this message with :white_check_mark: to participate!'%desc, embed = em)
    await bot.add_reaction(message, '✅')
    sched.add_job(gend, 'date', run_date = parsed_time, args=[message.id, message.channel, ctx.message.server.id, desc, code])
    sched.add_job(timer, 'interval', minutes = 5, end_date = parsed_time, args = [parsed_time, message, desc, ctx.message.author.avatar_url, ctx.message.author.name])
    return
    
sched.start()
bot.run("MzQyMjQ0MTA5ODMyMTU5MjMz.DGMzWw.BZ4UjCHq-j4vEb_TjJXOocZSiC8")
