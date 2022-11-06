import os
import datetime
import random
import time
import User
import disnake
from enum import Enum
from collections import OrderedDict
from disnake.ext import commands
from dotenv import load_dotenv


load_dotenv()
token = os.getenv('TOKEN')

bot = commands.Bot(command_prefix=commands.when_mentioned)

uptime = time.time()
@bot.event
async def on_ready():
    print('Bot online')

users = {}


#Help command
@bot.slash_command(
    name="help",
    description="Complete directory of valid commands!",
)
async def help(inter):
    desc = "**/help** - Get this list, the list of all valid bot commands\n" + "**/scavenge** - Scavenge for some money\n" + "**/daily** - Claim your daily currency and gain a bonus for claiming multiple days in a row\n" + "**/steal** - Steal some money, but you risk being caught...\n" + "**/balance** - Check your current balance\n" + "**/coinflip** - Place a bet and toss a coin to determine your winnings\n" + "**/leaderboard** - Check the leaders of today\n" + "**/profile** - View the bot profile (bot info)\n" + "**/shop** - Access the shop and buy yourself some goodies! *Alias: /buy*\n" + "**/inventory** - See your materials inventory\n"  + "**/craft** - Craft items for multipliers using your available materials\n" + "**/items** - Your list of crafted items\n**/multi** - See your currency multiplier\n"

    embed = disnake.Embed(
        title="COMMANDS",
        color=disnake.Colour.yellow(),
        description=desc,
        timestamp=datetime.datetime.now()
    )
    await inter.send(embed=embed)

#scavenge command
@bot.slash_command(
    name="scavenge",
    description="Gain $10-$15. 2 minute cooldown.",
)
async def scavenge(inter):
    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)
    userVar = users[inter.user.id]
    val = int(random.randint(10, 15)*userVar.multi)

    #if on cooldown
    if time.time() - userVar.scav < 120:
        await inter.send(f"This command is on cooldown for another **{int(120-(time.time()-userVar.scav))} seconds**")
        return
    
    userVar.balance += val
    await inter.send(f"You found **${val}** while scavenging!")

    #command cooldown
    userVar.scav = time.time()


#daily command
@bot.slash_command(
    name='daily',
    description='Claim your daily currency. Gain a multiplier for claiming multiple days in a row!',
)
async def daily(inter):
    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)
    userVar = users[inter.user.id]

    #if on cooldown
    if time.time() - userVar.daily < 86400:
        timeS = int(86400-(time.time()-userVar.daily))
        timeM = timeS//60
        timeS %= 60
        timeH = timeM//60
        timeM %= 60
        await inter.send(f"This command is on cooldown for another **{timeH} hours {timeM} minutes and {timeS} seconds**")
        return
    
    if time.time() - userVar.daily > 172800 and userVar.dailyStreak != 0:
        await inter.send(f"2+ days have passed since you last used `/daily`! Your daily streak has been reset!\n\nYou claimed your daily **${int(350*userVar.multi)}**! You currently have a streak of 1 day!")
        userVar.dailyStreak = 1
        userVar.balance += int(350*userVar.multi)
        return

    userVar.dailyStreak+=1
    #reset streak if too much time passes
    val = 350
    for i in range(userVar.dailyStreak-1):
        val*=1.015
    val = int(val*userVar.multi)
    userVar.balance += val
    await inter.send(f"You claimed your daily **${val}**! You currently have a streak of {userVar.dailyStreak} day(s)!")

    #command cooldown
    userVar.daily = time.time()


#steal command
@bot.slash_command(
    name="steal",
    description="Stealing is a crime. Is it worth getting caught? 3 minute cooldown.",
)
async def steal(inter):
    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)
    userVar = users[inter.user.id]
    val = int(random.randint(30, 40)*userVar.multi)
    badVal = int(random.randint(60, 75)*userVar.multi)
    
    #if on cooldown
    if time.time() - userVar.steal < 180:
        await inter.send(f"This command is on cooldown for another **{int(180-(time.time()-userVar.steal))} seconds**")
        return
    if(int(random.randint(0,4)) == 0):
        userVar.balance -= badVal
        await inter.send(f"You got caught stealing and had to pay a **${badVal}** fine!")
    else:
        userVar.balance += val
        await inter.send(f"You stole **${val}**. How terrible!")

    #command cooldown
    userVar.steal = time.time()

#Balance command
@bot.slash_command(
    name="balance",
    description="Get your current balance",
)
async def balance(inter):
    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)
    await inter.send(f"Your current balance is: **${users[inter.user.id].balance}**")


