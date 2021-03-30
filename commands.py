# Developers - twitch.tv/00mb1

# Index:
# 00 - Setup
# 01 - Validation
# 02 - Finance
# 03 - Pomodoro
# 04 - Points
# 05 - Games
# 06 - Misc

import os
from typing import NoReturn
import requests
from dotenv import load_dotenv
from twitchio.ext import commands
from twitchio.webhook import UserFollows
from dialogflow_bot import send_message
from random import choice
from pomo_logic import pomo
import yfinance as yf
import asyncio
import sqlite3
load_dotenv()

#00 - Setup
timers = pomo()
con = sqlite3.connect('users.db')
cur = con.cursor()
mods_list = os.getenv('MODS_LIST').split(",")

bot = commands.Bot(
    irc_token=os.getenv('TMI_TOKEN'),
    client_id=os.getenv('CLIENT_ID'),
    nick=os.getenv('BOT_NICK'),
    prefix=os.getenv('BOT_PREFIX'),
    initial_channels=[os.getenv('CHANNEL')]
)

@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f"{os.environ['BOT_NICK']} is online!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(os.environ['CHANNEL'], f"/me has landed!")


#01 - Validation
def isint(var):
    try:
        int(var)
    except:
        return None
    return int(var)

@bot.event
async def timer_validation(ctx, time):
    if isint(time):
        if int(time) < 5 or int(time) > 60:
            await ctx.send(f"{ctx.author.name} You can't study/break for that amount of time, please choose a different time!")
        elif not None and timers.get_timer(ctx.author.name) is None:
            return True
        else:
            await ctx.send(f"{ctx.author.name} You currently have an active timer, !timer to check your timers")
    return False

#02 - Finance
@bot.command(name='btc')
async def btc(ctx):
    response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
    data = response.json()["bpi"]["USD"]["rate"]
    await ctx.send(f"{ctx.author.name} BTC price rn: ${data}")

@bot.command(name='price')
async def btc(ctx, ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol.upper())
        todays_data = ticker.history(period='1d')
        price = todays_data['Close'][0]
    except:
        await ctx.send(f"{ctx.author.name} {ticker_symbol.upper()} is not a valid ticker!")
        return
    await ctx.send(f"{ctx.author.name} {ticker_symbol.upper()} price rn: ${round(price, 2)}")


#03 - Pomodoro
@bot.command(name='cancel')
async def cancel(ctx):
    if timers.cancel_timer(ctx.author.name):
        await ctx.send(f"{ctx.author.name} Removed timer")
    else:
        await ctx.send(f"{ctx.author.name} No current timers")

@bot.command(name='study')
async def study(ctx, study_time=''):
    user = ctx.author.name.lower()
    if await timer_validation(ctx, study_time):
        await ctx.send(f'{ctx.author.name} has started studying for {study_time} minutes!')
        timers.set_timer(user, study_time, "study")
        await asyncio.sleep(int(study_time))
        if timers.get_timer(user) is not None:
            await ctx.send(f'{ctx.author.name} time up! Good work you earned {int(study_time)*10} points, take a break with !break')
            user_found = checkdb(user)
            if user_found is None:
                await adduser(user)
            cur.execute("UPDATE USERS SET points = ? WHERE name = ?", ((int(study_time)*10)+int(user_found[1]), user))
            con.commit()
            timers.cancel_timer(user)

@bot.command(name='break')
async def study(ctx, break_time=''):
    user = ctx.author.name.lower()
    if await timer_validation(ctx, break_time):
        await ctx.send(f'Okay {ctx.author.name}, see you in {break_time} minutes!')
        timers.set_timer(ctx.author.name, break_time, "study")
        await asyncio.sleep(int(break_time))
        if timers.get_timer(ctx.author.name) is not None:
            await ctx.send(f'{ctx.author.name} time up! You earned {int(break_time)*2} points, get back to work with !study')
            user_found = checkdb(user)
            if user_found is None:
                await adduser(user)
            cur.execute("UPDATE USERS SET points = ? WHERE name = ?", ((int(break_time)*2)+int(user_found[1]), user))
            con.commit()
            timers.cancel_timer(ctx.author.name)
            

@bot.command(name='timer')
async def timer(ctx):
    if timers.get_timer(ctx.author.name) is not None:
        time_left = timers.time_left(ctx.author.name)
        if time_left < 1:
            await ctx.send(f"{ctx.author.name} You have less than 1 minute left on your timer")
        else:
            await ctx.send(f"{ctx.author.name} You have {time_left} minutes left on your timer")
    else:
        await ctx.send(f"{ctx.author.name} You have no current timers")

@bot.command(name="grinders")
async def grinders(ctx):
    timer_array = timers.active_timers
    message = f"{ctx.author.name} People studying: "
    for user in timer_array:
        if user[2] == "study":
            message += user[0]+" "
    if message == f"{ctx.author.name} People studying: ":
        message = f"{ctx.author.name} Nobody is studying, be the first!"
    await ctx.send(message)

