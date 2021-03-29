# bot.py
import time
import os # for importing env vars for the bot to use
import requests
from dotenv import load_dotenv
from twitchio.ext import commands
from twitchio.webhook import UserFollows
from dialogflow_bot import send_message
from random import choice
import yfinance as yf
import asyncio

load_dotenv()

bot = commands.Bot(
    # set up the bot
    irc_token=os.getenv('TMI_TOKEN'),
    client_id=os.getenv('CLIENT_ID'),
    nick=os.getenv('BOT_NICK'),
    prefix=os.getenv('BOT_PREFIX'),
    initial_channels=[os.getenv('CHANNEL')]
)


points_list = {}
active_timers = []
rest_timers = {}

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

def isint(var):
    try:
        int(var)
    except:
        return None
    return int(var)

async def timer_validation(ctx, time):
    if isint(time) is not None and no_current_timers(ctx):
        return True
    else:
        await ctx.send_privmsg(ctx.author.name, 'You currently have an active timer, !timer to check your timers')
        return False

@bot.command(name='btc')
async def btc(ctx):
    response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
    data = response.json()["bpi"]["USD"]["rate"]
    await ctx.send(f"BTC price rn: ${data}")

@bot.command(name='price')
async def btc(ctx, ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol.upper())
        todays_data = ticker.history(period='1d')
        price = todays_data['Close'][0]
    except:
        await ctx.send(f"@{ctx.author.name} {ticker_symbol.upper()} is not a valid ticker!")
        return
    await ctx.send(f"{ticker_symbol.upper()} price rn: ${round(price, 2)}")

@bot.command(name='study')
async def test(ctx, study_time=''):
    if await timer_validation(ctx, study_time):
        active_timers.append((ctx.author.name, time, "study"))
        await ctx.send(f'@{ctx.author.name} has started studying for {study_time} minutes!')
        await asyncio.sleep(int(study_time))
        await ctx.send(f'time up!')

@bot.command(name='givepoints')
async def givepoints(ctx, user, value):
    if ctx.author.name == "00mb1" and isint(value) is not None:
        if user in points_list.keys():
            points_list[user] += isint(value)
        else:
            points_list[user.lower()] = int(value)
            await ctx.send(f'Added {value} points to {user.lower()}')

@bot.command(name='pointsboard')
async def pointsboard(ctx):
    await ctx.send(points_list)

@bot.command(name='botme')
async def what(ctx, *tags):
    if tags:
        await ctx.send(f"@{ctx.author.name} {send_message(' '.join(tags))}")

@bot.command(name='rps')
async def rps(ctx, user_choice):
    choices = ["rock","paper","scissors"]
    if user_choice in choices:
        bot_choice = choice(choices)
        if bot_choice == user_choice:
            await ctx.send(f"I chose {bot_choice}, it was a draw!")
        elif (user_choice == "rock" and bot_choice == "scissors") or (user_choice == "paper" and bot_choice == "rock") or (user_choice == "scissors" and bot_choice == "paper"):
            await ctx.send(f"I chose {bot_choice}, you win!")
        else:
            await ctx.send(f"I chose {bot_choice}, I win!")


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