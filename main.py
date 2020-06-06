import discord
import random

tokeny = []
with open("tokeny.txt") as token_plik:
    for line in token_plik:
        tokeny.append(line)

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!pociagnij'):
        numer = random.randint(1, 2)
        if numer == 1:
            await message.author.send("strazniczka")
        elif numer == 2:
            await message.author.send("ksiaze")



client.run(tokeny[0])