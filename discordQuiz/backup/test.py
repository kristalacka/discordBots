import discord
from discord.ext.commands import Bot

bot = Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    
@bot.command()
async def react():
    channel = bot.get_channel('359723004264972288')
    msg = await bot.send_message(channel, content = 'test')
    print(msg)
    await bot.add_reaction(msg, '✅')
    print(msg.reactions)
bot.run("MzQyMjQ0MTA5ODMyMTU5MjMz.DGMzWw.BZ4UjCHq-j4vEb_TjJXOocZSiC8")
