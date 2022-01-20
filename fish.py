import sys

import discord
import math
from discord.ext import commands
import os
from discord.voice_client import VoiceClient
from discord import FFmpegPCMAudio
from discord.utils import get
import random
import timeit
import threading
from multiprocessing.pool import ThreadPool
from queue import Queue
import asyncio
import operator

from discord import File
from PIL import Image, ImageDraw, ImageFont
import io


#9/5 birthday
#note rarest fish is not really rarest fish anymore


#V0.1
#-lowered Plastic Fish rating, fixed Lesser Eel nick, lowered OJ spawn rate, lowered Normal Eel rating
#added Flopping, Sliding, Crawling, Walking Fish, Fishman, Crystal Fish, Lore 1-3

#V0.2 Elemental Update
#Wind,Cold,Hot Fish -- Gale,Ice,Lava Fish -- Dragon Fish -- Lily<Lotus<Reef<Myo<World Fish -- Dark Fish -- Shiny<Lumen<Radiant<Divine

#V0.2 Halloween

#V0.3
#better descriptions

class fishBreed:
    def __init__(self, name, nick, rarity, species, size, danger, evolution, item, hunt, phrase, thumbnail):
        self.name = name
        self.nick = nick
        self.rarity = rarity
        self.species = species
        self.danger = danger
        self.size = size
        self.evolution = evolution
        self.phrase = phrase
        self.item = item
        self.hunt = hunt
        self.thumbnail = thumbnail



class itemType:
    def __init__(self, name, nick, price, cost, lootNumber):
        self.name = name
        self.nick = nick
        self.price = price
        self.cost = cost
        self.lootNumber = lootNumber

class weaponType:
    def __init__(self, name, nick, cost, damage):
        self.name = name
        self.nick = nick
        self.cost = cost
        self.damage = damage

client = commands.Bot(command_prefix='f!')
os.chdir(os.path.join(os.path.expanduser('~'), 'Desktop', 'fish bot'))

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("_Command still on cooldown. Wait {:.2f} minutes to try again._".format(error.retry_after / 60))



def returnFish(fishName, userID):
    for fishy in fishes:
            if (findFishLine(userID, fishy.name) > -1) and (fishy.nick.lower() == fishName.lower() or fishy.name.lower() == fishName.lower()):
                return fishy
    return fishBreed('Bad Result', '', 0, 0, 0, 0, ('', 0, 0, ''), '', 0, '', '')


global fishSpawns
fishSpawns = {}


@client.event
async def on_ready():
    print('Booted up.')


    await client.wait_until_ready()

    #updateEveryone()
    client.loop.create_task(spawnEverything())
    client.loop.create_task(updateLeaderboard())

    for channel in convertServers().values():
        await client.get_channel(channel).send('```Bot online.```')
    
@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send("Hello! I'm **{}**. Input the command **f!channel** into the channel where you want fish to spawn. When fish start to spawn, do **f!catch** to get started and **f!help** for information on more commands.".format(client.user.name))
            break



@client.command()
async def ping(ctx):
    await ctx.send('Pong {} ms'.format(round(client.latency * 1000)))

@client.command()
async def version(ctx):
    await ctx.send('')


async def spawnEverything():
    print('Spawning...')
    await client.wait_until_ready()


    global resetSpawns
    resetSpawns = True
    spawnList = []
    while True:
        if resetSpawns:
            text = open('data - channels.txt', 'r')
            lines = text.readlines()
            for line in lines:
                colonIndex = line.find(':')
                boostedServers[int(line[colonIndex+1:len(line)])] = 0

            spawnList = []
            for server in convertServers():
                if client.get_guild(server): #check if server exists
                    spawnList.append(spawnFish(server))
            resetSpawns = False
            await asyncio.wait(spawnList, return_when=asyncio.FIRST_COMPLETED)



async def spawnFish(server):
    
    while True:

        if not client.get_guild(server): #1st check if guild was deleted
            return

        memberCount = 0
        for member in client.get_guild(server).members:
            if not member.bot:
                memberCount += 1
        
        minmax = (30, 60) #find spawn time
        if memberCount > 100:
            minmax = (5, 7)
        else:
            minmax = (int(500 / memberCount), (int(500 / memberCount) + 3))

        if resetSpawns: #channel added escape loop
            return

        #await asyncio.sleep(random.randrange(7, 12))
        await asyncio.sleep(random.randrange(minmax[0] * 60, minmax[1] * 60))
        #await client.get_channel(convertServers()[server]).send(minmax)
        
        if resetSpawns: #channel added escape loop
            return

        global spawnedFish
        print('\n\n\n')
        print(convertServers()[server])
        print(boostedServers[convertServers()[server]])
        if boostedServers[convertServers()[server]] == 1:
            subFish = [fish for fish in fishes if fish.rarity > 3 and fishes[fish] != 0]
            spawnedFish = random.choice(subFish)
        else:
            spawnedFish = random.choices(list(fishes), fishes.values())[0]
        fishSpawns[convertServers()[server]] = (spawnedFish, True)

        firstLetter = spawnedFish.name.lower()[0:1]
        article = 'A'
        if firstLetter == 'a' or firstLetter == 'e' or firstLetter == 'i' or firstLetter == 'o' or firstLetter =='u':
            article = 'An'

        if client.get_channel(convertServers()[server]): #second check
            print(convertServers()[server])
            print(spawnedFish.name)
            spawnName = spawnedFish.name
            if spawnName == 'Ghost Fish':
                s = list(spawnName)
                for i in range(len(s)):
                    if (random.randint(1,3) > 1):
                       s[i] = ' '
                spawnName = ''.join(s)

            if boostedServers[convertServers()[server]] == 1:
                msg = 'A Boost Potion is increasing the waves! {} {} has appeared!'
                boostedServers[convertServers()[server]] = 0
            else:
                msg = spawnedFish.phrase
            await client.get_channel(convertServers()[server]).send(msg.format(article, spawnName))




@client.command(brief='Sell an item for some doubloons')
async def sell(ctx):
    channelID = ctx.channel.id
    userID = ctx.author.id
    if os.path.exists(str(userID) + '.txt'):
        print('')

        amount = ctx.message.content.lower()[ctx.message.content.rfind(' ')+1:len(ctx.message.content)]
        if amount.isdecimal():
            itemSold = ctx.message.content.lower()[len('f!sell '):ctx.message.content.rfind(' ')]
        else:
            itemSold = ctx.message.content.lower()[len('f!sell '):len(ctx.message.content)]
            amount = '1'
        amount = int(amount)

        for item in items:
            print('\n\n')
            if (item.name.lower() == itemSold or item.nick.lower() == itemSold) and item.price[0]:
                if amount <= findStat(userID, findFishLine(userID, item.name)):
                    await ctx.send('{} has sold {} {} for {} Doubloons!'.format(ctx.author.mention, 
                        amount, item.name+'s', item.price[1] * amount))
                    print(findStat(userID, 1))
                    updateStat(userID, 6, item.price[1] * amount)
                    print(findStat(userID, 1))
                    addLoot(userID, item.name, -amount, False)
                    print(findStat(userID, 1))




                    return
                else:
                    await ctx.send('You do not have enough of this item.')
                    return
            
        await ctx.send('This item can not be sold.')
        return

    else:
        await ctx.send('This person does not fish.')




@client.command(brief='View items available in the shop, do f!buy [item name] [amount] to actually buy the item')
@commands.cooldown(1, 30, commands.BucketType.guild)
async def shop(ctx):

    itemField = ''
    boatField = ''
    for item in items:
        if item.cost > 0:
            itemField += '{} - {}\n'.format(item.name, item.cost)

    for boat in list(boats.keys()):
        if boats[boat][0] > 0:
            boatField += '{} - {}\n'.format(boat, boats[boat][0])

    embed = discord.Embed(
            title = 'Shop',
            color = discord.Color.dark_gray()
        )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name='Items', value=itemField)
    embed.add_field(name='Boats', value=boatField)

    await ctx.send(embed=embed)


@client.command(brief='View items available in the shop with f!shop, do f!buy [item name] [amount] to actually buy the item')
async def buy(ctx):
    userID = ctx.author.id
    if os.path.exists(str(userID) + '.txt'):


        amount = ctx.message.content.lower()[ctx.message.content.rfind(' ')+1:len(ctx.message.content)]
        if amount.isdecimal():
            itemBought = ctx.message.content.lower()[len('f!buy '):ctx.message.content.rfind(' ')]
        else:
            itemBought = ctx.message.content.lower()[len('f!buy '):len(ctx.message.content)]
            amount = '1'
        amount = int(amount)

        for boat in list(boats.keys()):
            if itemBought == boat.lower():
                if findStat(userID, 6) >= amount * boats[boat][0] and boats[boat][0] != 0:
                    await ctx.send('{} has bought {} {} for {} doubloons!'.format(ctx.author.mention, 
                        amount, boat, amount * boats[boat][0]))
                    
                    updateStat(userID, 6, -amount*boats[boat][0])
                    addLoot(userID, boat, amount, False)
                    return
               #text = open(str(ctx.author.id) + '.txt', 'r')
               # lines = text.readlines()
               # lines[5] = 'Boat:{}\n'.format(boat)

               # with open(str(ctx.author.id) + '.txt', 'w') as k:
                    #k.writelines(lines)
                #return await ctx.send('Your favorite fish is now the {}!'.format(fishy.name))

        for item in items:
            print('\n\n')
            if (item.name.lower() == itemBought or item.nick.lower() == itemBought) and item.cost > 0:
                print(findStat(userID, 6))
                print(amount * item.cost)
                print(amount)
                if findStat(userID, 6) >= amount * item.cost:
                    await ctx.send('{} has bought {} {} for {} doubloons!'.format(ctx.author.mention, 
                        amount, item.name, amount*item.cost))
                    
                    updateStat(userID, 6, -amount*item.cost)
                    addLoot(userID, item.name, amount, False)

                    return
                else:
                    await ctx.send('You do not have enough doubloons.')
                    return
            
        await ctx.send('This item can not be bought.')
        return

    else:
        await ctx.send('This person does not fish.')