@bot.command(name="sleepers")
async def grinders(ctx):
    timer_array = timers.active_timers
    message = f"{ctx.author.name} Taking a break: "
    for user in timer_array:
        if user[2] == "break":
            message += user[0]+", "
    if message == f"{ctx.author.name} Taking a break: ":
        message = f"{ctx.author.name} Nobody is taking a break!"
    await ctx.send(message)


#04 - Points
def checkdb(user):
    cur.execute("SELECT * FROM USERS WHERE name = ?", (user,))
    rows = cur.fetchall()
    if rows == []:
        return
    return rows[0]

@bot.command(name='adduser')
async def adduser(ctx, user):
    if ctx.author.name not in mods_list:
        await ctx.send("unauthorized")
        return
    user = user.lower()
    user_found = checkdb(user)
    if user_found is not None:
        await ctx.send(f"{user} is already in the database")
    else:
        cur.execute(f"INSERT INTO USERS VALUES (?, 0)", (user,))
        await ctx.send(f"successfully added {user}")

@bot.command(name='deleteuser')
async def deleteuser(ctx, user):
    if ctx.author.name != "00mb1":
        await ctx.send("unauthorized")
        return
    user = user.lower()
    user_found = checkdb(user)
    if user_found is not None:
        cur.execute(f"DELETE FROM USERS WHERE NAME = ?", (user,))
        await ctx.send(f"successfully removed {user}")
    else:
        await ctx.send(f"{user} is not in the database")

@bot.command(name='setpoints')
async def setpoints(ctx, user, value):
    user = user.lower()
    if ctx.author.name in mods_list and isint(value) is not None:
        value = int(value)
        user_found = checkdb(user)
        if user_found is None:
            await ctx.send(f'{user} is not found, use !adduser to add a new user')
        else:
            cur.execute(f"UPDATE USERS SET points = ? WHERE name = ?", (value, user))
            con.commit()
            await ctx.send(f'Set {user} points to {value}')

@bot.command(name='addpoints')
async def addpoints(ctx, user, value):
    if ctx.author.name in mods_list and isint(value) is not None:
        value = int(value)
        user = user.lower()
        user_found = checkdb(user)
        if user_found is None:
            await ctx.send(f'{user} is not found, use !adduser to add a new user')
        else:
            cur.execute("UPDATE USERS SET points = ? WHERE name = ?", (value+int(user_found[1]), user))
            con.commit()
            await ctx.send(f'Added {value} points to {user}')

@bot.command(name='removepoints')
async def removepoints(ctx, user, value):
    if ctx.author.name in mods_list and isint(value) is not None:
        value = int(value)
        user = user.lower()
        user_found = checkdb(user)
        if user_found is None:
            await ctx.send(f'{user} is not found, use !adduser to add a new user')
        elif user_found[1] - int(value) < 0:
            cur.execute("UPDATE USERS SET points = ? WHERE name = ?", (0, user))
            con.commit()
        else:
            cur.execute("UPDATE USERS SET points = ? WHERE name = ?", (int(user_found[1])-value, user))
            con.commit()
        await ctx.send(f'Removed {value} points from {user}')

@bot.command(name='points')
async def points(ctx):
    user = ctx.author.name.lower()
    user_found = checkdb(user)
    if ctx.author.name.lower() in user_found:
        await ctx.send(f"{user}, you currently have {user_found[1]} points")

@bot.command(name='leaderboard')
async def leaderboard(ctx):
    cur.execute("SELECT * FROM USERS ORDER BY POINTS DESC")
    points_list = cur.fetchall()[0:10]
    string = "Top 10 Points: "
    for x in range(len(points_list)):
        string += f"{str(x+1)}. {points_list[x][0]} ({points_list[x][1]}), "
    string = string[:-2] + "."
    await ctx.send(string)

@bot.command(name='position')
async def position(ctx):
    cur.execute("SELECT * FROM USERS ORDER BY POINTS DESC")
    points_list = cur.fetchall()
    string = "Top 10 Points: "
    for x in range(len(points_list)):
        if points_list[x][0] == ctx.author.name.lower():
            await ctx.send(f"{ctx.author.name}, you are currently ranked: {x+1}")


#05 - Games
@bot.command(name='rps')
async def rps(ctx, user_choice):
    choices = ["rock","paper","scissors"]
    if user_choice in choices:
        bot_choice = choice(choices)
        if bot_choice == user_choice:
            await ctx.send(f"{ctx.author.name} I chose {bot_choice}, it was a draw!")
        elif (user_choice == "rock" and bot_choice == "scissors") or (user_choice == "paper" and bot_choice == "rock") or (user_choice == "scissors" and bot_choice == "paper"):
            await ctx.send(f"{ctx.author.name} I chose {bot_choice}, you win!")
        else:
            await ctx.send(f"{ctx.author.name} I chose {bot_choice}, I win!")


#06 - Misc
@bot.command(name='botme')
async def what(ctx, *tags):
    if tags:
        await ctx.send(f"{ctx.author.name} {send_message(' '.join(tags))}")


if __name__ == "__main__":
    bot.run()