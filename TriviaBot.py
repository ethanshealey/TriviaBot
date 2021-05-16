import asyncio
import html
import json
import os
import random
from urllib.request import urlopen

import discord
import requests
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return

    content = msg.content
    if content.startswith('?'):
        content = content.split(' ')
        if len(content) == 1 and content[0] == '?help':
            # help prompt
            embed = discord.Embed(title='Help', color=0x1FB3FC)
            embed.add_field(name='Welcome to TriviaBot!', value='How to use:\n• To play: type `?triv` in chat\n• To respond: TriviaBot will automatically react with the possible options, click on the option you think is correct!', inline=False)
            await msg.channel.send(embed=embed)

        elif len(content) == 1 and content[0] == '?triv':
            # get data
            url = 'https://opentdb.com/api.php?amount=1'
            data = json.loads(urlopen(url).read().decode("utf-8"))

            #parse data
            data = data['results'][0]
            cat = html.unescape(data['category'])
            question = html.unescape(data['question'])
            diff = html.unescape(data['difficulty'])
            type = html.unescape(data['type'])
            correct_ans = html.unescape(data['correct_answer'])
            if not type == 'boolean':
                possible_ans = [html.unescape(d) for d in data['incorrect_answers']]
                possible_ans.append(correct_ans)
            else:
                possible_ans = ['True', 'False']
            
            # shuffle ans
            if not type == 'boolean':
                random.shuffle(possible_ans)

            # create embed
            embed = discord.Embed(title="Welcome to Trivia!", color=0x1FB3FC)
            embed.add_field(name='Category', value=cat, inline=False)
            embed.add_field(name='Difficulty', value=diff, inline=False)
            if not type == 'boolean':
                embed.add_field(name='Question', value=question + f'\n\nA) {possible_ans[0]}\nB) {possible_ans[1]}\nC) {possible_ans[2]}\nD) {possible_ans[3]}', inline=False)
            else: 
                embed.add_field(name='Question', value=question + f'\n\nTrue or False?', inline=False)
            # send embeded message
            m = await msg.channel.send(embed=embed)

            if not type == 'boolean':
                emotes = {'🇦': possible_ans[0], '🇧': possible_ans[1], '🇨': possible_ans[2], '🇩': possible_ans[3]}
            else:
                emotes = {'🇹': possible_ans[0], '🇫':possible_ans[1]}

            for emote in emotes:
                await m.add_reaction(emote)

            # wait for a response
            hasAnswered, ans = False, None
            while not hasAnswered:
                await asyncio.sleep(1)
                m = await msg.channel.fetch_message(m.id)

                if not type == 'boolean':
                    A = get(m.reactions, emoji=list(emotes)[0])
                    B = get(m.reactions, emoji=list(emotes)[1])
                    C = get(m.reactions, emoji=list(emotes)[2])
                    D = get(m.reactions, emoji=list(emotes)[3])

                    # find which answer the user gave
                    if A and A.count > 1:
                        hasAnswered, ans = True, 0
                    elif B and B.count > 1:
                        hasAnswered, ans = True, 1
                    elif C and C.count > 1:
                        hasAnswered, ans = True, 2
                    elif D and D.count > 1:
                        hasAnswered, ans = True, 3

                else:
                    T = get(m.reactions, emoji=list(emotes)[0])
                    F = get(m.reactions, emoji=list(emotes)[1])

                    if T and T.count > 1:
                        hasAnswered, ans = True, 0
                    elif F and F.count > 1:
                        hasAnswered, ans = True, 1

            # respond
            if possible_ans[ans] == correct_ans:
                embed = discord.Embed(title="Correct!", description="Good job!", color=0x68FF38)
            else:
                embed = discord.Embed(title="Incorrect!", description=f"Sorry! The correct answer was {correct_ans}", color=0xFC1F4E)       
            await msg.channel.send(embed=embed)

            print(correct_ans, possible_ans[ans])

        '''
        elif len(content) == 2 and content[0] == '?triv' and content[1] == 'adv':
            await msg.channel.send('Here is the prompt for an advanced question!')

        elif len(content) == 4 and content[0] == '?triv' and content[1] == 'adv':
            await msg.channel.send('Here is an advanced question!')
        '''
    
client.run(TOKEN)