#Coinflip command
@bot.slash_command(
    name='coinflip',
    description= "Flip a coin. If heads, you win 1.75 times what you bet. If tails, you lose your bet.",
)
async def coinflip(inter, amount: int):
    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)
    userVar = users[inter.user.id]
    #if on cooldown
    if time.time() - userVar.cf < 300:
        await inter.send(f"This command is on cooldown for another **{int(300-(time.time()-userVar.cf))} seconds**")
        return
    if amount <= 0:
        await inter.send('You must bet at least $1')
        return
    elif amount > userVar.balance:
        await inter.send(f'You don\'t have enough money to gamble **${amount}!**')
        return
    else:
        coin = (random.randint(0,1))
        if(coin == 1):
            userVar.balance += (int)(amount * (0.5 + (userVar.multi-1)))
            await inter.send(f":coin: The coin landed on __heads__! :)\n\nYour new balance is **${userVar.balance}**!")
        else:
            userVar.balance -= (int)(amount)
            await inter.send(f":coin: The coin landed on __tails__! :(\n\nYour new balance is **${userVar.balance}**!")
    
    #command cooldown
    userVar.cf = time.time()

#leaderboard command
@bot.slash_command(
    name='leaderboard',
    description= "Pull up the leaders of today in an embed!",
)
async def leaderboard(inter):

    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)

    #sort the users
    sorted_dict = {}
    sorted_keys = sorted(users, key=users.get) 

    for i in sorted_keys:
        sorted_dict[i] = users[i]
    sorted_dict = OrderedDict(reversed(list(sorted_dict.items())))

    #embed
    desc = ""
    place = 1
    for user in sorted_dict:
        desc+=str(place)
        desc+=f". <@{user}>: **${sorted_dict[user].balance}**"
        if place >= 5:
            break
        desc+="\n"
        place+=1
    embed = disnake.Embed(
        title="LEADERBOARD",
        color=disnake.Colour.red(),
        description=desc,
        timestamp=datetime.datetime.now()
    )
    await inter.send(embed=embed)

#enum type for shop argument
class Stonks(Enum):
    WOOD = 1
    STONE = 2
    IRON = 3
    SILVER = 4
    DIAMOND = 5

#shop command
@bot.slash_command(
    name='shop',
    description='Access the shop and buy yourself some nice goodies. Alias: /buy',
)
async def shop(inter, args: Stonks = None):
    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)
    userVar = users[inter.user.id]

    #WOOD
    if args == 1:
        if userVar.balance < 100:
            await inter.send("This item costs $100. How can you not even afford that? What's that? Oh, sorry, I can't hear you over the sound of my *AirPods* :headphones:")
        else:
            userVar.balance -= 100
            userVar.inv[args] += 1
            await inter.send(f"Congrats on your purchase of: :wood:. You now have {userVar.inv[args]} :wood:")

    #STONE
    if args == 2:
        if userVar.balance < 450:
            await inter.send("This item costs $450. You should probably practice some saving methods if you want to buy this item LOL!")
        else:
            userVar.balance -= 450
            userVar.inv[args] += 1
            await inter.send(f"Congrats on your purchase of: :rock:. You now have {userVar.inv[args]} :rock:")

    #IRON
    if args == 3:
        if userVar.balance < 1000 and userVar.balance > 500:
            inter.send("This item costs $1000. You're almost halfway there, keep saving! ")
        elif userVar.balance < 1000:
            await inter.send("This item costs $1000. You should probably practice some safe saving methods if you want to buy this item LOL!")
        else:
            userVar.balance -= 1000
            userVar.inv[args] += 1
            await inter.send(f"Congrats on your purchase of: :magnet:. You now have {userVar.inv[args]} :magnet:")

    #SILVER
    if args == 4:
        if userVar.balance < 1750 and userVar.balance < 250:
            await inter.send("This item costs $1750. You need to save up a LOTTT more LOL!")
        elif userVar.balance < 1750 and userVar.balance > 1500:
            await inter.send("This item costs $1750. You only need to save up a little more :coin:! You got this:)")
        elif userVar.balance < 1750:
            await inter.send("This item costs 1750. keep saving up, you got this!!")
        else:
            userVar.balance -= 1750
            userVar.inv[args] += 1
            await inter.send(f"Congrats on your purchase of: :second_place:. You now have {userVar.inv[args]} :second_place:")

    #DIAMOND
    if args == 5:
        if userVar.balance < 6000 and userVar.balance > 1000:
            await inter.send("This item costs $6000. maybe try purchasing something else from the shop!, or keep saving up!!!")
        elif userVar.balance < 6000 and userVar.balance < 500:
            await inter.send("This item may be wayyy out of your reach, maybe try purchasing something else from the shop! Or, keep saving up! You got this:)")
        elif userVar.balance < 6000 and userVar.balance > 3000:
            await inter.send("This item costs $6000. You're almost halfway there, keep saving! ")
        elif userVar.balance < 6000:
            await inter.send("This item costs $6000. Try saving some more :coin: or, don't be shy to take a look at other stuff from the shop!")
        else:
            userVar.balance -= 6000
            userVar.inv[args] += 1
            await inter.send(f"Congrats on your purchase of: :gem:. You now have {userVar.inv[args]} :gem:")

    #default no args
    if args == None:
        desc = "*Purchase materials with /shop or /buy <material name>*\nMaterials can be used to craft items which give multipliers (See /craft).\n\n"
        desc += ":wood: Wood: **$100**\n:rock: Stone: **$450**\n:magnet:Iron: **$1000**\n:second_place: Silver: **$1750**\n:gem: Diamond: **$6000**\n"
        embed = disnake.Embed(
            title="MARKETPLACE",
            color=disnake.Colour.blurple(),
            description=desc,
            timestamp=datetime.datetime.now()
        )
        await inter.send(embed=embed)


