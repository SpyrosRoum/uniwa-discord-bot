from difflib import get_close_matches
import asyncio
from datetime import datetime, timedelta
from time import time, sleep
import json
from os.path import isfile as fexists

import discord
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup as soup

token = "token"
channel = 'channel id'
url = "http://www.ice.uniwa.gr/announcements-all/"
wres = 18000 # 5 hours to secs
json_file_name = 'posted.json'

grafeiaKathigitwn = {
    'βασιλας'       : 'Κ16.115',
    'γαλιωτου'      : 'Κ16.122',
    'γεωργουλη'     : 'Κ16.216',
    'γιαννακοπουλος': 'Στο διαδρομο του εργαστηριου SUN',
    'διλιντας'      : 'Κ16.203',
    'ελληνας'       : 'Κ16.203',
    'καρανικολας'   : 'Κ16.120',
    'κεχαγιας'      : 'Κ16.116',
    'κουκουλετσος'  : 'Κ16.204',
    'μαγος'         : 'Κ16.119',
    'μαμαλης'       : 'Κ16.120-121',
    'μαστοροκωστας' : 'Κ16.204',
    'μιαουλης'      : 'Κ16.118',
    'νικολοπουλος'  : 'Στο διαδρομο του εργαστηριου SUN',
    'παντζιου'      : 'Κ16.115',
    'πρεζερακος'    : 'Κ16.203',
    'σαμαρακου'     : 'Κ16.208',
    'σγουροπουλου'  : 'Κ16.123',
    'σκουρλας'      : 'Κ16.120-121',
    'χαλαρης'       : 'Κ16.120-121',
    'μπογρης'       : 'Κ16.999',
    'φατουρος'      : 'Κ16.204',
    'βουλοδημος'    : 'Κ16.118',
    'καντζαβελου'   : 'Κ16.122',
    'καρκαζης'      : 'Κ16.203',
    'κουμπουρος'    : 'Κ16.122',
    'ξυδας'         : 'Κ16.120-121',
    'μπαρδης'       : 'Κ16.199',
    'βελωνη'        : 'Κ16.204',
    'γεωργουλακη'   : 'Κ16.999',
    'μελετιου'      : 'K10.018',
    'γιαλπας'       : 'Κ16.121',
    'παυλιδης'      : 'Κ16.ΚΔΕ',
}

client = commands.Bot(command_prefix=";")
session = aiohttp.ClientSession(loop=client.loop)

async def getNotifications():
    notifications = {}
    now = datetime.now()

    posted = {}
    if fexists(json_file_name):
        with open(json_file_name) as json_file:
            posted = json.load(json_file)

    # convert strings to datetime objects
    for key in posted:
        posted[key] = datetime.strptime(posted[key], '%d/%m/%Y')

    posted = { link : date for link, date in posted.items() if date.date() > (now - timedelta(days=2)).date() }


    async with session.get(url) as r:
        if r.status != 200:
            return {}
        page_html = await r.text()

    page_soup = soup(page_html, "html.parser")
    anakoinwseis = page_soup.find_all('div', {'class': 'col-lg-12 col-md-12 col-sm-12 col-xs-12 single_post_row'})
    for anakoinwsi in anakoinwseis:
        date = datetime.strptime(anakoinwsi.find('div', {'class': 'single_post_date'}).contents[0].strip(), '%d/%m/%Y')
        title = anakoinwsi.find('div', {'class': 'single_post_title'}).contents[0].strip()
        anakoinwsi = str(anakoinwsi)
        link = anakoinwsi[anakoinwsi.find('http'):anakoinwsi.find('">')].replace('amp;', '')
        if date.date() < (now - timedelta(seconds=wres)).date() or link in posted:
            break
        posted[link] = date
        notifications[link] = title

    # convert datetime objects to strings to dump it to json file
    for key in posted:
        posted[key] = posted[key].strftime('%d/%m/%Y')
    with open(json_file_name, 'w') as json_file:
        json.dump(posted, json_file)

    return notifications


async def findProgramma(programma):
    async with session.get(url) as r:
        if r.status != 200:
            return None, None
        page_html = await r.text()

    page_soup = soup(page_html, "html.parser")
    anakoinwseis = page_soup.find_all('div', {'class': 'col-lg-12 col-md-12 col-sm-12 col-xs-12 single_post_row'})
    for anakoinwsi in anakoinwseis:
        title = anakoinwsi.find('div', {'class': 'single_post_title'}).contents[0].strip()
        anakoinwsi = str(anakoinwsi)
        link = anakoinwsi[anakoinwsi.find('http'):anakoinwsi.find('">')].replace('amp;', '')
        if programma in title.lower():
            return title, link
    return None, None


@client.event
async def on_ready():
    print("Bot is online")

@client.event
async def on_message(message):
    message.content = message.content.lower()
    if message.content.startswith(";βρες") or message.content.startswith(";vres"):
        author = message.author
        args = message.content.split(" ")
        if " ".join(args[1:3]) == 'προγραμμα μαθηματων' or " ".join(args[1:3]) == 'πρόγραμμα μαθημάτων'\
                or " ".join(args[1:3]) == 'programma mathimatwn':
            title, link = await findProgramma('ωρολόγιο πρόγραμμα')
            if title:
                embed = discord.Embed()
                embed.add_field(name=title, value=link, inline=False)
                await author.send(embed=embed)
            else:
                await author.send('Site is down')
        elif " ".join(args[1:3]) == 'προγραμμα εξεταστικης' or " ".join(args[1:3]) == 'πρόγραμμα εξεταστικής' \
                or " ".join(args[1:3]) == 'programma eksetastikis':
            title, link = await findProgramma('πρόγραμμα εξεταστικής')
            if title:
                embed = discord.Embed()
                embed.add_field(name=title, value=link, inline=False)
                await author.send(embed=embed)
            else:
                await author.send('Site is down')
        elif args[1] == 'γραφειο' or args[1] == 'γραφείο' or args[1] == 'grafeio':
            matches = get_close_matches(args[2], grafeiaKathigitwn)
            if matches:
                await author.send(matches[0] + ': ' + grafeiaKathigitwn[matches[0]])
            else:
                await author.send('Δεν ξερω που ειναι το γραφειο του ' + args[2])
    elif message.content == ";help":
        author = message.author
        msg = '''***command list***
        ;βρες προγραμμα μαθηματων
        ;βρες προγραμμα εξεταστικης
        ;βρες γραφειο ονομα_καθηγητη'''
        await author.send(msg)


async def post():
    await client.wait_until_ready()
    while not client.is_closed():
        startTime = datetime.now()
        anakoinwseis = await getNotifications()
        for key in anakoinwseis.keys():
            embed = discord.Embed()
            embed.add_field(name=anakoinwseis[key], value=key, inline=False)
            chn = client.get_channel(channel)
            await chn.send('@everyone', embed=embed)
        await asyncio.sleep(wres + (startTime - datetime.now()).total_seconds())


client.loop.create_task(post())
client.run(token)
