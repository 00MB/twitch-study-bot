# bot.py
import os # for importing env vars for the bot to use
from dotenv import load_dotenv
from twitchio.ext import commands
from twitchio.webhook import UserFollows
from dialogflow_bot import send_message

load_dotenv()

bot = commands.Bot(
    # set up the bot
    irc_token=os.getenv('TMI_TOKEN'),
    client_id=os.getenv('CLIENT_ID'),
    nick=os.getenv('BOT_NICK'),
    prefix=os.getenv('BOT_PREFIX'),
    initial_channels=[os.getenv('CHANNEL')]
)

rest_timers = {}
study_timers = {}

@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f"{os.environ['BOT_NICK']} is online!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(os.environ['CHANNEL'], f"/me has landed!")

def no_current_timers(ctx):
    if ctx.author.name in rest_timers.keys() or ctx.author.name in rest_timers.keys():
        return False
    return True

async def timer_validation(ctx, time):
    try: 
        int(time)
    except:
        return False
    if no_current_timers(ctx):
        return True
    else:
        await ctx.send_privmsg(ctx.author.name, 'You currently have an active timer, !timer to check your timers')
        return False

@bot.command(name='study')
async def test(ctx, time=''):
    if await timer_validation(ctx, time):
        await ctx.send(f'@{ctx.author.name} has started studying for {time} minutes!')

@bot.command(name='botme')
async def what(ctx, *tags):
    if tags:
        print(type(tags))
        await ctx.send(f"@{ctx.author.name} {send_message(' '.join(tags))}")

if __name__ == "__main__":
    bot.run()


# @bot.event
# async def event_message(ctx):
#     'Runs every time a message is sent in chat.'

#     # make sure the bot ignores itself and the streamer
#     if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
#         return

#     await bot.handle_commands(ctx)

#     # await ctx.channel.send(ctx.content)

#     if 'hello' in ctx.content.lower():
#         await ctx.channel.send(f"Hi, @{ctx.author.name}!")