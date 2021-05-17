# Created by Ethan Shealey
# Last updated: 5/17/2021
# 
# TriviaBot! alllows you and your friends to play trivia in your chat!
#
# Run with `python3 TriviaBot.py`

import asyncio, html, json, os, random, discord, requests, sqlite3, sys
from sqlite3 import Error
from urllib.request import urlopen
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
con = sqlite3.connect('player_stats.db')
cursorObj = con.cursor()
client = discord.Client()

async def get_user(m):
    users = []

    for react in m.reactions:
        async for u in react.users():
            if u.id != 843268722658377758:
                users.append(u)
    if len(users) > 0:
        username = users[0].name
        user = await client.fetch_user(users[0].id)
    else:
        user = msg.author
    
    return user, username

def get_subjects_and_codes():
    subjects = ['Animals', 'Art', 'Celebrities', 'Entertainment', 'Entertainment: Board Games', 'Entertainment: Books', 'Entertainment: Cartoon & Animations', 'Entertainment: Comics', 'Entertainment: Film', 'Entertainment: Japanese Anime & Manga', 'Entertainment: Music', 'Entertainment: Musicals & Theatres', 'Entertainment: Television', 'Entertainment: Video Games', 'General Knowledge', 'Geography', 'History', 'Mythology', 'Politics', 'Science', 'Science & Nature', 'Science: Computers', 'Science: Gadgets', 'Science: Mathematics', 'Sports', 'Vehicles']
    entertainment_list = ['5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
    science_list = ['21', '22', '23', '24']
    subject_codes = {'1': 27, '2': 25, '3': 26, '5': 16, '6': 10, '7': 32, '8': 29, '9': 11, '10': 31, '11': 12, '12': 13, '13': 14, '14': 15, '15': 9, '16': 22, '17': 23, '18': 20, '19': 24, '21': 17, '22': 18, '23': 30, '24': 19, '25': 21, '26': 28}
    subject_codes['4'] = subject_codes[entertainment_list[random.randint(0, len(entertainment_list)-1)]]
    subject_codes['20'] = subject_codes[science_list[random.randint(0, len(science_list)-1)]]

    return subjects, science_list, subject_codes

def get_url(content, subject_codes):
    url = 'https://opentdb.com/api.php?amount=1'
    if len(content) == 2:
        if content[1].isdigit():
            url += '&category=' + str(subject_codes[content[1]])
        if content[1].lower() == 'easy' or content[1].lower() == 'medium' or content[1].lower() == 'hard':
            url += '&difficulty=' + content[1].lower()

    elif len(content) == 3:
        if content[1].isdigit():
            url += '&category=' + str(subject_codes[content[1]])
        elif content[2].isdigit():
            url += '&category=' + str(subject_codes[content[2]])

        if content[1].lower() == 'easy' or content[1].lower() == 'medium' or content[1].lower() == 'hard':
            url += '&difficulty=' + content[1]
        elif content[2].lower() == 'easy' or content[2].lower() == 'medium' or content[2].lower() == 'hard':
            url += '&difficulty=' + content[2]

    return url

def add_if_new_user(user):
    query = ("SELECT * FROM stats WHERE username=?")
    data = [i for i in cursorObj.execute(query, (str(user),))]
    if data == []:
        # insert new player into database
        query = ("INSERT INTO stats (username) values (?)")
        cursorObj.execute(query, (str(user),))
        con.commit()
        print('added user', user, 'to db')
    else:
        print('user', user, 'is requesting a question')

def update_score(user, correct):
    if correct:
        query = ("UPDATE stats SET correct = correct + 1 WHERE username=?")
    else:
        query = ("UPDATE stats SET incorrect = incorrect + 1 WHERE username=?")
    cursorObj.execute(query, (str(user),))
    con.commit()

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='?help'))

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return

    content = msg.content
    if content.startswith('?'):
        content = content.split(' ')

        subjects, science_list, subject_codes = get_subjects_and_codes()

        if len(content) == 1 and content[0] == '?help':
            # help prompt
            embed = discord.Embed(title='Help', color=0x1FB3FC)
            embed.add_field(name='Welcome to TriviaBot!', value='To play, type `?triv` in chat, then you have 30 seconds to answer!', inline=False)#, value="""How to use:\n• To play: type ```?triv``` in chat\n• OPTIONAL: You can also specify a subject ID by doing ```?triv <subject id>```\n• OPTIONAL: You can also specify difficulty using one of the three keywords, i.e ```?triv hard```\n• OPTIONAL: Finally, you can combine both these in any order, i.e ```?triv 10 hard``` or ```?triv hard 10```\n• To respond: TriviaBot will automatically react with the possible options, click on the option you think is correct!\n\nSubject IDs:\n1) General Knowledge\n2) Entertainment: Books\n3) Entertainment: Film\n4) Entertainment: Music\n5) Entertainment: Musicals & Theatres\n6) Entertainment: Television\n7) Entertainment: Video Games\n8) Entertainment: Board Games\n9) Science & Nature\n10) Science: Computers\n11) Science: Mathematics\n12) Mythology\n13) Sports\n14) Geography\n15) History\n16) Politics\n17) Art\n18) Celebrities\n19) Animals\n20) Vehicles\n21) Entertainment: Comics\n22) Science: Gadgets\n23) Entertainment: Japanese Anime & Manga\n24) Entertainment: Cartoon & Animations\n\nDifficulties:\n• Easy\n• Medium\n• Hard""")
            embed.add_field(name='Optional choices', value='• To specify a subject, type `?triv <subject id>` in chat!\n• To specify a difficulty, type `?triv <difficulty>` in chat!\n\n*Note: These two optional statements can be combined in any order, e.g.*\n`?triv hard 10`\n*or*\n`?triv 10 hard`', inline=False)
            embed.add_field(name='Stats', value='To see your stats, type `?stats` in chat!\nYou can also mention a user like `?stats @<user>` to see their stats!\n\n*Note: Allowing a question to time out will count against your score!*\n\n', inline=False)
            subject_str = ''
            for x in range(len(subjects)):
                subject_str += str(x+1) + ') ' + list(subjects)[x] + '\n'
            embed.add_field(name='Subjects', value=subject_str)
            embed.add_field(name='Difficulties', value='• Easy\n• Medium\n• Hard')
            embed.set_footer(text='Create by Ethan Shealey | https://github.com/ethanshealey/TriviaBot\nQuestions from opentdb.com | https://opentdb.com')
            await msg.channel.send(embed=embed)

        elif len(content) <= 2 and (content[0] == '?stats' or content[0] == '?stat'):
            if len(content) == 2:
                user = msg.mentions[0]
            else:
                user = msg.author
            query = ("SELECT * FROM stats WHERE username=?")
            data = [i for i in cursorObj.execute(query, (str(user),))]
            if len(data) >= 1:
                data=data[0]
                embed = discord.Embed(title='Stats for ' + str(data[1]), color=0x1FB3FC)
                embed.add_field(name='Score', value='❓\'s answered: ' + str(data[2] + data[3]), inline=False)
                embed.add_field(name='Accuracy', value='100%' if data[3] == 0 else str(round((data[2]/(data[2]+data[3])) * 100,2)) + '%', inline=False)
            else:
                embed = discord.Embed(title=str(user) + ' has not played', description='No stats for player', color=0x1FB3FC)

            await msg.channel.send(embed=embed)

        elif len(content) >= 1 and content[0] == '?triv':
            # get data                    
            url = get_url(content, subject_codes)
            data = json.loads(urlopen(url).read().decode("utf-8"))

            #parse data
            data = data['results'][0]
            cat = html.unescape(data['category'])
            question = html.unescape(data['question'])
            diff = data['difficulty'][0].upper() + str(html.unescape(data['difficulty'][1::]))
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
            embed = discord.Embed(title="Welcome to Trivia!", color=0x46e065 if diff == 'Easy' else 0xf2f549 if diff == 'Medium' else 0xfc4b30)
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
            time = 0
            while not hasAnswered and time <= 30:
                
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

                await asyncio.sleep(1)
                time += 1

            user, username = await get_user(m)

            # respond
            if not hasAnswered and time >= 30:
                add_if_new_user(user)
                update_score(user, 0)
                embed = discord.Embed(title="⏰ Out of time!", description=f"Sorry! The correct answer was {correct_ans}", color=0xFC1F4E)
            elif possible_ans[ans] == correct_ans:
                add_if_new_user(user)
                update_score(user, 1)
                embed = discord.Embed(title="✅ Correct!", description=f"Good job {username}!", color=0x68FF38)
            else:
                add_if_new_user(user)
                update_score(user, 0)
                embed = discord.Embed(title="❌ Incorrect!", description=f"Sorry {username}! The correct answer was {correct_ans}", color=0xFC1F4E)       
            await msg.channel.send(embed=embed)
    
client.run(TOKEN)
con.close()