#buy command (alias of shop)
#include amount parameter
@bot.slash_command(
    name='buy',
    description='Access the shop and buy yourself some nice goodies. Alias: /buy',
)
async def buy(inter, args: Stonks):
    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)
    userVar = users[inter.user.id]

    #WOOD
    if args == 1:
        if userVar.balance < 100:
            await inter.send("This item costs $100. How can you not even afford that? What's that? Oh, sorry, I can't hear you over the sound of my *AirPods* :headphones:")
        else:
            userVar.balance -= 100
            userVar.inv[args] += 1
            await inter.send(f"Congrats on your purchase of: :wood:. You now have {userVar.inv[args]} :wood:")

    #STONE
    if args == 2:
        if userVar.balance < 450:
            await inter.send("This item costs $450. You should probably practice some saving methods if you want to buy this item LOL!")
        else:
            userVar.balance -= 450
            userVar.inv[args] += 1
            await inter.send(f"Congrats on your purchase of: :rock:. You now have {userVar.inv[args]} :rock:")

    #IRON
    if args == 3:
        if userVar.balance < 1000 and userVar.balance > 500:
            inter.send("This item costs $1000. You're almost halfway there, keep saving! ")
        elif userVar.balance < 1000:
            await inter.send("This item costs $1000. You should probably practice some safe saving methods if you want to buy this item LOL!")
        else:
            userVar.balance -= 1000
            userVar.inv[args] += 1
            await inter.send(f"Congrats on your purchase of: :magnet:. You now have {userVar.inv[args]} :magnet:")

    #SILVER
    if args == 4:
        if userVar.balance < 1750 and userVar.balance < 250:
            await inter.send("This item costs $1750. You need to save up a LOTTT more LOL!")
        elif userVar.balance < 1750 and userVar.balance > 1500:
            await inter.send("This item costs $1750. You only need to save up a little more :coin:! You got this:)")
        elif userVar.balance < 1750:
            await inter.send("This item costs 1750. keep saving up, you got this!!")
        else:
            userVar.balance -= 1750
            userVar.inv[args] += 1
            await inter.send(f"Congrats on your purchase of: :second_place:. You now have {userVar.inv[args]} :second_place:")

    #DIAMOND
    if args == 5:
        if userVar.balance < 6000 and userVar.balance > 1000:
            await inter.send("This item costs $6000. maybe try purchasing something else from the shop!, or keep saving up!!!")
        elif userVar.balance < 6000 and userVar.balance < 500:
            await inter.send("This item may be wayyy out of your reach, maybe try purchasing something else from the shop! Or, keep saving up! You got this:)")
        elif userVar.balance < 6000 and userVar.balance > 3000:
            await inter.send("This item costs $6000. You're almost halfway there, keep saving! ")
        elif userVar.balance < 6000:
            await inter.send("This item costs $6000. Try saving some more :coin: or, don't be shy to take a look at other stuff from the shop!")
        else:
            userVar.balance -= 6000
            userVar.inv[args] += 1
            await inter.send(f"Congrats on your purchase of: :gem:. You now have {userVar.inv[args]} :gem:")

#Items enum type
class Items(Enum):
    TABLE = 21 #wood*5
    MORTAR = 22 #stone*3 (mortar and pestle)
    FIREPIT = 23 #wood*1 + stone*4
    PICKAXE = 24 #wood*2 + stone*1 + iron*3
    SILVER_RING = 25 #silver*2
    MIRROR = 26 #silver*2 + wood*6 + stone*4
    DIAMOND_RING = 27 #diamond*1 + silver*2
    DIAMOND_BLOCK = 28 #diamond*9


