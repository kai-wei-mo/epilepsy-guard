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
            author_full_user = author.name + '#' + author.discriminator
            await message.channel.purge(limit=1)

            if (isMalicious(attachment.proxy_url)): # proxy temporarily persists after deletion
                e = discord.Embed(title=author_full_user + ' sent a GIF.', description='', color=0xff6962)
                e.add_field(name="ANALYSIS:", value="We determined that your GIF is capable of inducing epileptic seizures.\nFor the safety of you and your server, we have removed your GIF.", inline=False)
                e.add_field(name="USER MESSAGE:", value='>>> ' + text, inline=False)
            else:
                e = discord.Embed(title=author_full_user + ' sent a GIF.', description='', color=0x77dd76)
                e.add_field(name="ANALYSIS:", value="This GIF is safe to watch.", inline=False)
                e.add_field(name="USER MESSAGE:", value='>>> ' + text, inline=False)
                e.set_image(url=attachment.proxy_url)

            await message.channel.send(embed=e)


client.run(CLIENT_SECRET)