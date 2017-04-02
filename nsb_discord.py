import discord as discord_api
import asyncio
import os
import threading
import cotn_twitter
import imp

PYTHONASYNCIODEBUG = 1
client = discord_api.Client()
global_twitter = None

async def update_boards(twitter):
    for msg, linked_data in cotn_twitter.update(twitter):
        disc_id = linked_data['discord']['id']

        if disc_id:
            await post('<@{}>{}'.format(disc_id, msg))
        else:
            await post('{}{}'.format(linked_data['steam']['personaname'],
                msg))

async def background_task(twitter):
    await client.wait_until_ready()
    await asyncio.sleep(20)
    print('starting background task')
    while True:
        await update_boards(twitter)
        await asyncio.sleep(300)

@client.event
async def on_ready():
    print('logged in as {}'.format(client.user.name))
    #print('starting thread')
    #ch = client.get_channel('296608387808886784')
    #await client.send_message(ch, 'hello')

    #asyncio.ensure_future(task())
    #print('thread started')


@client.event
async def on_message(message):
    #print(message.content)
    if message.content.startswith('!scorebot'):
        if message.author.id != '84627464709472256':
            await post('beep boop, not authorized, exterminate')
        else:
            if 'update' in message.content:
                await update_boards(global_twitter)
            if 'reload' in message.content:
                imp.reload(cotn_twitter)


        #await client.send_message(message.channel, 'hello? :3')

async def post(text):
    #botspam
    ch = client.get_channel('296636142210646016') #botspam
    #ch = client.get_channel('296608387808886784') #tnsb

    await client.send_message(ch, text)

def run(token, twitter):
    global global_twitter
    global_twitter = twitter
    client.loop.create_task(background_task(twitter))
    try:
        client.run(token)
    except:
        e = sys.exc_info()[0]
        print('caught exception {}\nlogging out'.format(e))
        client.logout()