#craft command
@bot.slash_command(
    name='craft',
    description='Use your materials to craft items which give multipliers! (Multipliers are additive)',
)
async def craft(inter, args: Items = None):
    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)
    userVar = users[inter.user.id]

    #TABLE
    if args == 21:
        if userVar.inv[1] < 5:
            await inter.send("You have insufficient materials.")
        elif userVar.items[args] > 0:
            await inter.send("You already have this item. Why would you ever need two tables?")
        else:
            userVar.inv[1] -= 5
            userVar.items[args] += 1
            userVar.multi += 0.05
            await inter.send(f"You have crafted a table! Your currency multiplier is now **{userVar.multi}x**!")
    
    #MORTAR

    #FIREPIT

    #PICKAXE

    #SILVER_RING

    #MIRROR

    #DIAMOND_RING

    #DIAMOND_BLOCK

    #default no args
    if args == None:
        desc = "*Craft items using /craft <item>*\nCrafting items gives you multipliers for all currency gained. *You are limited to one of each item.*\n\n"
        desc += "TABLE: *requires 5\*:wood:*\t-\t1.05x multiplier\n\nMORTAR: *requires 3\*:rock:* - 1.05x multiplier\n\n"
        desc += "FIREPIT: *requires 1\*:wood: and 4\*:rock:*\t-\t1.05x multiplier\n\nPICKAXE: *requires 2\*:wood:, 1\*:rock:, 3\*:second_place:*\t-\t1.06x multiplier\n\n"
        desc += "SILVER_RING: *requires 2\*:second_place:*\t-\t1.07x multiplier\n\nMIRROR: *requires 2\*:second_place:, 6\*:wood:, 4\*:rock:*\t-\t1.07x multiplier\n\n"
        desc += "DIAMOND_RING: *requires 1\*:gem: and 2\*:second_place:*\t-\t1.1x multiplier\n\nDIAMOND_BLOCK: *requires 9\*:gem:*\t-\t1.2x multiplier"
        embed = disnake.Embed(
            title="Craftables",
            color=disnake.Colour.blurple(),
            description=desc,
            timestamp=datetime.datetime.now()
        )
        await inter.send(embed=embed)


#inventory command
@bot.slash_command(
    name='inventory',
    description='See your materials inventory',
)
async def inventory(inter):
    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)
    userVar = users[inter.user.id]

    desc = ""
    for mat in userVar.inv:
        desc += f"\n{Stonks(mat).name}: **{userVar.inv[mat]}**"

    embed = disnake.Embed(
        title=f"{inter.user}'s inventory",
        color=disnake.Colour.dark_blue(),
        description=desc,
        timestamp=datetime.datetime.now()
    )
    await inter.send(embed=embed)

#items command
@bot.slash_command(
    name='items',
    description='See your items inventory',
)
async def items(inter):
    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)
    userVar = users[inter.user.id]

    desc = ""
    for item in userVar.items:
        desc += f"\n{Items(item).name}: **{userVar.items[item]}**"

    embed = disnake.Embed(
        title=f"{inter.user}'s items",
        color=disnake.Colour.dark_blue(),
        description=desc,
        timestamp=datetime.datetime.now()
    )
    await inter.send(embed=embed)


#profile command
@bot.slash_command(
    name='profile',
    description='Get basic bot info',
)
async def profile(inter):
    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)
    timeS = int(time.time()-uptime)
    timeM = timeS//60
    timeS %= 60
    timeH = timeM//60
    timeM %= 60
    timeD = timeH//24
    timeH %= 24

    desc = f"Bot uptime: {timeD}D{timeH}H{timeM}M{timeS}S\nLast updated: 11/6/2022\nContributors: Jason Cho (VV#0410), Namitha Yalla (nemoooo#4242), Kauvya Palle (kauvyaP#3222), Akshitha Singathi (akshithasingathi#4557)"
    embed = disnake.Embed(
        title="Bot info",
        color=disnake.Colour.dark_blue(),
        description=desc,
        timestamp=datetime.datetime.now()
    )
    await inter.send(embed=embed)

#multi command
@bot.slash_command(
    name='multi',
    description='See your currency multiplier',
)
async def shop(inter):
    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)
    userVar = users[inter.user.id]

    await inter.send(f"Your current currency multiplier is **{userVar.multi}x**!")

#Owner command- set money (give)
@bot.slash_command(
    hidden=True,
    name='give',
    description='Owner-Only',
)
async def give(inter, amount: int):
    if inter.user.id not in users:
        users[inter.user.id] = User.User(inter.user.id)
    userVar = users[inter.user.id]

    if userVar.id == 274694514432802816:
        userVar.balance += amount
        await inter.send("done")

bot.run(token)