@client.command(brief="View your boats. do f!boat [boat name] to set the boat you're displaying.")
async def boat(ctx):
    if (ctx.message.mentions == []):
        userID = ctx.author.id
        userName = ctx.author.name
        userProfile = ctx.author.avatar_url
    else: #wants to see another user's profile
        userID = ctx.message.mentions[0].id
        userName = ctx.message.mentions[0].name
        userProfile = ctx.message.mentions[0].avatar_url
        
    if os.path.exists(str(userID) + '.txt'):
        print(ctx.message.content.lower())
        if ctx.message.content.lower() == 'f!boat' or ('f!boat' in ctx.message.content.lower() and ctx.message.mentions != []):
            embed = discord.Embed(
            color = discord.Color.dark_gray()
            )
            embed.set_author(name=userName, icon_url=userProfile)
            field = ''
            for boat in list(boats.keys()):
                if findStat(userID, findFishLine(userID, boat)) > 0:
                    field += '{}\n'.format(boat)
                else:
                    field += '-----\n'
            embed.add_field(name='Boats Owned', value=field)
            print(embed)
            return await ctx.send(embed=embed)

        else:
            boatName = ctx.message.content.lower()[len('f!boat '):len(ctx.message.content)]
            for boat in list(boats.keys()):
                if boatName == boat.lower() and findStat(userID, findFishLine(userID, boat)) > 0:
                    text = open(str(ctx.author.id) + '.txt', 'r')
                    lines = text.readlines()
                    lines[7] = 'Boat:{}\n'.format(boat)

                    with open(str(userID) + '.txt', 'w') as k:
                        k.writelines(lines)
                    
                    return await ctx.send('You have set your boat to {}'.format(boat))
            
            await ctx.send('You do not have this boat.')

    else:
        await ctx.send('This person does not fish.')



@client.command(brief='Scales a fish')
async def scale(ctx):
    userID = ctx.author.id
    if os.path.exists(str(userID) + '.txt'):
        print('')

        amount = ctx.message.content.lower()[ctx.message.content.rfind(' ')+1:len(ctx.message.content)]
        if amount.isdecimal():
            fishScaled = ctx.message.content.lower()[len('f!scale '):ctx.message.content.rfind(' ')]
        else:
            fishScaled = ctx.message.content.lower()[len('f!scale '):len(ctx.message.content)]
            amount = '1'
        amount = int(amount)

        print(amount)
        print(fishScaled)

        for fishy in fishes:
            print('\n\n')
            if (fishy.name.lower() == fishScaled or fishy.nick.lower() == fishScaled) and fishy.item != None:
                if amount <= findStat(userID, findFishLine(userID, fishy.name)):
                    xpGained = int(amount * 10 / (fishy.evolution[2]*(random.randrange(5, 12)/10)))
                    await ctx.send('{} has scaled {} {} into {} and gained {} XP!'.format(ctx.author.mention, 
                        amount, fishy.name, fishy.item+'s', xpGained))
                    
                    updateStat(userID, 1, -amount)
                    updateStat(userID, 3, xpGained)
                    addLoot(userID, fishy.name, -amount, True)
                    addLoot(userID, fishy.item, amount, True)
                    if levelUp(ctx.author.id):
                        await ctx.send('{} has leveled up to Fisher Level {}'.format(ctx.author.mention, str(findStat(ctx.author.id, 2))))

                    sortFish(ctx.author.id)
                    updateStat(ctx.author.id, 4, rarestFish(ctx.author.id).rarity - findStat(ctx.author.id, 4))
                    return
                else:
                    await ctx.send('You do not have enough of this fish.')
                    return
            
        await ctx.send('This fish can not be scaled.')
        return

    else:
        await ctx.send('This person does not fish.')


@client.command(brief="Catches a fish")
async def catch(ctx):
    channelID = ctx.channel.id
    userID = ctx.author.id

    if os.path.exists(str(userID) + '.txt'):
       print('')
    else:
        createUser(ctx.author.id)


    if channelID in fishSpawns: #checks if in ocean

        print('f!catch {}'.format(str(fishSpawns[channelID][0].nick)))
        print(ctx.message.content.lower())

        print(fishSpawns[channelID][1])
        if fishSpawns[channelID][1]:
            if 'f!catch {}'.format(str(fishSpawns[channelID][0].nick)).lower() == ctx.message.content.lower() or 'f!catch {}'.format(str(fishSpawns[channelID][0].name)).lower() == ctx.message.content.lower():
                print('{} is catching'.format(ctx.author.name))

                tempName = str(fishSpawns[channelID][0].name)

                xpGained = int(10 / (fishSpawns[channelID][0].evolution[2]*(random.randrange(7, 15)/10)))
                updateStat(userID, 3, xpGained)
                addLoot(ctx.author.id, fishSpawns[channelID][0].name, 1, True)

                fishSpawns[channelID] = (spawnedFish, False)

                await ctx.send('{} reeled in a {} and gained {} XP!'
                    .format(ctx.author.mention, str(tempName), str(xpGained)))

                if findFishLine(ctx.author.id, 'Mystery Egg') > -1:
                    updateStat(ctx.author.id, 11, 1)
                if findStat(ctx.author.id, 11) >= 100 and findFishLine(ctx.author.id, 'Weird Squid') == -1:
                    addLoot(ctx.author.id, 'Weird Squid', 1, True)
                    addLoot(ctx.author.id, 'Mystery Egg', -findStat(ctx.author.id, findFishLine(ctx.author.id, 'Mystery Egg')), False)
                    await ctx.send("{}'s Mystery Egg has hatched into a Weird Squid!".format(ctx.author.mention))

                sortFish(userID)

                
                updateStat(userID, 4, rarestFish(userID).rarity - findStat(userID, 4))

                if (levelUp(userID)):
                    await ctx.send('{} has leveled up to Fisher Level {}'
                        .format(ctx.author.mention, str(findStat(userID, 2))))








