import discord, asyncio, json, logging, random
from discord.ext.commands import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dateutil.parser import parse
from datetime import datetime

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
giveaway_on=False
locked=True

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

    new_data = {str(server.id): {'lockdown': False, 'giveaway': False}}
    with open('serverState.json', 'r') as f:
        data = json.load(f)

    data.update(new_data)
    with open('serverState.json', 'w') as f:
        json.dump(data, f)
    
@bot.event
async def on_member_join(member):
    with open('serverState.json', 'r') as f:
        data = json.load(f)
    
    if (data[member.server.id]):
        return await bot.kick(member)
    
    for role in member.server.roles:
        if (role.name == 'joining'):
            roleId = role
            break
        
    await bot.add_roles(member, roleId)
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
        return await bot.remove_roles(member, roleId)

@bot.command(pass_context=True)
async def lockdown(ctx, state):
    for j in ctx.message.author.roles:
        if (j.permissions.administrator):
            break
    else:
        return await bot.say('You are not an administrator')

    with open('serverState.json', 'r') as f:
        data = json.load(f)
        
    if (state=='begin'):
        locked=True
        await bot.say('Lockdown has been initiated to figure out permission issues. Stay tuned to news channel for more info.')
    elif (state=='end'):
        locked=False;
        await bot.say('Lockdown is now over.')
    else:
        return await bot.say('invalid state')

    data[ctx.message.server.id]['lockdown'] = locked

    with open ('serverState.json', 'w') as f:
        json.dump(data, f)
    return;

@bot.command(pass_context=True)
async def kick(ctx, member):
    for j in ctx.message.author.roles:
        if (j.permissions.administrator):
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
        if (j.permissions.administrator):
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
        if (j.permissions.administrator):
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
        data.update({member.id: {'reports':[{ctx.message.author.name: message}], 'name': member.name}})
    else:
        for i in data[member.id]['reports']:
            if ctx.message.author.name in i.keys():
                return await bot.say('You have already reported this person')
        data[member.id]['reports'].append({ctx.message.author.name: message})
    await bot.say('Thank you for the report, the admins will investigate if we keep getting negative feedback about the user')
      
    if (len(data[member.id]['reports'])==5):
        await bot.say('%s has 5 reports'%data[member.id]['name'])
        for role in ctx.message.server.roles:
            if (role.name == 'restricted'):
                roleId = role
                break
        else:
            return await bot.say('error, no role called "restricted"')
        await bot.add_roles(member, roleId)
   
    with open ('reports.json', 'w') as f:
        json.dump(data, f)
    return

async def gend(message_id, msg_channel, server_id):
    with open ('serverState.json', 'r') as f:
        data = json.load(f)

    channel = bot.get_channel(data[server_id]['channel'])
    message = await bot.get_message(msg_channel, message_id)
    reactions = message.reactions
    print(reactions)
    for i in reactions:
        if (i.emoji == '✅'):
            reaction = i

    entries = await bot.get_reaction_users(reaction)
    print(entries)
    entries = entries[:-1]
    print(entries)
    winner = random.choice(entries)
    if (len(entries)>0):
        msg = await bot.send_message(channel, content = 'everyone The giveaway for %s has ended! The winner is %s, congratulations! *Total number of participants:* `%s`'%(data[server_id]['desc'], winner.mention, len(entries)))
    else:
        await bot.send_message(channel, content = 'everyone no winner selected: noone entered')

    data[server_id]['giveaway'] = False
    data[server_id]['desc'] = ''
    with open('serverState.json', 'w') as f:
        json.dump(data, f)

    await bot.send_message(winner, content='You\'ve won!')
    return
    
@bot.command(pass_context=True)
async def gcreate(ctx, *args):
    for j in ctx.message.author.roles:
        if (j.permissions.administrator):
            break
    else:
        return await bot.say('You are not an administrator')
        
    with open('serverState.json', 'r') as f:
        data = json.load(f)

    if (data[ctx.message.server.id]['giveaway']):
        return await bot.say('A giveaway is already active.')

    time = ''
    for i in args:
        time+=i + ' '
    parsed_time = parse(time[:-1])

    if (parsed_time < datetime.now()):
        return await bot.say('I cannot travel back in time, it is %s UTC right now'%datetime.now())
    
    await bot.say('Enter what the giveaway is for')
    desc = await bot.wait_for_message(author = ctx.message.author, timeout=300)
    desc = desc.content
    data[ctx.message.server.id]['giveaway'] = True
    data[ctx.message.server.id]['desc'] = desc
    
    with open('serverState.json', 'w') as f:
        json.dump(data, f)
        
    channel = bot.get_channel(data[ctx.message.server.id]['channel'])
    message = await bot.send_message(channel, content = 'everyone new giveaway: %s! React to this message with :white_check_mark: to participate!'%desc)
    await bot.add_reaction(message, '✅')
    sched.add_job(gend, 'date', run_date = parsed_time, args=[message.id, message.channel, ctx.message.server.id])
    return
    
sched.start()
bot.run("MzQyMjQ0MTA5ODMyMTU5MjMz.DGMzWw.BZ4UjCHq-j4vEb_TjJXOocZSiC8")
