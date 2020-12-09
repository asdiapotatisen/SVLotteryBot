import discord
import math
import asyncio
import random
import json
import os
import requests
from datetime import datetime
from discord.ext import commands

client = commands.Bot(command_prefix='!', help_command=None, case_insensitive=True)


creditsperticket = 0
baseprize = 0
announcement_channel = 0
roleid = 0
profitpercent = 0
hostsvid = 0
drawtime = ''

deadlinehere = False

def keys_exists(element, *keys):
    if not isinstance(element, dict):
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        raise AttributeError('keys_exists() expects at least two arguments, one given.')
    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True

def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)

embedhelpmain = discord.Embed(title='Help Menu: Main')
embedhelpmain.add_field(name='Admin', value='Commands for Lottery Admins. You must have the "Lottery Bot Admin" role to be considered a Lottery Admin. (`!help admin`).')
embedhelpmain.add_field(name='User', value='Commands for Lottery Users (`!help user`).', inline=False)

embedhelpadmin = discord.Embed(title='Help Menu: Admin')
embedhelpadmin.add_field(name='sethost', value="""Sets the SVID of the Lottery Host.
`!sethost [svid of host]`""", inline=False)

embedhelpadmin.add_field(name='setprize', value="""Sets the base prize of the lottery. Measured in credits.
`!setprize [base prize]`""", inline=False)

embedhelpadmin.add_field(name='setprofit', value="""Sets the percentage you want to take from the earnings of the lottery. Must not be above 100. Measured in credits.
`!setprofit [percentage taken]`""", inline=False)

embedhelpadmin.add_field(name='setprice', value="""Sets the price per lottery ticket. Measured in credits.
`!setprice [price per ticket]`""", inline=False)

embedhelpadmin.add_field(name='setdrawtime', value="""Sets lottery draw time in DD/MM/YY format.
`!setdrawtime [draw time]`""", inline=False)

embedhelpadmin.add_field(name='setchannel', value="""Sets the channel where the winner will be announced. Channel name must be exact.
`!setchannel [channel name]`""", inline=False)

embedhelpadmin.add_field(name='pickwinner', value="""Picks a winner. Announcement will be sent in the lottery announcement channel.
`!pickwinner`""", inline=False)

embedhelpuser = discord.Embed(title='Help Menu: User')

embedhelpuser.add_field(name='info', value="""View lottery settings
`!info`""", inline=False)

embedhelpuser.add_field(name='register', value="""Registers an account
`!register`""", inline=False)

embedhelpuser.add_field(name='account', value="""View your ticket count.
`!account`""", inline=False)

embedhelpuser.add_field(name='pay', value="""Initiates the payment process. **ALWAYS DO THIS BEFORE PAYING THE HOST.** Measured in credits.
`!pay [amount]`""", inline=False)

embedhelpuser.add_field(name='total', value="""Views top 10 users with highest ticket count and current prize pool.
`!total`""", inline=False)

@client.command(name='help')
async def help(ctx, *category):
    if len(category) == 0:
        await ctx.send(embed=embedhelpmain)
    if len(category) > 0:
        catstr = "".join(category)
        if catstr == "admin":
            await ctx.send(embed=embedhelpadmin)
        elif catstr == "user":
            await ctx.send(embed=embedhelpuser)
        else:
            await ctx.send("Category not recognised")

# DM server owner on join, create bot role
@client.event
async def on_guild_join(guild):
    role = await guild.create_role(name="Lottery Bot Admin")
    global roleid
    roleid = role.id

# Configure lottery
@client.command(name='sethost')
async def host(ctx, svid):
    global hostsvid
    role = discord.utils.get(ctx.guild.roles, id=roleid)
    if role in ctx.author.roles:
        try:
            result = requests.get(f"https://api.spookvooper.com/group/getname?svid={svid}").text
        except:
            try:
                result = requests.get(f"https://api.spookvooper.com/user/getusername?svid={svid}").text
            except:
                await ctx.send("That SVID is invalid.")
            else:
                hostsvid = result
        else:
            hostsvid = result
    else:
        await ctx.send("You do not have the permission to configure the lottery settings.")

@client.command(name='setprize')
async def setprize(ctx, amount):
    global baseprize
    role = discord.utils.get(ctx.guild.roles, id=roleid)
    if role in ctx.author.roles:
        if deadlinehere == True:
            try:
                baseprize = float(amount)
                await ctx.send(f'Base prize set to {baseprize}.')
            except TypeError:
                await ctx.send("Prize must be a number.")
        else:
            await ctx.send("Lottery has already started.")
    else:
        await ctx.send("You do not have the permission to configure the lottery settings")