@client.command(brief='Use an item do f!use [item name] [amount you want to use]')
async def use(ctx):
    
    if os.path.exists(str(ctx.author.id) + '.txt'):
        fishData = fishBreed('', '', 0, 0, 0, 0, ('', 0, 0, ''), '', 0, '', '')

        amount = ctx.message.content.lower()[ctx.message.content.rfind(' ')+1:len(ctx.message.content)]
        if amount.isdecimal():
            itemUsed = ctx.message.content.lower()[len('f!use '):ctx.message.content.rfind(' ')]
        else:
            itemUsed = ctx.message.content.lower()[len('f!use '):len(ctx.message.content)]
            amount = '1'
        amount = int(amount)
        
        embed = discord.Embed(
        color = discord.Color.dark_gray()
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)


        #SHARD
        if ('Elemental Shard'.lower() == itemUsed or 'Shard'.lower() == itemUsed) and findFishLine(ctx.author.id, 'Elemental Shard') >= amount:
            embed.title='Evolvable Fish'
            embed.description = 'React with the corresponding emoji to evolve the desired fish.\n🔴 - Red Fish\n🟢 - Green Fish\n🔵 - Blue Fish\n🟡 - Yellow Fish\n🟣 - Purple Fish'
            msg = await ctx.send(embed=embed)
            reactions = ['🔴', '🟢', '🔵', '🟡', '🟣']
            for emoji in reactions:
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in reactions

            try:
                reaction,user = await client.wait_for('reaction_add', timeout=60, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return await ctx.send('Transaction cancelled...')


            await msg.delete()

            if str(reaction.emoji) == '🔴':
                fishName = 'Red Fish'
            elif str(reaction.emoji) == '🟢':
                fishName = 'Green Fish'
            elif str(reaction.emoji) == '🔵':
                fishName = 'Blue Fish'
            elif str(reaction.emoji) == '🟡':
                fishName = 'Yellow Fish'
            elif str(reaction.emoji) == '🟣':
                fishName = 'Purple Fish'
                amount *= 3
            
            fishData = returnFish(fishName, ctx.author.id)

            if findStat(ctx.author.id, findFishLine(ctx.author.id, fishData.name)) >= amount*fishData.evolution[1]:
                fishGained = int(amount / fishData.evolution[1])
                updateStat(ctx.author.id, findFishLine(ctx.author.id, fishData.evolution[3]), -amount)
                return await evolve(ctx, fishData, fishGained, -amount*fishData.evolution[1], fishData.evolution[0])
            
            await ctx.send('You do not have enough of this fish.')



        #UGLY HAT
        elif ('Ugly Hat'.lower() == itemUsed or 'Hat'.lower() == itemUsed) and findFishLine(ctx.author.id, 'Ugly Hat') >= amount:
            if findStat(ctx.author.id, findFishLine(ctx.author.id, 'Red Fish')) >= amount:
                updateStat(ctx.author.id, findFishLine(ctx.author.id, 'Red Fish'), -amount)
                addLoot(ctx.author.id, 'Ugly Hat', -amount, False)
                addLoot(ctx.author.id, 'Ugly Red Hat Fish', amount, True)
                sortFish(ctx.author.id)
                return await ctx.send('{} noticed their Red Fish has a receeding hairline. Better cover that up with an Ugly Hat. You have evolved {} Red Fish into {} Ugly Red Hat Fish!'.format(ctx.author.mention, amount, amount))        
            await ctx.send('You do not have enough of this fish.')




        #PICKAXE
        elif ('Pickaxe'.lower() == itemUsed or 'Pick'.lower() == itemUsed) and findFishLine(ctx.author.id, 'Pickaxe') > 0:
            if findStat(ctx.author.id, findFishLine(ctx.author.id, 'Ore Fish')) >= amount:
                updateStat(ctx.author.id, findFishLine(ctx.author.id, 'Ore Fish'), -amount)
                fishList = {"None": 0, "Topaz Fish": 0, "Garnet Fish": 0, "Amethyst Fish": 0, "Ruby Fish": 0, "Sapphire Fish": 0, "Emerald Fish": 0, "Diamond Fish": 0, "Moonstone Fish": 0, "Umbrium Fish": 0}
                newFish = ''
                for i in range(amount):
                    newFish = random.choices(list(fishList.keys()), weights = [40, 48/2, 48/2, 11/4, 11/4, 11/4, 11/4, 3.9/2, 3.9/2, 0.1], k=1)[0]
                    addLoot(ctx.author.id, newFish, 1, True)
                    fishList[newFish] += 1

    
                sortFish(ctx.author.id)
                updateStat(ctx.author.id, 4, rarestFish(ctx.author.id).rarity - findStat(ctx.author.id, 4))

                msg = '{} used their pickaxe to break {} Ore Fish and found '.format(ctx.author.mention, amount)
                newMsg = ''
                for item in list(fishList.keys()):
                    if fishList[item] > 0 and item != 'None':
                        newMsg += '{} {}, '.format(fishList[item], item)
                
                if len(newMsg) <= 0:
                    newMsg = 'nothing!'
                else:
                    newMsg = newMsg[:-2] + '!'

                return await ctx.send(msg + newMsg)  
            await ctx.send('You do not have enough of this fish.')


        #HEART SCALE
        elif ('Heart Scale'.lower() == itemUsed or 'Heart'.lower() == itemUsed) and findFishLine(ctx.author.id, 'Heart Scale') >= amount:
            potionsMade = 0
            for i in range(amount):
                addLoot(ctx.author.id, 'Heart Scale', -1, False)
                if random.randint(0, 1) == 1:
                    addLoot(ctx.author.id, 'Reset Potion', 1, False)
                    potionsMade += 1
            
            if potionsMade > 0:
                return await ctx.send('{} used {} Heart Scales to make {} Reset Potions.'.format(ctx.author.mention, amount, potionsMade))
            else:
                return await ctx.send('{} used {} Heart Scales but failed to make anything.'.format(ctx.author.mention, amount))


        #RESET POTION
        elif ('Reset Potion'.lower() == itemUsed or 'Reset'.lower() == itemUsed) and findFishLine(ctx.author.id, 'Reset Potion') >= amount:
            addLoot(ctx.author.id, 'Reset Potion', -1, False)
            hunt.reset_cooldown(ctx)
            return await ctx.send('{} used a Reset Potion to reset their hunt cooldown.'.format(ctx.author.mention))


        #PLASTIC PIECE
        elif ('Plastic Piece'.lower() == itemUsed or 'Plastic'.lower() == itemUsed) and findFishLine(ctx.author.id, 'Plastic Piece') > 0:
            embed.title="The Tinkerer's Shop"
            embed.description="Hello! I am known as The Tinkerer! Thank you for cleaning up our oceans from my failed exp-\n...I mean, these annoying Plastic Fish. I will cut you a deal! I'll trade you 1 Bronze Part for every 30 Plastic Pieces you return to me."
            embed.description += "\n\nBronze Parts : Plastic Pieces\n1️⃣ : 30\n2️⃣ : 60\n3️⃣ : 90\n5️⃣ : 150\n🔟 : 300"
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/753825392753770616/900453728442802267/thetinkerer.png')
            msg = await ctx.send(embed=embed)
            reactions = ['1️⃣', '2️⃣', '3️⃣', '5️⃣', '🔟']
            for emoji in reactions:
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in reactions

            try:
                reaction,user = await client.wait_for('reaction_add', timeout=60, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return await ctx.send('Transaction cancelled...')


            await msg.delete()

            if str(reaction.emoji) == '1️⃣':
                amount = 1
            elif str(reaction.emoji) == '2️⃣':
                amount = 2
            elif str(reaction.emoji) == '3️⃣':
                amount = 3
            elif str(reaction.emoji) == '5️⃣':
                amount = 5
            elif str(reaction.emoji) == '🔟':
                amount = 10

            if findStat(ctx.author.id, findFishLine(ctx.author.id, "Plastic Piece")) >= amount*30:
                addLoot(ctx.author.id, 'Plastic Piece', -amount*30, False)
                addLoot(ctx.author.id, 'Bronze Part', amount, False)
                return await ctx.send('{} has traded {} Plastic Pieces for {} Bronze Parts'.format(ctx.author.mention, amount*30, amount))
            else:
                return await ctx.send('You do not have enough of this item.')


        #BRONZE PART
        elif ('Bronze Part'.lower() == itemUsed or 'Bronze'.lower() == itemUsed) and findFishLine(ctx.author.id, 'Bronze Part') > 0:
            embed.title="The Tinkerer's Shop"
            embed.description="Hello! I am known as The Tinkerer! Welcome to my shop! Here you can exchange Bronze Parts for some of my creations!"
            embed.description += "\n\n🐟 - Bronze Fish (3)\n⛵ - Steamship (10)"
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/753825392753770616/900453728442802267/thetinkerer.png')
            msg = await ctx.send(embed=embed)
            reactions = ['🐟', '⛵']
            for emoji in reactions:
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in reactions

            try:
                reaction,user = await client.wait_for('reaction_add', timeout=60, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return await ctx.send('Transaction cancelled...')


            await msg.delete()

            if str(reaction.emoji) == '🐟':
                amount = 3
                itemGained = 'Bronze Fish'
                ifFish = True
            elif str(reaction.emoji) == '⛵':
                amount = 10
                itemGained = 'Steamship'
                ifFish = False

            if findStat(ctx.author.id, findFishLine(ctx.author.id, "Bronze Part")) >= amount:
                addLoot(ctx.author.id, itemGained, 1, ifFish)
                addLoot(ctx.author.id, 'Bronze Part', -amount, False)
                sortFish(ctx.author.id)
                updateStat(ctx.author.id, 4, rarestFish(ctx.author.id).rarity - findStat(ctx.author.id, 4))
                return await ctx.send('{} has traded {} Bronze Parts for a {}!'.format(ctx.author.mention, amount, itemGained))
            else:
                return await ctx.send('You do not have enough of this item.')
            

        #BUCKET OF GRAY SCALES
        elif ('Bucket of Gray Scales'.lower() == itemUsed or 'Bucket'.lower() == itemUsed) and findFishLine(ctx.author.id, 'Bucket of Gray Scales') > 0:
            wolfAmount = findStat(ctx.author.id, findFishLine(ctx.author.id, 'Wolf Fish'))
            if wolfAmount <= 0:
                return await ctx.send('You do not have enough of the required fish.')
            else:
                text = open(str(ctx.author.id) + '.txt', 'r')
                lines = text.readlines()
                for line in lines:
                    if 'Pack of Wolf Fish' in line:
                        oldPack = line[0:line.find(':')]
                        return addLoot(ctx.author.id, oldPack, -1, True)
                addLoot(ctx.author.id, 'Pack of Wolf Fish Lv.{}'.format(wolfAmount), 1, True)
                addLoot(ctx.author.id, 'Wolf Fish', -wolfAmount, True)
                addLoot(ctx.author.id, 'Bucket of Gray Scales', -1, False)
                return await ctx.send('{} used a Bucket of Gray Scales to lure in all of their Wolf Fish! {} has formed a Pack of Wolf Fish Lv.{}'.format(ctx.author.mention, ctx.author.mention, wolfAmount))


        #MOONSTONE
        elif 'Moonstone'.lower() == itemUsed and findFishLine(ctx.author.id, 'Moonstone') > 0:
            darkAmount = findStat(ctx.author.id, findFishLine(ctx.author.id, 'Dark Fish'))
            if darkAmount < amount*3:
                return await ctx.send('You do not have enough of the required fish.')
            else:
                addLoot(ctx.author.id, 'Moon Fish', amount, True)
                addLoot(ctx.author.id, 'Dark Fish', -amount*3, True)
                addLoot(ctx.author.id, 'Moonstone', -amount, False)
                updateStat(ctx.author.id, 4, rarestFish(ctx.author.id).rarity - findStat(ctx.author.id, 4))
                return await ctx.send('{} used {} Moonstones to turn {} Dark Fish into {} Moon Fish!'.format(ctx.author.mention, amount, amount*3, amount))

        #WEAPONS TICKET
        elif ('Weapons Ticket'.lower() == itemUsed or 'Ticket'.lower() == itemUsed) and findFishLine(ctx.author.id, 'Weapons Ticket') > 0:
            embed.title="The Weapons Shop"
            embed.description="Yo! I'm Ronzo, master fisherman and weapons expert! Take a look at my cool weapons! Fishmen love them!"
            embed.add_field(name='Weapons', value='💂‍♂️ - Spear (No Use Currently)\n👨‍🌾 - Harpoon\n🧙‍♂️ - Wand')
            embed.add_field(name='Doubloons', value='150\n300\n600')
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/753825392753770616/902304211918802954/ronzo.png')
            msg = await ctx.send(embed=embed)
            reactions = ['💂‍♂️', '👨‍🌾', '🧙‍♂️']
            for emoji in reactions:
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in reactions

            try:
                reaction,user = await client.wait_for('reaction_add', timeout=60, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return await ctx.send('Transaction cancelled...')


            await msg.delete()

            if str(reaction.emoji) == '💂‍♂️':
                weapon = 'Spear'
                cost = 150
            elif str(reaction.emoji) == '👨‍🌾':
                weapon = 'Harpoon'
                cost = 300
            elif str(reaction.emoji) == '🧙‍♂️':
                weapon = 'Wand'
                cost = 600

           
            if findStat(ctx.author.id, 6) >= cost:
                addLoot(ctx.author.id, weapon, 1, False)
                updateStat(ctx.author.id, 6, -cost)
                await ctx.send("{} has bought a {} for {} Doubloons!".format(ctx.author.mention, weapon, cost))
            else:
                await ctx.send("You do not have enough Doubloons.")

        
        #SPEAR, HARPOON, WAND
        elif 'Spear'.lower() == itemUsed and findFishLine(ctx.author.id, 'Spear') > 0:
            if findStat(ctx.author.id, findFishLine(ctx.author.id, 'Fishman')) >= amount:
                addLoot(ctx.author.id, 'Fishman-Warrior', amount, True)
                addLoot(ctx.author.id, 'Spear', -amount, False)
                addLoot(ctx.author.id, 'Fishman', -amount, True)
                await ctx.send("{} has used {} Spears to turn their Fishmen into Fishman-Warriors!".format(ctx.author.mention, amount))
            else:
                return await ctx.send("You do not have enough Fishmen.")
        elif 'Harpoon'.lower() == itemUsed and findFishLine(ctx.author.id, 'Harpoon') > 0:
            if findStat(ctx.author.id, findFishLine(ctx.author.id, 'Fishman')) >= amount:
                addLoot(ctx.author.id, 'Fishman-Hunter', amount, True)
                addLoot(ctx.author.id, 'Harpoon', -amount, False)
                addLoot(ctx.author.id, 'Fishman', -amount, True)
                await ctx.send("{} has used {} Harpoons to turn their Fishmen into Fishman-Hunters!".format(ctx.author.mention, amount))
            else:
                return await ctx.send("You do not have enough Fishmen.")
        elif 'Wand'.lower() == itemUsed and findFishLine(ctx.author.id, 'Wand') > 0:
            if findStat(ctx.author.id, findFishLine(ctx.author.id, 'Fishman')) >= amount:
                addLoot(ctx.author.id, 'Fishman-Enchanter', amount, True)
                addLoot(ctx.author.id, 'Wand', -amount, False)
                addLoot(ctx.author.id, 'Fishman', -amount, True)
                await ctx.send("{} has used {} Wands to turn their Fishmen into Fishman-Enchanters!".format(ctx.author.mention, amount))
            else:
                return await ctx.send("You do not have enough Fishmen.")




        #BOOST POTION
        elif ('Boost Potion'.lower() == itemUsed or 'Boost'.lower() == itemUsed) and findFishLine(ctx.author.id, 'Boost Potion') > 0:
            boostedServers[ctx.message.channel.id] = 1
            print('BOOSTED:')
            print(ctx.message.channel.id)
            print(boostedServers[ctx.message.channel.id])
            addLoot(ctx.author.id, "Boost Potion", -amount, False)
            return await ctx.send("{} has boosted the channel! The next fish will have a higher rarity!".format(ctx.author.mention))




        #TRANSFORM POTION
        elif ('Transform Potion'.lower() == itemUsed or 'Transform'.lower() == itemUsed) and findFishLine(ctx.author.id, 'Transform Potion') > 0:
            if findStat(ctx.author.id, findFishLine(ctx.author.id, 'Happy Fish')) > 0:
                addLoot(ctx.author.id, 'Transform Potion', -amount, False)
                addLoot(ctx.author.id, 'Happy Fish', -amount, True)
                subFish = [fish for fish in fishes if fish.rarity > 1]
                fishList = {}
                for fish in subFish:
                    fishList[fish.name] = 0
                for i in range(amount):
                    fishData = random.choice(list(subFish))
                    addLoot(ctx.author.id, fishData.name, 1, True)
                    fishList[fishData.name] += 1
                msg = ""
                for fish in fishList:
                    if fishList[fish] > 0:
                        msg += "{} {}, ".format(fishList[fish], fish)
                msg = msg[:-2]
                return await ctx.send("{} has used {} Transform Potions to turn {} Happy Fish into {}.".format(ctx.author.mention, amount, amount, msg))
            else:
                return await ctx.send("You do not have enough Happy Fish.")


        
        #ORB
        elif ('Elemental Orb'.lower() == itemUsed or 'Orb'.lower() == itemUsed) and findFishLine(ctx.author.id, 'Elemental Orb') >= amount:
            embed.title='Evolvable Fish'
            embed.description = 'React with the corresponding emoji to evolve the desired fish.\n🔴 - Fire Fish\n🟢 - Kelp Fish\n🔵 - Ice Fish\n🟡 - Lightning Fish\n'
            msg = await ctx.send(embed=embed)
            reactions = ['🔴', '🟢', '🔵', '🟡']
            for emoji in reactions:
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in reactions

            try:
                reaction,user = await client.wait_for('reaction_add', timeout=60, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return await ctx.send('Transaction cancelled...')


            await msg.delete()

            if str(reaction.emoji) == '🔴':
                fishName = 'Fire Fish'
            elif str(reaction.emoji) == '🟢':
                fishName = 'Kelp Fish'
            elif str(reaction.emoji) == '🔵':
                fishName = 'Ice Fish'
            elif str(reaction.emoji) == '🟡':
                fishName = 'Lightning Fish'
            
            fishData = returnFish(fishName, ctx.author.id)

            if findStat(ctx.author.id, findFishLine(ctx.author.id, fishData.name)) >= amount*fishData.evolution[1]:
                updateStat(ctx.author.id, findFishLine(ctx.author.id, fishData.evolution[3]), -amount)
                size = random.choices([' (Runt)', ' (Average)'], weights = [1, 1], k=1)[0]
                fishEvo = fishData.evolution[0] + size
                return await evolve(ctx, fishData, amount, -amount*fishData.evolution[1], fishEvo)
            
            await ctx.send('You do not have enough of this fish.')

        #SERPENT SCALE
        elif('Serpent Scale'.lower() == itemUsed or 'Serpent'.lower() == itemUsed) and findFishLine(ctx.author.id, 'Serpent Scale') >= amount:
            fishData = returnFish('White Fish', ctx.author.id)
            if findStat(ctx.author.id, findFishLine(ctx.author.id, fishData.name)) >= amount*fishData.evolution[1]:
                updateStat(ctx.author.id, findFishLine(ctx.author.id, fishData.evolution[3]), -amount)
                size = random.choices([' (Runt)', ' (Average)'], weights = [1, 1], k=1)[0]
                fishEvo = fishData.evolution[0] + size
                return await evolve(ctx, fishData, amount, -amount*fishData.evolution[1], fishEvo)
            else:
                return await ctx.send('You do not have enough of the required fish.')

        else:
            await ctx.send('You do not have enough of this item.')
    else:
        await ctx.send('This person does not fish.')









@client.command(brief='Combine your fish to get rarer fish')
async def evolve(ctx):
    if os.path.exists(str(ctx.author.id) + '.txt'):
        fishData = fishBreed('', '', 0, 0, 0, 0, ('', 0, 0, ''), '', 0, '', '')
        fishData = returnFish(ctx.message.content.lower()[len('f!evolve '):len(ctx.message.content)], ctx.author.id)




        if (fishData.evolution[0]=='None' or fishData.evolution[0]=='Coming Soon'):
            return await ctx.send('This fish does not evolve.')



        if findFishLine(ctx.author.id, fishData.name) > -1:
            
            print(fishData.evolution[3])
            if fishData.evolution[3] != None:
                return await ctx.send('{} needs a [{}] to evolve this fish. Use the command f!use [item name] [amount] to evolve this fish.'.format(ctx.author.mention, fishData.evolution[3]))


            fishLost = findStat(ctx.author.id, findFishLine(ctx.author.id, fishData.name))
            fishLost = fishLost%fishData.evolution[1]-fishLost
            fishGained = int(findStat(ctx.author.id, findFishLine(ctx.author.id, fishData.name)) / fishData.evolution[1])
            await evolve(ctx, fishData, fishGained, fishLost, fishData.evolution[0])

        else:
            await ctx.send('You do not have this fish.')
    else:
        await ctx.send('This person does not fish.')



async def evolve(ctx, fishData, fishGained, fishLost, fishEvo):
    if (fishEvo=='None' or fishEvo=='Coming Soon'):
            return await ctx.send('This fish does not evolve.')

    print(fishLost)
    if fishLost >= 0:
                return await ctx.send('You do not have enough fish to evolve.')

    updateStat(ctx.author.id, findFishLine(ctx.author.id, fishData.name), fishLost)
    addLoot(ctx.author.id,fishEvo, fishGained, True)
    sortFish(ctx.author.id)
    updateStat(ctx.author.id, 4, rarestFish(ctx.author.id).rarity - findStat(ctx.author.id, 4))

    xpGained = int(-fishLost * 10 / (fishData.evolution[2]*(random.randrange(5, 12)/10)))


    await ctx.send('{} has evolved {} {} into {} {} and gained {} XP!'.format(ctx.author.mention, 
        -fishLost, fishData.name, fishGained, fishEvo, xpGained))
    
    updateStat(ctx.author.id, 3, xpGained)
    if levelUp(ctx.author.id):
        await ctx.send('{} has leveled up to Fisher Level {}'.format(ctx.author.mention, str(findStat(ctx.author.id, 2))))
    updateStat(ctx.author.id, 1, fishLost)  





@client.command(brief="Shows user's profile")
async def profile(ctx):

    if (ctx.message.mentions == []):
        userID = ctx.author.id
        userName = ctx.author.name
        userProfile = ctx.author.avatar_url
    else: #wants to see another user's profile
        userID = ctx.message.mentions[0].id
        userName = ctx.message.mentions[0].name
        userProfile = ctx.message.mentions[0].avatar_url

    if os.path.exists(str(userID) + '.txt'):
        totalFish = findStat(userID, 1)
        fisherLevel = findStat(userID, 2)
        currentXP = findStat(userID, 3)
        neededXP = findStat(userID, 2) * 60 - currentXP #change 60 with xpMod
        doubloons = findStat(userID, 6)




        text = open(str(userID) + '.txt', 'r')
        lines = text.readlines()

        embed = discord.Embed(
            title = 'Profile',
            color = discord.Color.dark_gray()
        )
        embed.set_author(name=userName, icon_url=userProfile)
        embed.add_field(name='User ID', value=userID, inline=False)
        embed.add_field(name='Fisher Level', value=fisherLevel, inline=True)
        embed.add_field(name='Current XP', value=currentXP, inline=True)
        embed.add_field(name='Needed XP', value=neededXP, inline=True)
        embed.add_field(name='Doubloons', value = doubloons, inline=True)
        embed.add_field(name='Total Fish', value=totalFish, inline=True)
        embed.add_field(name='Favorite Fish', value=favoriteFish(userID), inline=True)
        embed.set_thumbnail(url=boats[findStat(userID, 7, False)][1])

        await ctx.send(embed=embed)
    else:
        await ctx.send("This person doesn't fish.")


@client.command(brief="Use a Fishman-Enchanter to create cool items")
@commands.cooldown(1, 86400, commands.BucketType.user) #day 86400
async def enchant(ctx):
    if os.path.exists(str(ctx.author.id) + '.txt'):
        if findStat(ctx.author.id, findFishLine(ctx.author.id, 'Fishman-Enchanter')) > 0:
            item = random.choices(['Elemental Orb', 'Reset Potion', 'Transform Potion', 'Boost Potion', 'Nothing'], weights = [1, 1, .7, .3, 1])[0]
            if item == 'Nothing':
                return await ctx.send("{}'s Fisherman-Enchanter wasn't able to conjure anything.".format(ctx.author.mention))
            
            addLoot(ctx.author.id, item, 1, False)
            return await ctx.send("{}'s Fisherman-Enchanter has conjured a {}.".format(ctx.author.mention, item))
        else:
            return await ctx.send("You do not have enough of the required fish.")

@client.command(brief="Hunt for an item, only certain fish can hunt")
@commands.cooldown(1, 3600, commands.BucketType.user) #hr 3600
async def hunt(ctx):
    if os.path.exists(str(ctx.author.id) + '.txt'):
        fishData = fishBreed('', '', 0, 0, 0, 0, ('', 0, 0, ''), '', 0, '', '')
        fishData = returnFish(ctx.message.content.lower()[len('f!hunt '):len(ctx.message.content)], ctx.author.id)
        if findStat(ctx.author.id, findFishLine(ctx.author.id, fishData.name)) > 0:
            if fishData.name == 'Ogre Fish':
                if random.randint(1, 5) == 1:
                    addLoot(ctx.author.id, 'Weapons Ticket', 1, False)
                    return await ctx.send("{}'s Ogre Fish returned with a weird letter. It's a Weapons Ticket!".format(ctx.author.mention))
                else:
                    return await ctx.send("{}'s Ogre Fish returned empty-handed!".format(ctx.author.mention))


            if fishData.hunt != None:
                lootTable = random.randint(1, 4)
                print(fishData.hunt[0])
                if lootTable == 1:
                    if fishData.name == "Fishman-Hunter":
                        maxRarity = len(rarities)-7
                    else:
                        maxRarity = fishData.rarity
                    subFish = [fish for fish in fishes if fish.rarity < maxRarity and fish.rarity >= len(rarities)-10]
                    spawnedFish = random.choice(list(subFish))
                    addLoot(ctx.author.id, spawnedFish.name, 1, True)
                    return await ctx.send("{}'s {} has hunted a {}!".format(ctx.author.mention, fishData.name, spawnedFish.name))
                elif lootTable == 2:
                    subItems = [item for item in items if item.lootNumber != None]
                    subItemsNoNone = [item for item in subItems if item.lootNumber <= fishData.hunt[0]]
                    spawnedItem = random.choice(list(subItemsNoNone))
                    addLoot(ctx.author.id, spawnedItem.name, 1, False)
                    return await ctx.send("{}'s {} has hunted a {}!".format(ctx.author.mention, fishData.name, spawnedItem.name))
                elif lootTable == 3 or lootTable == 4:
                    doubloonsAdded = int(fishData.hunt[1] * random.uniform(0.5, 2.5))
                    updateStat(ctx.author.id, 6, doubloonsAdded)
                    return await ctx.send("{}'s {} has hunted {} Doubloons!".format(ctx.author.mention, fishData.name, doubloonsAdded))

                hunt.reset_cooldown(ctx)
            else:
                await ctx.send("This fish can not hunt.")
                hunt.reset_cooldown(ctx)
        else:
            await ctx.send("You do not have this fish.")
            hunt.reset_cooldown(ctx)
    else:
        await ctx.send("This person doesn't fish.")
        hunt.reset_cooldown(ctx)



@client.command(brief="Shows user's inventory")
async def inventory(ctx):

    if (ctx.message.mentions == []):
        userID = ctx.author.id
        userName = ctx.author.name
        userProfile = ctx.author.avatar_url
    else: #wants to see another user's profile
        userID = ctx.message.mentions[0].id
        userName = ctx.message.mentions[0].name
        userProfile = ctx.message.mentions[0].avatar_url

    if os.path.exists(str(userID) + '.txt'):

        embed = discord.Embed(
            title = 'Inventory',
            color = discord.Color.dark_gray()
        )
        embed.set_author(name=userName, icon_url=userProfile)
        if (listItems(userID) != ''):
            embed.add_field(name='Items', value=listItems(userID))

        
        sortFish(userID)


        for i in range(2, findStat(userID, 4)+3): #UPDATE LATER, FORMULA FOR DISPLAYING WITHOUT 0S
            result = ''
            i = i%(findStat(userID, 4)+1)
            if (sortRarity(userID, rarities[i]) != ''):
                for line in sortRarity(userID, rarities[i]):
                    if not ':0' in line:
                        result += line

                embed.add_field(name='{} Fish'.format(rarities[i]), 
                    value=result.replace(':', ': '), inline=True)

        await ctx.send(embed=embed)
    else:
        await ctx.send("This person doesn't fish.")







@client.command(brief="Gets the information about a fish")
async def data(ctx):
    if os.path.exists(str(ctx.author.id) + '.txt'):
        
        #name, nick, rarity, species, (length, depth, danger level), (evolution, #), spawn phrase, description
        fishData = fishBreed('', '', 0, 0, 0, 0, ('', 0, 0, ''), '', 0, '', '')
        fishData = returnFish(ctx.message.content.lower()[len('f!data '):len(ctx.message.content)], ctx.author.id)


        if findFishLine(ctx.author.id, fishData.name) > -1 or ctx.author.id == 207354353596497930:
            embed = discord.Embed(
            title = 'Fish Databook',
            color = discord.Color.dark_gray()
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=fishData.thumbnail)
            embed.add_field(name='Fish', value=fishData.name, inline=True)
            embed.add_field(name='Rarity', value=rarities[fishData.rarity], inline=True)
            embed.add_field(name='Evolution', value=fishData.evolution[0], inline=True)
            embed.add_field(name='Species', value=species[fishData.species], inline=True)
            embed.add_field(name='Size', value=sizes[fishData.size], inline=True)
            embed.add_field(name='Danger Level', value=dangers[fishData.danger], inline=True)

            await ctx.send(embed=embed)
        else:
            await ctx.send('You do not have this fish.')
    else:
        await ctx.send('This person does not fish.')


def updateEveryone():
   for filename in os.listdir(os.getcwd()):
        if filename.endswith('.txt') and not 'data' in filename:
            text = open(filename, 'r')
            lines = text.readlines()
            #lines.insert(8,"FW:0\n")
            #lines.insert(9,"FH:0\n")
            #lines.insert(10,'FE:0\n')
            lines.insert(13,"Diver Knife:1\n")
            for line in lines:
                line.replace("Gem", "Shard")
            print(lines)
            print('\n\n\n')

            with open(filename, 'w') as k:
                k.writelines(lines)


@client.command(brief="Select your favorite fish to display", aliases=['fav'])
async def favorite(ctx):
    if os.path.exists(str(ctx.author.id) + '.txt'):
        fishName = ctx.message.content.lower()[len('f!favorite '):len(ctx.message.content)]
        for fishy in fishes:
            if (fishName == fishy.name.lower() or fishName == fishy.nick.lower()) and findFishLine(ctx.author.id, fishy.name) > -1:
                text = open(str(ctx.author.id) + '.txt', 'r')
                lines = text.readlines()
                lines[5] = 'Favorite:{}\n'.format(fishy.name)

                with open(str(ctx.author.id) + '.txt', 'w') as k:
                    k.writelines(lines)
                return await ctx.send('Your favorite fish is now the {}!'.format(fishy.name))
        return await ctx.send('You do not have this fish.')














@client.command(brief="Displays the best fishers")
@commands.cooldown(1, 30, commands.BucketType.guild)
async def leaderboard(ctx):

    await client.wait_until_ready()

    ifServer = ctx.message.content.lower()[len('f!leaderboard '):len(ctx.message.content)]
       
    if ifServer.lower() == 'server':
        users = []
        ids = [member.id for member in ctx.message.guild.members]
        for filename in os.listdir(os.getcwd()):
            if filename.endswith('.txt') and not 'data' in filename:
                filename = filename[0:len(filename)-4] #removes .txt
                if int(filename) in ids:
                    ranking = findStat(filename, 2) + (findStat(filename, 3) / (10 ** len(str(findStat(filename, 3))) )) #level.xp
                    users.append((filename, ranking))
        
        users.sort(key=lambda x:x[1], reverse=True)
        users = users[:7]
        
        namesAndLevels = ''
        favFishes = ''
        boatField = ''
        for userRank in users:
            user = await client.fetch_user(userRank[0])
            namesAndLevels += '{} ({})\n'.format(user.name, str(findStat(userRank[0], 2)))
            favFishes += favoriteFish(userRank[0])
            boatField += findStat(userRank[0], 7, False) + '\n'
        
        embed = discord.Embed(
            title = 'Leaderboard',
            color = discord.Color.dark_gray()
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name='User', value=namesAndLevels)
        embed.add_field(name='Boat', value=boatField)
        embed.add_field(name='Favorite Fish', value=favFishes)

        await ctx.send(embed=embed)







    else:
        text = open('data - leaderboard.txt', 'r')
        lines = text.readlines()

        namesAndLevels = ''
        favFishes = ''
        boatField = ''

        for line in lines:
            userID = line[0:len(line)-1]
            user = await client.fetch_user(userID)
            namesAndLevels += '{} ({})\n'.format(user.name, str(findStat(userID, 2)))
            favFishes += favoriteFish(userID)
            boatField += findStat(userID, 7, False) + '\n'
        

        embed = discord.Embed(
            title = 'Leaderboard',
            color = discord.Color.dark_gray()
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name='User', value=namesAndLevels)
        embed.add_field(name='Boat', value=boatField)
        embed.add_field(name='Favorite Fish', value=favFishes)

        await ctx.send(embed=embed)




  







async def updateLeaderboard():
    
    while True:

        users = []

        for filename in os.listdir(os.getcwd()):
            if filename.endswith('.txt') and not 'data' in filename:
                filename = filename[0:len(filename)-4] #removes .txt
                ranking = findStat(filename, 2) + (findStat(filename, 3) / (10 ** len(str(findStat(filename, 3))) )) #level.xp
                users.append((filename, ranking))
        
        users.sort(key=lambda x:x[1], reverse=True)


        text = open('data - leaderboard.txt', 'r')
        lines = text.readlines()
        lines.clear()

        for i in range(10):
            lines.append(users[i][0] + '\n')

        with open('data - leaderboard.txt', 'w') as k:
            k.writelines(lines)

        await asyncio.sleep(60 * 5)











@client.command(brief="Send this message in the channel where you want fish to spawn")
async def channel(ctx):
    channelID = ctx.message.channel.id
    guildID = ctx.message.guild.id

    text = open('data - channels.txt', 'r')
    lines = text.readlines()

    servers = {}
    global resetSpawns
    
    for line in lines:
        colonIndex = line.find(':')
        
        if not client.get_channel(int(line[colonIndex+1:len(line)])):
            lines[lines.index(line)] = ''
        else:
            servers[int(line[0:colonIndex])] = int(line[colonIndex+1:len(line)])


        if guildID in servers:
            lines[lines.index(line)] = '{}: {}\n'.format(guildID, channelID)


            await ctx.send('Channel Rewritten')
            with open(str('data - channels') + '.txt', 'w') as k:
                k.writelines(lines)
            resetSpawns = True
            return resetSpawns

    if not guildID in servers:
        await ctx.send('Channel Added')
        with open(str('data - channels') + '.txt', 'w') as k:
            k.writelines(lines)
            k.write('\n{}: {}'.format(guildID, channelID))
        resetSpawns = True
        return resetSpawns




 
def convertServers():                   #MAKE THIS FUNCTION OBSOLETE IN FUTURE
    text = open('data - channels.txt', 'r')
    lines = text.readlines()

    servers = {}
    
    for line in lines:
        colonIndex = line.find(':')
        servers[int(line[0:colonIndex])] = int(line[colonIndex+1:len(line)])

    return servers














def levelUp(userID):
    print('Checking level... level is now {}'.format(findStat(userID, 2)))
    print('Checking xp... level xp now {}'.format(findStat(userID, 3)))
    xpMod = 60


    if (findStat(userID, 3) > (findStat(userID, 2) * xpMod)):
        
        levelGained = 0
        while ((findStat(userID, 3) / (findStat(userID, 2) * xpMod)) > 1):
            xpLost = -findStat(userID, 2) * xpMod
            print('During calculations... xp is now {}'.format(updateStat(userID, 3, xpLost)))
            levelGained += 1
            print('During calculations... level is now {}'.format(updateStat(userID, 2, levelGained)))
        return True
        
    return False













def createUser(userID):
    if os.path.exists(str(userID) + '.txt'):
        print('User already exists.')
    else:
        print('Creating user.')
        open(str(userID) + '.txt', 'w') #creates new user file
        with open(str(userID) + '.txt', 'a') as k: #opens file to write in
            k.write('UserID:{}\nTotalFish:0\nFisherLevel:1\nFisherXP:0\nTier:1\nFavorite:None\nDoubloons:0\nBoat:Dinghy\nFW:0\nFH:0\nFE:0\nOcto:0\nDinghy:1\n'.format(str(userID)))
            #id-0   fishtotal-1     level-2     xp-3    tierrarity-4    fav-5       doubloons-6     boat-7     fw-8    fh-9   fe-10     octo-11
def findStat(userID, statLine, ifInt=True): #find with line
    
    if statLine == -1: #checks for fish hasnt been caught
        return -1

    if os.path.exists(str(userID) + '.txt'):
        text = open(str(userID) + '.txt', 'r')
        lines = text.readlines()
        colonIndex = lines[statLine].find(':')
        statAmount = lines[statLine][colonIndex+1:len(lines[statLine])]
        if ifInt:
            return int(statAmount)
        else:
            return str(statAmount)[:-1]



def updateStat(userID, statLine, statGained):
    text = open(str(userID) + '.txt', 'r')
    lines = text.readlines()

    colonIndex = lines[statLine].find(':')
    statName = lines[statLine][0:colonIndex]
    statAmount = lines[statLine][colonIndex+1:len(lines[statLine])]
    statAmount = int(statAmount) + statGained

    lines[statLine] = '{}:{}\n'.format(statName, str(statAmount))

    with open(str(userID) + '.txt', 'w') as k:
        k.writelines(lines)

    return str(statAmount)




def findFishLine(userID, name): #find with fish name
    textLine = 0
    with open(str(userID) + '.txt', 'r') as k:
        for line in k:
            if (name + ':') in line and not ':{}'.format(name) in line:
                return textLine
            textLine += 1
    return -1





def rarestFish(userID):
    text = open(str(userID) + '.txt', 'r')
    lines = text.readlines()
    colonIndex = lines[len(lines)-1].find(':')
    statName = lines[len(lines)-1][0:colonIndex]
    amount = lines[len(lines)-1][colonIndex+1:len(lines[len(lines)-1])]
    print(amount)
    for fishy in fishes:
        if fishy.name == statName and amount != 0:
            return fishy
    return findStat(userID, 4)

def favoriteFish(userID):
    text = open(str(userID) + '.txt', 'r')
    lines = text.readlines()
    colonIndex = lines[5].find(':')
    return lines[5][colonIndex+1:len(lines[5])]




def sortRarity(userID, rarity):
    sortedValue = ''
    for fishy in fishes:
        if (rarities[fishy.rarity] == rarity):
            if findStat(userID, findFishLine(userID, fishy.name)) > 0:
                sortedValue += '{}:{}\n'.format(fishy.name, findStat(userID, findFishLine(userID, fishy.name)))
    
    return sortedValue

def listItems(userID):
    sortedValue = ''
    for item in items:
        if findStat(userID, findFishLine(userID, item.name)) >= 0 and findStat(userID, findFishLine(userID, item.name)) > 0:
            sortedValue += '{}: {}\n'.format(item.name, findStat(userID, findFishLine(userID, item.name)))

    return sortedValue

def listBoats(userID):
    sortedValue = ''
    for boat in list(boats.keys()):
        if findStat(userID, findFishLine(userID, boat)) > 0:
            sortedValue += '{}: {}\n'.format(boat, findStat(userID, findFishLine(userID, boat)))
    
    return sortedValue


def sortFish(userID):
    sortedValue = ''
    text = open(str(userID) + '.txt', 'r')
    lines = text.read()

    delIndex = lines.find('Octo:') + len('Octo:') + len(str(findStat(userID, 11, False)))
    #gets the index of end of stats and beginning of fish
    
    lines = lines[0:delIndex]

    sortedValue += '\n'
    sortedValue += listBoats(userID).replace(': ', ':')
    sortedValue += listItems(userID).replace(': ', ':')

    for rarity in rarities:
        sortedValue += sortRarity(userID, rarity)

    with open(str(userID) + '.txt', 'w') as k:
        k.write(lines)
        k.write(sortedValue)


def addLoot(userID, lootName, numberAdded, ifFish):

    if os.path.exists(str(userID) + '.txt'):
        if ifFish:
            updateStat(userID, 1, numberAdded)

        if (findFishLine(userID, lootName) == -1): #adds the fish if doesnt exist
            with open(str(userID) + '.txt', 'a') as k:
                k.write('{}:{}\n'.format(lootName, numberAdded))
        else: #increases the count
            updateStat(userID, findFishLine(userID, lootName), numberAdded)








@client.command()
async def broadcast(ctx):
    if ctx.author.id == 207354353596497930:
        message = ctx.message.content[len('f!broadcast '):len(ctx.message.content)]
        if message == 'd':
            message = '```The bot is going down for testing.```'
        for channel in convertServers().values():
            await client.get_channel(channel).send('{}'.format(message))

@client.command()
async def kill(ctx):
    if ctx.author.id == 207354353596497930:
        guildID = ctx.author.guild.id

        text = open('data - channels.txt', 'r')
        lines = text.readlines()
        
        for line in lines:
            colonIndex = line.find(':')
            if guildID == line[0:colonIndex]:
                lines[lines.index(line)] = ''

        with open(str('data - channels') + '.txt', 'w') as k:
                k.writelines(lines)

        await client.get_channel(convertServers()[guildID]).send('**Leaving server...**')
        await client.get_guild(guildID).leave()


@client.command()
async def calculate(ctx):
    if ctx.author.id == 207354353596497930:
        numerator = ctx.message.content[len('f!calculate '):len(ctx.message.content)]
        print(float(numerator) / sum(fishes.values()))


boostedServers = {}
rarities = [
    'Special', #0
    'Legacy', #1
    'Simple', #2
    'Common', #3
    'Uncommon', #4
    'Rare', #5
    'Exotic', #6
    'Epic', #7
    'Prime', #8
    'Mythic', #9
    'Legendary', #10
    'Ascendant', #11
]

species = [
    'Fish', #0
    'Eel', #1
    'Fishman', #2
    'Squid', #3
    'Serpent', #4
    #'Jellyfish', #2
    #'Clam', #3
    #'Squid', #4
    #'Treasure', #5
    #'Fishman', #6
    #'Whale', #7
    #'God', 
]

dangers = [
    'Harmless', #0
    'F', #1
    'E', #2
    'D', #3
    'C', #4
    'B', #5
    'A', #6
    'S', #7
    'SS', #8
    'SS+', #9
    'SSS', #10
    'SSS+', #11
    'Threat: Critical', #12
    'Threat: Catastrophic', #10
    'Threat: Cataclysmic', #11
    'Hazard' #12
 
]
sizes = [
    'Miniscule', #0
    'Tiny', #1
    'Small', #2
    'Medium', #3
    'Large', #4
    'Huge', #5
    'Massive', #6
    'Gigantic', #7
    'Gargantuan', #8
    'Colossal', #9
    'Boundless' #10

]

phrases = [
    'currently designed for testing {} {}', #0
    '{} {} is lurking.', #1
    '{} {} is gliding across the water.', #2
    '{} {} is lurking...' #3

    #'{} {} has been spotted!', #2
    #'{} rare {} is on the line!', #3
    #'{} {} is visible.', #4
    #'{} {} is... lurking?', #5
    #'{} {} is cutting through the waters!', #6
    #'{} {} is splitting the water.', #7
    #'Something is seen sparkling under the water. Could it be... {} {}?', #8
    #'{} {} is on a rampage!', #9
    #'**A DANGEROUS STORM SHAKES THE SEAS.**\nTentacles burst out from the dark waves and latch onto your vessel...\n {} {} emerges!!!!!!', #10
    #'{} {} is flopping around.', #11
    #'{} {} is sliding around.', #12
    #'{} {} is crawling around.', #13
    #'It is a little windy. {} {} is lurking.', #14
    #'It is a little cold. {} {} is lurking.', #15
    #'It is a little hot. {} {} is lurking.', #16
    #'{} {} is floating atop the water.', #17
    #'There is some sort of light in the water. {} {} has been spotted!', #18
    #'{} {} is lurking in the mist.', #19
    #'{} {} is a glowing amidst the mist.', #20
    #'Something seems to be swimming along the surface, but there is no fish to be found.', #21
]

weapons = {
   weaponType("Diver Knife", "Diver", 0, 10)
}

items = {
    #name, nick, (sellable, doubloons), cost in shop, (hunt level, weight)
    
    itemType('Pickaxe', 'Pick', (False, 0), 500, None),
    itemType('Elemental Shard', 'Shard', (False, 0,), 150, 3),
    itemType('Ugly Hat', 'Hat', (False, 0), 999, None),
    itemType('Bucket of Gray Scales', 'Bucket', (False, 0), 100, None),

    itemType('Mystery Egg', 'Egg', (False, 0), 9999, 100),
    
    itemType('Weapons Ticket', 'Ticket', (False, 0), 0, None),

    itemType('Elemental Orb', 'Orb', (False, 0), 0, 100),

    
    itemType('White Scale', 'White', (True, 1), 0, 1),
    itemType('Red Scale', 'Red', (True, 2), 0, 1),
    itemType('Green Scale', 'Green', (True, 2), 0, 1),
    itemType('Blue Scale', 'Blue', (True, 2), 0, 1),
    itemType('Yellow Scale', 'Yellow', (True, 2), 0, 1),
    itemType('Gray Scale', 'Gray', (True, 4), 0, 1),
    itemType('Purple Scale', 'Purple', (True, 4), 0, 1),
    itemType('Pink Scale', 'Pink', (True, 4), 0, 1),
    itemType('Black Scale', 'Black', (True, 8), 0, 1),
    itemType('Rainbow Scale', 'Rainbow', (True, 10), 0, 2),
    itemType('Serpent Scale', 'Serpent', (True, 30), 0, 3),

    itemType('Topaz', 'Topaz', (True, 15), 0, 2),
    itemType('Garnet', 'Garnet', (True, 15), 0, 2),
    itemType('Amethyst', 'Amethyst', (True, 30), 0, 2),
    itemType('Ruby', 'Ruby', (True, 45), 0, 2),
    itemType('Sapphire', 'Sapphire', (True, 45), 0, 2),
    itemType('Emerald', 'Emerald', (True, 45), 0, 2),
    itemType('Diamond', 'Diamond', (True, 100), 0, 3),
    itemType('Moonstone', 'Moonstone', (True, 50), 0, 100),
    itemType('Umbrium Shard', 'Umbrium', (True, 5), 0, 100),

    itemType('Plastic Piece', 'Plastic', (False, 0), 0, 1),
    itemType('Heart Scale', 'Heart', (True, 20), 0, 2),
    itemType('Fragment of Light', 'Fragment', (False, 0), 0, 100),
    itemType('Bronze Part', 'Bronze', (False, 0), 0, 100),

    itemType('Spear', 'Spear', (False, 0), 0, 100),
    itemType('Harpoon', 'Harpoon', (False, 0), 0, 100),
    itemType('Wand', 'Wand', (False, 0), 0, 100),

    itemType('Reset Potion', 'Reset', (False, 0), 0, 100),
    itemType('Boost Potion', 'Boost', (False, 0), 0, 100),
    itemType('Transform Potion', 'Transform', (False, 0), 0, 100),

    
}


boats = {
    "Dinghy": (0, 'https://cdn.discordapp.com/attachments/753825392753770616/897258399123787806/dinghy.png'),
    "Caravel": (250, 'https://cdn.discordapp.com/attachments/753825392753770616/898064697088172082/caravel.png'),
    "Galleon": (1000, 'https://cdn.discordapp.com/attachments/753825392753770616/902304236216418444/galleon.png'),
    "Frigate": (3000, 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'),
    "Steamship": (0, 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png')
    #going to add Xebec, Jet Ski (maybe), Timberclad

}
#https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png

fishes = {

    #rarity, species, size, danger
    #(Ev, #, XP, ItemNeeded), ItemGiven
    #fish : spawnrate

    #jumbo, wolf, wolfpack (hunting mechanic)
    
    #Simple
    fishBreed('Normal Fish', 'Normal', len(rarities)-10, 0, 1, 0, ('Odd Fish', 10, 1, None), 
        None, None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/891792836016627742/normalfish.png'): 1.2,

    fishBreed('Guppy', 'Guppy', len(rarities)-10, 0, 0, 0, ('Jumbo Fish', 30, 1, None), 
        None, None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/892201740894621736/guppy.png'): .6,

    fishBreed('White Fish', 'White', len(rarities)-10, 0, 1, 0, ('Sky Serpent', 30, 1, 'Serpent Scale'), 
        'White Scale', None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/891792390300532736/whitefish.png'): .9,

    fishBreed('Red Fish', 'Red', len(rarities)-10, 0, 1, 0, ('Fire Fish', 1, .8, 'Elemental Shard'), 
        'Red Scale', None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/891838803067678781/redfish.png'): .7,

    fishBreed('Green Fish', 'Green', len(rarities)-10, 0, 1, 0, ('Kelp Fish', 1, .8, 'Elemental Shard'), 
        'Green Scale', None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/891838780347150366/greenfish.png'): .7,

    fishBreed('Blue Fish', 'Blue', len(rarities)-10, 0, 1, 0, ('Ice Fish', 1, .8, 'Elemental Shard'), 
        'Blue Scale', None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/891838761611186226/bluefish.png'): .7,

    fishBreed('Yellow Fish', 'Yellow', len(rarities)-10, 0, 1, 0, ('Lightning Fish', 1, .8, 'Elemental Shard'), 
        'Yellow Scale', None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/898064652179767336/yellowfish.png'): .7,

    fishBreed('Happy Fish', 'Happy', len(rarities)-10, 0, 1, 0, ('Coming Soon', 0, .8, None), 
        None, None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/891792943520809060/happyfish.png'): .2,

    fishBreed('Plastic Fish', 'Plastic', len(rarities)-10, 0, 1, 0, ('None', 0, 1, None), 
        'Plastic Piece', None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/896253652589772800/plasticfish.png'): .3,

    fishBreed('Gold Fish', 'Gold', len(rarities)-10, 0, 1, 0, ('Cursed Fish', 0, .5, 'Umbrium Shard'), 
        None, None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/891792882082652250/goldfish.png'): .2,

    fishBreed('Coal Fish', 'Coal', len(rarities)-10, 0, 1, 0, ('Diamond Fish', 50, .8, None), 
        None, None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): .2,
    
    fishBreed('Lesser Eel', 'Lesser', len(rarities)-10, 1, 2, 1, ('Greater Eel', 9, .7, None),
        None, None, phrases[2], 'https://cdn.discordapp.com/attachments/753825392753770616/894679371288281108/lessereel.png'): .3,





    #Common
    fishBreed('Odd Fish', 'Odd', len(rarities)-9, 0, 1, 0, ('Bizarre Fish', 5, .8, None), 
        None, None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/892261429770604564/oddfish.png'): .03,

    fishBreed('Jumbo Fish', 'Jumbo', len(rarities)-9, 0, 4, 0, ('Coming Soon', 0, .7, None), 
        None, None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/892641118364250172/jumbofish.png'): .05,

    fishBreed('Gray Fish', 'Gray', len(rarities)-9, 0, 1, 0, ('Coming Soon', 0, .8, None), 
        'Gray Scale', None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/892201933983604747/grayfish.png'): .2,

    fishBreed('Purple Fish', 'Purple', len(rarities)-9, 0, 1, 0, ('Toxic Fish', 3, .8, 'Elemental Shard'), 
        'Purple Scale', None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/892201955886243970/purplefish.png'): .2,

    fishBreed('Pink Fish', 'Pink', len(rarities)-9, 0, 1, 0, ('Heart Fish', 5, .8, None), 
        'Pink Scale', None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/902304302339600424/pinkfish.png'): .2,

    fishBreed('Fire Fish', 'Fire', len(rarities)-9, 0, 1, 1, ('Fire Serpent', 10, .5, 'Elemental Orb'), 
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894144139078279188/firefish.png'): 0,

    fishBreed('Kelp Fish', 'Kelp', len(rarities)-9, 0, 1, 0, ('Kelp Serpent', 10, .5, 'Elemental Orb'), 
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894144158703452170/kelpfish.png'): 0,

    fishBreed('Ice Fish', 'Ice', len(rarities)-9, 0, 1, 0, ('Ice Serpent', 10, .5, 'Elemental Orb'), 
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894144285610504212/icefish.png'): 0,

    fishBreed('Lightning Fish', 'Lightning', len(rarities)-9, 0, 1, 2, ('Lightning Serpent', 10, .5, 'Elemental Orb'), 
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/898076629279064134/lightningfish.png'): 0,

    fishBreed('Ore Fish', 'Ore', len(rarities)-9, 0, 3, 0, ('Varying Gem Fish', 0, .8, None),
        None, None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/896229691315351572/orefish.png'): .2,

    fishBreed('Wolf Fish', 'Wolf', len(rarities)-9, 0, 2, 1, ('Alpha Wolf Fish', 5, .5, None), 
        None, (1, 5), phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/901201436044570666/wolffish_-_hunt.png'): .07,

    fishBreed('Topaz Fish', 'Topaz', len(rarities)-9, 0, 2, 0, ('None', 0, .8, None),
        'Topaz', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/900213310694236160/topazfish.png'): 0,

    fishBreed('Garnet Fish', 'Garnet', len(rarities)-9, 0, 2, 0, ('None', 0, .8, None),
        'Garnet', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/900210421611499560/garnetfish.png'): 0,

    fishBreed('Goblin Fish', 'Goblin', len(rarities)-9, 0, 2, 1, ('Hobgoblin Fish', 9, .8, None),
        None, None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/904912549051502592/goblinfish.png'): .2,

     fishBreed('Greater Eel', 'Greater', len(rarities)-9, 1, 3, 2, ('Superior Eel', 6, .4, None),
        None, None, phrases[2], 'https://cdn.discordapp.com/attachments/753825392753770616/894858549446991902/greatereel.png'): .008,


    
    
    #Uncommon
    fishBreed('Bizarre Fish', 'Bizarre', len(rarities)-8, 0, 3, 1, ('Fishman', 3, .4, None),
        None, None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/896229772873568298/bizarrefish.png'): 0,
    
    fishBreed('Black Fish', 'Black', len(rarities)-8, 0, 2, 1, ('Dark Fish', 3, .2, None),
        'Black Scale', None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/894858878464974898/blackfish.png'): .05,

    fishBreed('Shiny Fish', 'Shiny', len(rarities)-8, 0, 1, 0, ('Glow Fish', 5, .2, None),
        None, None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/904961744420601876/shinyfish.png'): .05,

    fishBreed('Toxic Fish', 'Toxic', len(rarities)-8, 0, 1, 3, ('Coming Soon', 0, 0, None),
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/900209763533590528/toxicfish.png'): 0,

    fishBreed('Heart Fish', 'Heart', len(rarities)-8, 0, 0, 0, ('None', 0, .5, None),
        'Heart Scale', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/902304280571170906/heartfish.png'): 0,

    fishBreed('Ghost Fish', 'Ghost', len(rarities)-8, 0, 2, 0, ('Phantom Fish', 10, .2, None),
        None, None, phrases[3], 'https://cdn.discordapp.com/attachments/753825392753770616/895202452259876864/ghostfish.png'): .04,

    fishBreed('Alpha Wolf Fish', 'Alpha', len(rarities)-8, 0, 3, 3, ('None', 0, 0, None),
        None, (2, 10), phrases[3], 'https://cdn.discordapp.com/attachments/753825392753770616/901201430407417886/alphawolffish_-_hunt.png'): .0,

    fishBreed('Amethyst Fish', 'Amethyst', len(rarities)-8, 0, 2, 0, ('None', 0, .6, None),
        'Amethyst', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/900209867132911636/amethystfish.png'): 0,

    fishBreed('Ruby Fish', 'Ruby', len(rarities)-8, 0, 2, 0, ('None', 0, .6, None),
        'Ruby', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/900209787285962782/rubyfish.png'): 0,
    
    fishBreed('Sapphire Fish', 'Sapphire', len(rarities)-8, 0, 2, 0, ('None', 0, .6, None),
        'Sapphire', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/900209821700206612/sapphirefish.png'): 0,

    fishBreed('Emerald Fish', 'Emerald', len(rarities)-8, 0, 2, 0, ('None', 0, .6, None),
        'Emerald', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/900209908237099069/emeraldfish.png'): 0,
        
    fishBreed('Hobgoblin Fish', 'Hob', len(rarities)-8, 0, 3, 3, ('Ogre Fish', 3, .8, None),
        None, None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/904912550402097172/hobgoblinfish.png'): 0,

    fishBreed('Superior Eel', 'Superior', len(rarities)-8, 1, 4, 4, ('High Eel', 3, .5, None),
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/897564750496550912/superioreel.png'): 0,
        

    
    #Rare
    fishBreed('Fishman', 'Fishman', len(rarities)-7, 2, 4, 2, ('Varying Fishman Classes', 0, 0, None),
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/904912544932708422/fishman.png'): 0,

    fishBreed('Fire Serpent (Runt)', 'Fire Runt', len(rarities)-7, 4, 5, 4, ('None', 0, .03, None),
        'Serpent Scale', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,

    fishBreed('Kelp Serpent (Runt)', 'Kelp Runt', len(rarities)-7, 4, 5, 3, ('None', 0, .03, None),
        'Serpent Scale', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,
        
    fishBreed('Ice Serpent (Runt)', 'Ice Runt', len(rarities)-7, 4, 5, 3, ('None', 0, .03, None),
        'Serpent Scale', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,
        
    fishBreed('Lightning Serpent (Runt)', 'Lightning Runt', len(rarities)-7, 4, 5, 5, ('None', 0, .03, None),
        'Serpent Scale', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,

    fishBreed('Sky Serpent (Runt)', 'Sky', len(rarities)-7, 4, 5, 5, ('None', 0, .03, None),
        'Serpent Scale', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,

    fishBreed('Dark Fish', 'Dark', len(rarities)-7, 0, 2, 3, ('Moon Fish', 3, .05, 'Moonstone'),
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,

     fishBreed('Rainbow Fish', 'Rainbow', len(rarities)-7, 0, 0, 0, ('None', 0, .05, None),
        'Rainbow Scale', None, phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/898069367621836830/rainbowfish.png'): .004,   

    fishBreed('Phantom Fish', 'Phantom', len(rarities)-7, 0, 3, 2, ('Coming Soon', 0, 0, None),
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,

    fishBreed('Glow Fish', 'Glow', len(rarities)-7, 0, 1, 0, ('Coming Soon', 0, .2, None),
        'Fragment of Light', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/904961719229612082/glowfish.png'): 0,
    
    fishBreed('Tiger Fish', 'Tiger', len(rarities)-7, 0, 4, 4, ('None', 0, .08, None),
        None, (2, 20), phrases[1], 'https://cdn.discordapp.com/attachments/753825392753770616/901201435209900052/tigerfish_-_hunt.png'): .002,

    fishBreed('Diamond Fish', 'Diamond', len(rarities)-7, 0, 2, 0, ('None', 0, .4, None),
        'Diamond', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/910246791088308274/diamondfish.png'): 0,

    fishBreed('Moonstone Fish', 'Moonstone', len(rarities)-7, 0, 2, 0, ('None', 0, .4, None),
        'Moonstone', None, phrases[0], 'https://cdn.discordapp.com/attachments/221786569164455947/906970439031599194/moonstonefish.png'): 0,

    fishBreed('Ogre Fish', 'Ogre', len(rarities)-7, 0, 4, 5, ('Coming Soon', 0, 1, None),
        None, (0, 0), phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/904914577517609001/ogrefish_-_hunt.png'): 0,

    fishBreed('High Eel', 'High', len(rarities)-7, 1, 5, 5, ('Coming Soon', 0, 0, None),
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,


    #Exotic 
    fishBreed('Fire Serpent (Average)', 'Fire Average', len(rarities)-6, 4, 6, 5, ('None', 0, .03, None),
        'Serpent Scale', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,

    fishBreed('Ice Serpent (Average)', 'Ice Average', len(rarities)-6, 4, 6, 4, ('None', 0, .03, None),
        'Serpent Scale', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,
        
    fishBreed('Kelp Serpent (Average)', 'Kelp Average', len(rarities)-6, 4, 6, 4, ('None', 0, .03, None),
        'Serpent Scale', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,
        
    fishBreed('Lightning Serpent (Average)', 'Lightning Average', len(rarities)-6, 4, 6, 6, ('None', 0, .03, None),
        'Serpent Scale', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,

    fishBreed('Sky Serpent (Average)', 'Sky Average', len(rarities)-6, 4, 6, 6, ('Coming Soon', 0, .03, None),
        'Serpent Scale', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,

    fishBreed('Umbrium Fish', 'Umbrium', len(rarities)-6, 0, 2, 12, ('None', 0, .2, None),
        'Umbrium Shard', None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,

    fishBreed('Bronze Fish', 'Bronze', len(rarities)-6, 0, 1, 0, ('None', 0, 0, None),
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,

   fishBreed('Moon Fish', 'Moon', len(rarities)-6, 0, 0, 5, ('Coming Soon', 0, 0, None),
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,






    #Special
    fishBreed('Ugly Red Hat Fish', 'Ugly', 0, 0, 1, 0, ('None', 0, 0, None),
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/895421001960157234/uglyredhatfish.png'): 0,

    fishBreed('Weird Squid', 'Squid', 0, 3, 3, 0, ('Coming Soon', 0, 0, None),
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png'): 0,

    fishBreed('Fishman-Warrior', 'Warrior', 0, 2, 4, 4, ('None', 0, 0, None),
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/904912547667378236/fishman-warrior.png'): 0,
    
    fishBreed('Fishman-Hunter', 'Hunter', 0, 2, 4, 3, ('None', 0, 0, None),
        None, (3, 15), phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/904912871350227006/fishman-hunter_-_hunt.png'): 0,
    
    fishBreed('Fishman-Enchanter', 'Enchanter', 0, 2, 4, 3, ('None', 0, 0, None),
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/904912543036895282/fisherman-enchanter.png'): 0,


    
        

    


    #Legacy
    fishBreed('Beta Fish', 'Beta', 1, 0, 1, 3, ('None', 0, .1, None), 
        None, (1, 3), phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/901256951646797834/betafish_-_hunt.png'): 0,

    fishBreed('Developer Fish', 'Dev', 1, 0, 1, 0, ('None', 0, 0, None),
       None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894863470720319528/developerfish.png'): 0,
    
      fishBreed('Fishman-Thugger', 'Thugger', 1, 2, 4, 6, ('None', 0, 0, None),
        None, None, phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/906068596663394344/fishman-thugger.png'): 0,





   



}

for i in range(500):
    fishes[fishBreed('Pack of Wolf Fish Lv.{}'.format(i), 'Pack', 0, 0, min(len(sizes)-1, int(math.pow(i, 0.2875))+1), 12, ('None', 0, 1, None),
        None, (max(1, int(math.pow(i, 0.2631))), i), phrases[0], 'https://cdn.discordapp.com/attachments/753825392753770616/894679153427742720/missing.png')] = 0
    




client.run('NzM4ODYwNTE3NTIyNjY5NjE5.XySDeg.u3Q7kTob5cRCWn7xIUUf4r7vvs0')




