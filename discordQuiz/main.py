import discord, asyncio, json, logging, random
from discord.ext.commands import Bot
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dateutil.parser import parse
from datetime import datetime, timedelta

sched = AsyncIOScheduler()
logging.basicConfig(level = logging.INFO)
bot = Bot(command_prefix='!')
quiz ={
    '0You are getting ready to post some NSFW material. What should you do?\n1. Ask a Helper first.\n2. Post it in the NSFW channel.\n3. Don’t post it at all.\n4. Post it in the general chat.': '3',
    '1Somebody is being a real jerk. What do you do?\n1. Give them a taste of their own medicine.\n2. Tell a Helper or Me.\n3. Ignore them.\n4. Spam Emojis to express frustration. ': '2',
    '2Somebody has posted a really bad piece and is asking for opinions. What do you do? \n1. Teach them how to improve.\n2. Tell them that they are horrible. \n3. Make fun of their work. \n4. Ignore them and offer no help. ': '1',
    '3Somebody is being an annoying spammer. What do you do?\n1. Keep asking them to stop. \n2. Tell a Helper or Me.\n3. Curse at them. \n4. Join them. ': '2',
    '4There’s a political event that you want to talk about. What do you do? \n1. Begin talking about it. \n2. Express your views in a rude manner. \n3. Don’t say anything about it. Talk about something else instead.\n4. Begin fighting with another user over it.': '3',
    '5Two users are fighting and being rude. What do you do? \n1. You report them to Me or tell a Helper.\n2. You ask them to stop in a rude way. \n3. You take a side and join the fight. \n4. You ignore it and don’t do anything. ': '1'
    }
corrResponses = ['That’s right! This server has a strict NSFW ban. Please keep it clean and friendly! ', 'Correct! When someone’s being a jerk tell someone who can do something about it. I’m always able to help if many people report one person. ', 'Right! Dabble is all about learning and improving skills, not hurting other people. So don’t be afraid to share your two cents. ', 'Yup! Always be sure to tell Helpers or Me about a person who’s spamming. They will most likely be banned.', 'Correct! While you always have a right to your opinions, Dabble is not the place to share them when it comes to controversial topics such as politics.', 'Right! When there is a conflict in Dabble always be sure to notify the helpers or report the users to me. ']

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
        if (i.name.lower() == 'joining'):
            break;
    else:
        await bot.create_role(server, name = 'joining')

    for i in server.roles:
        if (i.name.lower() == 'restricted'):
            break;
    else:
        await bot.create_role(server, name = 'restricted')

    new_data = {str(server.id): {'lockdown': False}}
    with open('serverState.json', 'r') as f:
        data = json.load(f)

    data.update(new_data)
    with open('serverState.json', 'w') as f:
        json.dump(data, f)

async def give_role(member):
    for i in member.server.roles:
        if (i.name.lower() == 'community'):
            new_role = i
    try:
        return await bot.replace_roles(member, new_role)
    except:
        return
    
@bot.event
async def on_member_join(member):
    with open('serverState.json', 'r') as f:
        data = json.load(f)
    
    if (data[member.server.id]['lockdown']):
        return await bot.kick(member)
    
    for i in member.server.roles:
        if (i.name.lower() == 'joining'):
            role = i
            break
        
    await bot.replace_roles(member, role)
    await bot.start_private_message(member)
    rules = await bot.send_message(member, content = 'Hello there, my name is Waffles and I’m here to help you get started on this server! Dabble is aiming to be a great community to share talents and have fun. Please read through the rules so you can have idea of what the community expects of you. When you’ve read carefully through the rules just say \'start\' (without quotes) to proceed.')
    await bot.wait_for_message(timeout=300, content='start')
    await bot.send_message(member, content = 'Nice! Now that you’ve read the rules I’ve got a special surprise for you. A pop quiz! Didn’t expect that did you ;)')
    await bot.delete_message(rules)
    questions = random.sample(quiz.keys(), 3)
    def notBot(m):
        return m.author != bot.user
    
    for q in questions:
        await bot.send_message(member, content = q[1:])
        answer = await bot.wait_for_message(timeout=300, check = notBot)
        if (answer.content.lower()!=quiz[q]):
            await bot.send_message(member, content = 'Whoops looks like you missed one! Are you sure you read the rules? You can retake the quiz at any time by pressing this link, https://discord.gg/HwqKKB7')
            return await bot.kick(member)
        await bot.send_message(member, content = corrResponses[int(q[0])])
    else:
        await bot.send_message(member, content = 'Wow! Looks like you read all the rules. Don’t forget to check out all the channels to get more information and stay up to date on the server. Welcome to Dabble!')
        for i in member.server.roles:
            if (i.name.lower() == 'new'):
                roleN = i
                break
        await bot.replace_roles(member, roleN)
        sched.add_job(give_role, 'date', run_date = datetime.now()+timedelta(weeks=1), args=[member]) 
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

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()

class Music:
    """Voice related commands.
    Works in multiple servers at once.
    """
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel : discord.Channel):
        """Joins a voice channel."""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('Already in a voice channel...')
        except discord.InvalidArgument:
            await self.bot.say('This is not a voice channel...')
        else:
            await self.bot.say('Ready to play audio in ' + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('You are not in a voice channel.')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song : str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('Enqueued ' + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value : int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('Set the volume to {:.0%}'.format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pauses the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('Not playing any music right now...')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say('Requester requested skipping song...')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.bot.say('Skip vote passed, skipping song...')
                state.skip()
            else:
                await self.bot.say('Skip vote added, currently at [{}/3]'.format(total_votes))
        else:
            await self.bot.say('You have already voted to skip this song.')

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        """Shows info about the currently played song."""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('Not playing anything.')
        else:
            skip_count = len(state.skip_votes)
            await self.bot.say('Now playing {} [skips: {}/3]'.format(state.current, skip_count))


bot.add_cog(Music(bot))
    
sched.start()
bot.run("<Discord API Token>")