@client.command(name='setprofit')
async def setprofit(ctx, percentage):
    global profitpercent
    role = discord.utils.get(ctx.guild.roles, id=roleid)
    if role in ctx.author.roles:
        if deadlinehere == True:
            try:
                profitpercent = float(percentage)
                if profitpercent > 100:
                    profitpercent = 0
                    await ctx.send("Profit cannot be above 100%")
                else:
                    await ctx.send(f'Profit set to {percentage}.')
            except TypeError:
                await ctx.send("Percentage must be a number.")
        else:
            await ctx.send("Lottery has already started.")
    else:
        await ctx.send("You do not have the permission to configure the lottery settings")

@client.command(name='setprice')
async def setprice(ctx, amount):
    global creditsperticket
    role = discord.utils.get(ctx.guild.roles, id=roleid)
    if role in ctx.author.roles:
        if deadlinehere == True:
            try:
                creditsperticket = float(amount)
                await ctx.send(f'Price set to {creditsperticket} per ticket.')
            except TypeError:
                await ctx.send("Price must be a number.")
        else:
            await ctx.send("Lottery has already started.")
    else:
            await ctx.send("You do not have the permission to configure the lottery settings.")

@client.command(name='setdrawtime')
async def setdrawtime(ctx, time):
    global drawtime
    role = discord.utils.get(ctx.guild.roles, id=roleid)
    if role in ctx.author.roles:
        if deadlinehere == True:
            drawtime = ctx.message.content
            await ctx.send(f'Drawtime set to {drawtime}.')
        else:
            await ctx.send("Lottery has already started.")
    else:
            await ctx.send("You do not have the permission to configure the lottery settings")

@client.command(name='setchannel')
async def setchannel(ctx, name):
    global announcement_channel
    role = discord.utils.get(ctx.guild.roles, id=roleid)
    if role in ctx.author.roles:
        if deadlinehere == True:
            channel = discord.utils.get(ctx.guild.channels, name=name)
            announcement_channel = channel.id
            await ctx.send(f'Channel set.')
        else:
            await ctx.send("Lottery has already started.")
    else:
        await ctx.send("You do not have the permission to configure the lottery settings")

# Start lottery
@client.command(name='startlottery')
async def start(ctx):
    global deadlinehere
    role = discord.utils.get(ctx.guild.roles, id=roleid)
    if role in ctx.author.roles:
        if deadlinehere == True:
            deadlinehere = False
            await ctx.send("Lottery started")
        else:
            await ctx.send("Lottery has already started.")
    else:
        await ctx.send("You do not have the permission to start a lottery")

# During lottery
@client.command(name='info')
async def info(ctx):
    embedinfo = discord.Embed(title='Lottery Info')
    embedinfo.add_field(name='Host', value=f"{hostsvid}", inline=False)
    embedinfo.add_field(name='Price', value=f"{creditsperticket} credits per ticket", inline=False)
    embedinfo.add_field(name='Draw Time', value=f"{drawtime} (DD/MM/YY)", inline=False)

@client.command(name='register')
async def register(ctx):
    if deadlinehere == False:
        svid = requests.get(f"https://api.spookvooper.com/User/GetSVIDFromDiscord?discordid={ctx.author.id}").text
        with open('lottery.txt') as infile:
            lotterylist = json.load(infile)
        if keys_exists(lotterylist, svid):
            await ctx.send('You have already registered.')
        else:
            lotterylist[svid] = 0
            blank = ""
            with open('lottery.txt', 'w') as outfile:
                json.dump(blank, outfile, indent=2)
            with open('lottery.txt', 'w') as outfile:
                json.dump(lotterylist, outfile, indent=2)
            await ctx.send('Successfully registered.')
    else:
        await ctx.send("Lottery has ended.")
        
@client.command(name='account')
async def account(ctx):
    if deadlinehere == False:
        user = ctx.message.author
        svid = requests.get(f"https://api.spookvooper.com/User/GetSVIDFromDiscord?discordid={ctx.author.id}").text
        with open('lottery.txt') as infile:
            lotterylist = json.load(infile)
        if keys_exists(lotterylist, svid):
            balance = lotterylist[svid]
            embedaccount = discord.Embed(title=user.name)
            embedaccount.add_field(name='Balance', value=balance)
            await ctx.send(embed=embedaccount)
        else:
            await ctx.send("Please register an account first.")
    else:
        await ctx.send("Lottery has ended.")
        
