import discord, random, praw, asyncio, json

count = 0

from discord.ext.commands import Bot

my_bot = Bot(command_prefix="!")

reddit = praw.Reddit(client_id='<ID>',
                     client_secret='Secret',
                     user_agent='UA',
                     username='UN',
                     password='<Pass>')

@my_bot.event
async def on_ready():
   print('Logged in as')
   print(my_bot.user.name)
   print(my_bot.user.id)
   print(len(my_bot.servers))
   await my_bot.change_presence(game=discord.Game(name='type !info'))

@my_bot.event
async def on_server_join(server):
   for i in server.roles:
      if (i.name == 'JuiceBot Commander'):
         break;
   else:
      await my_bot.create_role(server, name = 'JuiceBot Commander')
      
   new_data = {str(server.id): False}
   
   with open('servers.json', 'r') as f:
      data = json.load(f)

   data.update(new_data)
   with open('servers.json', 'w') as f:
      json.dump(data, f)

@my_bot.command(pass_context=True)
async def tag(ctx, name, i):
   for j in ctx.message.author.roles:
      if (j.name == 'JuiceBot Commander'):
         if (int(i)>20):
            return await my_bot.say('No that\'s too much')
         if (name=='@everyone' or name=='@here'):
            return await my_bot.say('No.')
         else:
            for i in range(int(i)):
               await my_bot.say(name)
               await asyncio.sleep(1)
         break;
   else:
      return await my_bot.say('You do not have the necessary role. !permissions for more info')

@my_bot.command()
async def permissions():
   return await my_bot.say('The JuiceBot Commander role lets you access admin commands.')

@my_bot.command(pass_context=True)
async def post(ctx, sub):
   if (sub=='meme'):
      meme_list=['me_irl', 'meirl', 'dankmemes']
      subreddit=reddit.subreddit(random.choice(meme_list))
   elif (sub=='nudes'):
      nsfw_list=['gonewild', 'realgirls', 'adorableporn', 'complexionexcellence', 'amateur']
      subreddit=reddit.subreddit(random.choice(nsfw_list))
   else:
      subreddit=reddit.subreddit(sub)
      
   posts=subreddit.hot(limit=70)
   random_post_number=random.randint(0, 70)
   posts=list(posts)
   post=posts[random_post_number]
   
   with open('servers.json', 'r') as f:
      data = json.load(f)
      
   if (post.over_18 and not data[ctx.message.server.id]):
      return await my_bot.say('NSFW content disabled !nsfw enable to revert this change')
      
   message='```'+'post from reddit.com/r/'+str(subreddit)+'```\n'+post.title+'\n'+post.url
   return await my_bot.say(message)

@my_bot.command(pass_context = True)
async def nsfw(ctx, state):
   for j in ctx.message.author.roles:
      if (j.name == 'JuiceBot Commander'):
         break;
   else:
      return await my_bot.say('You do not have the necessary role. !permissions for more info')

   with open('servers.json', 'r') as f:
      data = json.load(f)
      
   if (state == 'enable'):
      stateB = True
   elif (state == 'disable'):
      stateB = False
   else:
      return await my_bot.say('invalid state (enable/disable)')

   data[ctx.message.server.id] = stateB
         
   with open('servers.json', 'w') as f:
      json.dump(data, f)
   return await my_bot.say('NSFW successfully **%sd**'%state)
   
@my_bot.command()
async def makeitrain(sub, msg):
   subreddit=reddit.subreddit(sub)
   if (int(msg)>10):
      return await my_bot.say ('10 is the cap. Don\'t abuse me :(')
   posts=subreddit.hot(limit=int(msg))
   for post in posts:
      await my_bot.say(post.url)
      await asyncio.sleep(1)
   return

@my_bot.command()
async def diss(*name):
   if ('<@135122745884278785>' in name):
      return await my_bot.say('The god cannot be dissed')
   if ('@everyone' in name or '@here' in name):
      return await my_bot.say('No')
   names=''
   for i in name:
      names+=i+' '
      
   with open('insults.txt', 'r') as file:
      insult = file.readlines()
   random_index = random.randint(0,len(insult))
   message=names+' '+insult[random_index]
   file.close()
   return await my_bot.say(message)

@my_bot.command()
async def rate():
   return await my_bot.say(str(random.randint(0, 10))+'/10')

@my_bot.command()
async def magic8ball():
   return await my_bot.say(random.choice(['It is certain','It is decidedly so','Without a doubt','Yes definitely','You may rely on it','As I see it, yes','Most likely','Outlook good','Yes','Signs point to yes','Reply hazy try again','Ask again later','Better not tell you now','Cannot predict now','Concentrate and ask again','Don\'t count on it','My reply is no','My sources say no','Outlook not so good','Very doubtful']))

@my_bot.command()
async def servers():
   em = discord.Embed (title = 'The servers JuiceBot is in', description = str(len(my_bot.servers))+ ' servers', colour = 0x9932CC)
   for i in my_bot.servers:
      em.add_field(name = i.name, value = str(len(i.members))+ ' members', inline = True)
   return await my_bot.say(embed = em)

@my_bot.command(pass_context=True)
async def kick(ctx, member):
    for j in ctx.message.author.roles:
        if (j.permissions.administrator):
            break
    else:
        return await my_bot.say('You are not an administrator')

    if (member[:2] == '<@'):
        member = ctx.message.mentions[0]
    else:
        member = ctx.message.server.get_member_named(member)
        
    await bot.say("%s has been kicked"%member.name)
    return await my_bot.kick(member)

@my_bot.command(pass_context=True)
async def ban(ctx, member):
    for j in ctx.message.author.roles:
        if (j.permissions.administrator):
            break
    else:
        return await my_bot.say('You are not an administrator')

    if (member[:2] == '<@'):
        member = ctx.message.mentions[0]
    else:
        member = ctx.message.server.get_member_named(member)
        
    await bot.say("%s has been banned"%member.name)
    return await my_bot.ban(member)

@my_bot.command(pass_context=True)
async def unban(ctx, member):
    for j in ctx.message.author.roles:
        if (j.permissions.administrator):
            break
    else:
        return await my_bot.say('You are not an administrator')

    server = ctx.message.server
    
    if (member[:1] == '@'):
        member = member[:-1]
    bans = await my_bot.get_bans(server)
    
    for i in bans:
        if (i.name[:-5] == member or i.name == member):
            member = i
            break
        
    await bot.say("%s has been unbanned"%member.name)
    return await my_bot.unban(server, member)

@my_bot.command(pass_context = True)
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
    await my_bot.say('Thank you for the report, the admins will investigate if we keep getting negative feedback about the user')
      
    if (len(data[member.id]['reports'])==5):
        em = discord.Embed(title = 'User reports', description = 'for %s'%data[member.id]['name'], colour = 0x003087)
        for name, val in data[member.id]['reports'].items():
            em.add_field(name = name, value = val, inline=True)

        await my_bot.say('%s has 5 reports'%data[member.id]['name'], embed = em)
        data[member.id]['reports'] = {}
   
    with open ('reports.json', 'w') as f:
        json.dump(data, f)
    return
   
my_bot.run("<Discord API Token>")


