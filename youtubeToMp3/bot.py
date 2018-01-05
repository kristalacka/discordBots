import discord, youtube_dl, os
from discord.ext.commands import Bot

bot = Bot(command_prefix = '.')
ydl_opts = {
	'outtmpl': u'%(title)s.%(ext)s',
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

@bot.event
async def on_ready():
	print(bot.user.name)
	print(bot.user.id)
	await bot.change_presence(game=discord.Game(name='.download'))

@bot.command(pass_context = True)
async def download(ctx):
	url = ctx.message.content[10:]
	try:
		info_dict = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'}).extract_info(url, download=False)
		video_title = info_dict.get('title', None)
		name = '%s.mp3'%(video_title)
		message = await bot.say('`Downloading %s`'%video_title)
	except:
		return await bot.say('`Error occured while processing your request, are you sure the link is correct?`')

	size = info_dict.get('duration', None)
	if (size>330):
		return await bot.say('`File size too large to post on discord. Current length limit is around 5 minutes.`')

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		try:
			ydl.download([url])
		except:
			return await bot.say('`Error occured while downloading the file.`')

	try:
		await bot.send_file(destination = ctx.message.channel, fp = 'C:/Users/Admin/Desktop/programming/youtube to mp3/%s'%name, content = '`%s has finished downloading!`'%video_title)
	except:
		await bot.say('`Error occured while attempting to send the file`')

	await bot.delete_message(message)
	os.remove(name)
	return

bot.run('<Discord API Token>')