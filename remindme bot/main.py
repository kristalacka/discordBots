import logging, discord
from dateutil.parser import parse
from datetime import datetime
from discord.ext.commands import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sched = AsyncIOScheduler()
logging.basicConfig(level = logging.INFO)
client = Bot(command_prefix = '!')

async def reminder(channel, user, message, date):
    em = discord.Embed(title = str(date), description = message, colour = 0x4286f4)
    await client.send_message(channel, '%s reminding you of'%user, embed = em)

@client.event
async def on_ready():
    print('logged in')
    await client.change_presence(game = discord.Game(name = '!help'))

@client.event
async def on_message(message):
    if message.content.startswith('!remindme'):
        msg = message.content[10:]
        await client.send_message(message.channel, 'When would you like to be reminded of "%s"?'%msg)
        time = await client.wait_for_message(author = message.author)
        parsed_time = parse(time.content)
        
        if (parsed_time < datetime.now()):
            await client.send_message(message.channel, 'Beep. I cannot travel back in time, it is %s right now'%datetime.now())
        else:
            em = discord.Embed(title = 'OK. Reminding you on %s'%parsed_time, description = msg, colour = 0x4286f4)
            await client.send_message(message.channel, embed = em)
            sched.add_job(reminder, 'date', run_date = parsed_time, args = [message.channel, message.author.mention, msg, parsed_time])
            sched.start()

client.run('<Discord API Token>')
