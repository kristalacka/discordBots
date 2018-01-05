import discord, json, asyncio, requests, smtplib, random, string
from paypal import PayPalInterface
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from discord.ext.commands import Bot

bot = Bot(command_prefix='!')
notifChannel='<channel ID>'
serverID='<server ID>'
paypal_api = PayPalInterface(API_USERNAME="<paypal api username>",
                             API_PASSWORD="<paypal api password>",
                             API_SIGNATURE="<paypal api signature>",
                             DEBUG_LEVEL=0,
                             HTTP_TIMEOUT=30)

@bot.event
async def on_ready():
   print('Logged in as')
   print(bot.user.name)
   print(bot.user.id)

async def send_mail(code, email):
   msg = MIMEText('<message contents> %s'%code)
   msg['From'] = '<from email>'
   msg['To'] = email
   msg['Subject'] = '<message subject>'
   mail = smtplib.SMTP('smtp.gmail.com', 587)
   mail.ehlo()
   mail.starttls()
   mail.login('<from email>', '<password>')
   mail.send_message(msg)
   mail.quit
   return

def rand_code():
   with open('codes.json', 'r') as f:
      used_codes = json.load(f)

   code = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(16))
   if code in used_codes['used']:
      code = rand_code() #recursive regeneration of codes if code has been used
   else:
      return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(16))

async def background():
   await bot.wait_until_ready()
   code = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(10))
   while not bot.is_closed:
      date_end = datetime.utcnow()
      date_start = date_end-timedelta(seconds = 60)
      date_start = date_start.strftime('%Y-%m-%dT%H:%M:%SZ')
      transactions = paypal_api._call('TransactionSearch',
                                STARTDATE=date_start,
                                STATUS="Success")
      transIds = []
      for key, item in transactions.items():
         if (key[:15]=='L_TRANSACTIONID'):
            transIds.append(item)

      for i in transIds:
         info = paypal_api._call('GetTransactionDetails',
                                 TRANSACTIONID=i)
        
         em = discord.Embed(title = 'New %s %s donation!'%(info['AMT'], info['CURRENCYCODE']), description = 'from %s %s'%(info['FIRSTNAME'], info['LASTNAME']), colour = 0x003087)
         em.set_footer(text = 'PayPal transaction', icon_url = 'https://www.paypalobjects.com/webstatic/icon/pp258.png')
         em.add_field(name = 'Email', value = info['EMAIL'], inline = True)
         em.add_field(name = 'Value', value = '%s %s'%(info['AMT'], info['CURRENCYCODE']), inline = True)
         em.add_field(name = 'Country', value = info['COUNTRYCODE'], inline = True)
         em.add_field(name = 'Transaction ID', value = i, inline = True)
         await bot.send_message(bot.get_channel(notifChannel), embed = em)

         code = rand_code() #random 16 character code
         with open ('codes.json', 'r') as f:
            data = json.load(f)
         data['unused'].append(code)
         with open ('codes.json', 'w') as f:
            json.dump(data, f)
         await send_mail(code, info['EMAIL'])  
      await asyncio.sleep(60)

@bot.command(pass_context=True)
async def claimrole(ctx, code):
   if not ctx.message.channel.is_private:
      return await bot.say('Command only available in private messages')

   server = bot.get_server(serverID)
   member = server.get_member(ctx.message.author.id)
   
   with open ('codes.json', 'r') as f:
      data = json.load(f)

   if code not in data['unused']:
      return await bot.say('Invalid code')

   data['unused'].remove(code)
   for i in server.roles:
      if (i.name=='Donator'):
         role = i
         break

   data['used'].append(code)
   with open('codes.json', 'w') as f:
      json.dump(data, f)

   await bot.send_message(bot.get_channel(notifChannel), content = ('%s (%s) has claimed the code %s'%(member.name, member.mention, code)))
   await bot.send_message(member, content = 'You have successfully claimed the code!')
   return await bot.add_roles(member, role)
        
@bot.command(pass_context = True)
async def warn(ctx, member, *args):
   for i in ctx.message.author.roles:
      if (i.permissions.administrator):
         break
   else:
      return await bot.say('You are not an admin')
   
   message = ''
   if (member[:2] == '<@'):
      member = ctx.message.mentions[0]
   else:
      member = ctx.message.server.get_member_named(member)
      
   for i in args:
      message+=i+' '
   message = message[:-1]
      
   with open ('warnings.json', 'r') as f:
      data = json.load(f)

   if (member.id not in data.keys()):
      data.update({member.id: [message]})
   else:
      data[member.id].append(message)
      
   if (len(data[member.id])==3):
      await bot.kick(member)
      data[member.id]=[]
   
   with open ('warnings.json', 'w') as f:
      json.dump(data, f)

bot.loop.create_task(background())
bot.run("<discord token>")
