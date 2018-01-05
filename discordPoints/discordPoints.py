import discord, gspread
from discord.ext.commands import Bot
from oauth2client.service_account import ServiceAccountCredentials

bot = Bot(command_prefix = '-')

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return len(str_list)+1

@bot.event
async def on_ready():
   print('Logged in as')
   print(bot.user.name)
   print(bot.user.id)

@bot.command(pass_context = True)
async def add(ctx, name, site):
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('discordPointsBot').sheet1
    names = sheet.col_values(1)
    if (str(ctx.message.author) in names):
        for i, name in enumerate(names):
            if (name==str(ctx.message.author)):
                nr = i+1
                break;
        sheet.update_cell(nr, 4, int(sheet.cell(nr, 4).value)+1)
    else:
        row_nr = next_available_row(sheet)
        row = [ctx.message.author, name, site, 1]
        cell_list = sheet.range('A%s:D%s'%(row_nr, row_nr))
        for i, cell in enumerate(cell_list):
            try:
                cell.value=row[i]
            except:
                break
            
        sheet.update_cells(cell_list)
    return await bot.say('Your point has been added, if you have any questions, message @Overlaugh')

bot.run("<Discord API Token>")
