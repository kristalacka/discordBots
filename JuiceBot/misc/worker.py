import discord, random, praw, asyncio

count = 0

from discord.ext.commands import Bot

my_bot = Bot(command_prefix="!")

reddit = praw.Reddit(client_id='gZbPvEUcPPHepw',
                     client_secret='JmzpEnSH-3z17wnYdRVMuUrekfM',
                     user_agent='Discord bot by /u/xxjuiceboxxx',
                     username='DCJuiceBot',
                     password='AwMiNoclan4f4')

@my_bot.event
async def on_ready():
   print('Logged in as')
   print(my_bot.user.name)
   print(my_bot.user.id)
   print('------')
   await my_bot.change_presence(game=discord.Game(name='type !info'))

@my_bot.command()
async def tag(name, i):
   if (int(i)>20):
      return await my_bot.say('No that\'s too much')
   if (name=='@everyone' or name=='@here'):
      return await my_bot.say('No.')
   else:
      for i in range(int(i)):
         await my_bot.say(name)
         await asyncio.sleep(1)

@my_bot.command()
async def post(sub):
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
   message='```'+'post from reddit.com/r/'+str(subreddit)+'```\n'+post.title+'\n'+post.url
   return await my_bot.say(message)

@my_bot.command()
async def makeitrain(msg):
   if (msg.author!='<@135122745884278785>'):
      return await my_bot.say('Not available publically yet')
   subreddit=reddit.subreddit('me_irl')
   posts=subreddit.hot(limit=int(msg))
   for post in posts:
      await my_bot.say(post.url)
      await asyncio.sleep(1)
   return

@my_bot.command()
async def diss(name):
   if (name=='<@135122745884278785>'):
      return await my_bot.say('The god cannot be dissed')
   if (name=='@everyone' or name=='@here'):
      return await my_bot.say('No')
   with open('insults.txt', 'r') as file:
      insult = file.readlines()
   random_index = random.randint(0,len(insult))
   message=name+' '+insult[random_index]
   file.close()
   return await my_bot.say(message)

@my_bot.command()
async def rate():
   return await my_bot.say(str(random.randint(0, 10))+'/10')

@my_bot.command()
async def info():
   em = discord.Embed(title = 'Invite the bot to your server', description = 'Join JuiceBot\'s server: https://discord.io/juicebot', url = 'https://discordapp.com/oauth2/authorize?client_id=297426108104572928&scope=bot&permissions=0', colour = 0x9932CC)
   em.add_field(name = '!tag <@name> <number>', value = 'tags a member the desired amount of times', inline = False)
   em.add_field(name = '!post <topic>', value = 'posts a hot submission from the desired subreddit', inline = False)
   em.add_field(name = '!diss <@name>', value = 'Fucks a bitch up', inline = False)
   em.add_field(name = '!rate', value = 'rates your nudes from 1 to 10', inline = False)
   em.set_author(name = 'JuiceBot', icon_url = my_bot.user.avatar_url)
   await my_bot.say(embed = em)

my_bot.run("Mjk3NDI2MTA4MTA0NTcyOTI4.C8Anyg.URBpSLG_I3TOMhP7CzSWWI6hToI")