@client.command(name='pay')
async def pay(ctx, amount):
    if deadlinehere == False:
        try:
            user = ctx.message.author
            svid = requests.get(f"https://api.spookvooper.com/User/GetSVIDFromDiscord?discordid={ctx.author.id}").text
            await ctx.send(f'Please pay {hostsvid} in the next 30 seconds. 1 ticket = {creditsperticket} credits')
            userbalance = float(requests.get(f"https://api.spookvooper.com/Eco/GetBalance?svid={svid}").text)
            hostbalance = float(requests.get(f"https://api.spookvooper.com/Eco/GetBalance?svid={hostsvid}").text)
            await asyncio.sleep(30)
            userbalance2 = float(requests.get(f"https://api.spookvooper.com/Eco/GetBalance?svid={svid}").text)
            hostbalance2 = float(requests.get(f"https://api.spookvooper.com/Eco/GetBalance?svid={hostsvid}").text)
            userlost = userbalance - userbalance2 # positive
            hostgain = hostbalance2 - hostbalance # positive
            if hostgain <= 0:
                await ctx.send("No payment was detected.")
            else:
                if userlost < float(amount):
                    await ctx.send(f"Something went wrong! Please contact a lottery admin.")
                elif hostgain < float(amount):
                    await ctx.send(f"Something went wrong! Please contact a lottery admin.")
                else:
                    newtickets = int(hostgain) / creditsperticket
                    newticketsround = math.floor(newtickets)
                    with open("lottery.txt") as infile:
                        lotterylist = json.load(infile)
                    balance = lotterylist[svid]
                    newbalance = balance + newticketsround
                    lotterylist[svid] = newbalance
                    embedpay = discord.Embed(title=user.name)
                    embedpay.add_field(name='Balance', value=newbalance)
                    await ctx.send(embed=embedpay)
                    with open('lottery.txt') as outfile:
                        json.dump(lotterylist, outfile)
        except TypeError:
            await ctx.send("Amount must be a number.")
    else:
        await ctx.send("Lottery has ended.")

@client.command(name='total')
async def total(ctx):
    if deadlinehere == False:
        async with ctx.typing():
            with open('lottery.txt') as infile:
                lotterylist = json.load(infile)
            keys = list(lotterylist.keys())
            sortedkeys = sorted(keys)
            embedinfo = discord.Embed(title='Info')
            totaltickets = 0
            for i in range(0, len(keys)):
                svid = keys[i]
                name = requests.get(f"https://api.spookvooper.com/User/GetUsername?SVID={svid}").text
                balance = lotterylist[svid]
                totaltickets += balance
            for i in range(0, 11):
                try:
                    svid = sortedkeys[i]
                    name = requests.get(f"https://api.spookvooper.com/User/GetUsername?SVID={svid}").text
                    balance = lotterylist[svid]
                    embedinfo.add_field(name=name, value=f'{balance} tickets', inline=False)
                except IndexError:
                    break
            embedinfo.add_field(name='Total Tickets', value=f"{totaltickets} tickets", inline=False)
            embedinfo.add_field(name='Prize Pool', value=f"{(totaltickets * 10) * ((100-profitpercent)/100) + baseprize} credits", inline=False)
            await ctx.send(embed=embedinfo)
    else:
        await ctx.send("Lottery has ended.")

# End lottery
@client.command(name='pickwinner')
async def pickwinner(ctx):
    global deadlinehere
    role = discord.utils.get(ctx.guild.roles, id=roleid)
    if role in ctx.author.roles:
        if deadlinehere == False:
            with open('lottery.txt') as infile:
                lotterylist = json.load(infile)
            keys = list(lotterylist.keys())
            values = list(lotterylist.values())
            totaltickets = 0
            for i in range(0, len(values)):
                totaltickets += values[i]
            weight = []
            for i in range(0, len(values)):
                weight.append(values[i] / totaltickets)
            winner = random.choices(population=keys, weights=weight, k=1)[0]
            channel = client.get_channel(announcement_channel)
            username = requests.get(f"https://api.spookvooper.com/User/GetUsername?SVID={winner}").text
            data = json.loads(requests.get(f"https://api.spookvooper.com/User/GetUser?SVID={winner}").text)
            discordid = data['discord_id']
            await channel.send(f'{username} (<@{discordid}>) has won the lottery!')
            os.remove("lottery.txt")
            deadlinehere = True
        else:
            await ctx.send("Lottery has ended.")
    else:
        await ctx.send("You do not have the permission to end the lottery.")

client.run('BOT_TOKEN')
