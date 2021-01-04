import discord
from discord.ext import commands
from main import isMalicious
from secret import CLIENT_SECRET

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('Logged in as {0.user}.'.format(client))
    print("Epilepsy Guard is online.")

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  for attachment in message.attachments:
    if attachment.filename.endswith('.gif'):
        text = message.content
        author = message.author
        await message.channel.purge(limit=1)

        if (isMalicious(attachment.proxy_url)): # proxy temporarily persists after deletion
            await message.channel.send('bad :(')
        else:
            await message.channel.send('good :)')
            # author_full_user = author.name + '#' + author.discriminator
            # await message.channel.send('**' + author_full_user + '**:\n>>> ' + text)


client.run(CLIENT_SECRET)