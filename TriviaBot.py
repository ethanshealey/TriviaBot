# Created by Ethan Shealey
# Last updated: 5/17/2021
# 
# TriviaBot! alllows you and your friends to play trivia in your chat!
#
# Run with `python3 TriviaBot.py`
#
# FEATURES:
#   - stats tracker:
#       • the built in stats tracker allows you and your friends
#         to see how well you do in trivia, keeping track of total 
#         questions answered and your overall score
#   - general trivia
#       • get a completely random question taken from one of the
#         26 categories and 3 difficulties which you then have
#         30 seconds to answer the question
#   - advanced trivia
#       • specify a specific category or a specific difficulty (or both)
#         and test your knowledge  
#
# FEATURES @TODO:
#   - `group` mode:
#       • group mode would allow any user to vote on an answer
#         then after the allotted time expires the bot reveals
#         the correct answer and the players who were correct
#   - `team` mode:
#       • team mode allows a player to set up two teams of 
#         n players who then compete to answer a set of questions
#         first, whichever team ends with the most points win the 
#         game

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

'''
async def get_user(m, msg)

parameters: m, msg

m - The message object the bot sent that is awaiting response
msg - The original message object sent by the user

This function loops through the reactions and gets the users who
are not the bot

returns a single user id and username
'''
async def get_user(m, msg):

    # init user array and username
    users, username = [], ''

    # Iterate through reactions on post
    for react in m.reactions:
        # Iterate through users in each reaction
        async for u in react.users():
            # Check if user is bot
            if u.id != 843268722658377758:
                # Append to user list
                users.append(u)

    # If a user is found
    if len(users) > 0:
        # Save the information of the first user to react
        username = users[0].name
        user = await client.fetch_user(users[0].id)
    # Else get author info
    else:
        username = msg.author.name
        user = msg.author
    
    # return user information
    return user, username

'''
def get_subjects_and_codes()

parameters: None

This function links the possible trivia
subjects and their respective codes for
the opentdb.com API

returns the subjects and subject codes
'''
def get_subjects_and_codes():
    subjects = ['Animals', 'Art', 'Celebrities', 'Entertainment', 'Entertainment: Board Games', 'Entertainment: Books', 'Entertainment: Cartoon & Animations', 'Entertainment: Comics', 'Entertainment: Film', 'Entertainment: Japanese Anime & Manga', 'Entertainment: Music', 'Entertainment: Musicals & Theatres', 'Entertainment: Television', 'Entertainment: Video Games', 'General Knowledge', 'Geography', 'History', 'Mythology', 'Politics', 'Science', 'Science & Nature', 'Science: Computers', 'Science: Gadgets', 'Science: Mathematics', 'Sports', 'Vehicles']
    entertainment_list = ['5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
    science_list = ['21', '22', '23', '24']
    subject_codes = {'1': 27, '2': 25, '3': 26, '5': 16, '6': 10, '7': 32, '8': 29, '9': 11, '10': 31, '11': 12, '12': 13, '13': 14, '14': 15, '15': 9, '16': 22, '17': 23, '18': 20, '19': 24, '21': 17, '22': 18, '23': 30, '24': 19, '25': 21, '26': 28}
    subject_codes['4'] = subject_codes[entertainment_list[random.randint(0, len(entertainment_list)-1)]]
    subject_codes['20'] = subject_codes[science_list[random.randint(0, len(science_list)-1)]]

    return subjects, subject_codes

'''
def get_url(content, subject_codes)

parameters: content, subject_codes

content - The command the user gave e.g `?triv 10 hard`
subject_codes - dictionary to convert user given code to API code

This function creates the needed URL to interact with the API

returns the completed URL
'''
def get_url(content, subject_codes):
    url = 'https://opentdb.com/api.php?amount=1'
    if len(content) == 2:
        if content[1].isdigit():
            if int(content[1]) < 1 or int(content[1]) > 26:
                return None
            else:
                url += '&category=' + str(subject_codes[content[1]])
        if content[1].lower() == 'easy' or content[1].lower() == 'medium' or content[1].lower() == 'hard':
            url += '&difficulty=' + content[1].lower()

    elif len(content) == 3:
        if content[1].isdigit():
            if int(content[1]) < 1 or int(content[1]) > 26:
                return None
            else:
                url += '&category=' + str(subject_codes[content[1]])
        elif content[2].isdigit():
            if int(content[2]) < 1 or int(content[2]) > 26:
                return None
            else:
                url += '&category=' + str(subject_codes[content[2]])

        if content[1].lower() == 'easy' or content[1].lower() == 'medium' or content[1].lower() == 'hard':
            url += '&difficulty=' + content[1].lower()
        elif content[2].lower() == 'easy' or content[2].lower() == 'medium' or content[2].lower() == 'hard':
            url += '&difficulty=' + content[2].lower()

    return url

'''
def add_if_new(user)

parameters: user

user - The user who answered the question

This function determines if the user who answered
is in the database, adds them if they do not exist
'''
def add_if_new_user(user):
    # select the user from the database
    query = ("SELECT * FROM stats WHERE username=?")
    data = [i for i in cursorObj.execute(query, (str(user),))]
    # if returns empty list, player does not exist
    if data == []:
        # insert new player into database
        query = ("INSERT INTO stats (username) values (?)")
        cursorObj.execute(query, (str(user),))
        con.commit()
        # log new user being added
        print('added user', user, 'to db')
    else:
        # log player requesting to play
        print('user', user, 'is requesting a question')

'''
def update_score(user, correct)

parameters: user, correct

user - The user who answered the question
correct - Boolean value showing if the user was correct

This function updates the users score in the database
'''
def update_score(user, correct):
    # check if user is new
    add_if_new_user(user)
    # if user was correct, update correct value
    if correct:
        query = ("UPDATE stats SET correct = correct + 1 WHERE username=?")
    # if user was incorrect, update incorrect value
    else:
        query = ("UPDATE stats SET incorrect = incorrect + 1 WHERE username=?")
    # execute and commit
    cursorObj.execute(query, (str(user),))
    con.commit()

'''
async def on_ready()

parameters: None

This function runs when the bot boots, soley used
to give the bot a `playing` status
'''
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='?triv help'))

'''
async def on_message(msg)

parameters: msg

msg - The message the user sends

This function handles all other possibilities:
    - ?help | ?triv help
    - ?stat | ?stats | ?stat <@ user> | ?stats <@ user>
    - ?triv | ?triv <subject id> | ?triv <difficulty> | ?triv <subject id> <difficulty>
'''
@client.event
async def on_message(msg):

    # dont let bot respond to itself
    if msg.author == client.user:
        return

    # save message from user 
    content = msg.content
    # if user is using TriviaBot! prefix
    if content.startswith('?'):

        # split the content by spaces
        content = content.split(' ')

        # get the subjects and subject codes
        subjects, subject_codes = get_subjects_and_codes()

        '''
        Error handling

        If user gives too many arguments send a message to inform them
        '''
        if len(content) > 3:
            embed = discord.Embed(title='Too many arguments!', description='Please type `?help` or `?triv help` in chat to find the proper syntax!')  
            await msg.channel.send(embed=embed)
            return 

        '''
        ?help | ?triv help 

        Send help prompt to user
        '''
        if (len(content) == 1 and content[0].lower() == '?help') or (len(content) == 2 and content[0].lower() == '?triv' and content[1].lower() == 'help'):
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
            embed.set_footer(text='Created by Ethan Shealey | https://github.com/ethanshealey/TriviaBot\nQuestions from opentdb.com | https://opentdb.com')
            await msg.channel.send(embed=embed)

        '''
        ?stats | ?stat | ?stats <@ user> | ?stat <@ user>

        Send stats report to player, optinally show stats of mentioned user
        '''
        if len(content) <= 2 and (content[0].lower() == '?stats' or content[0].lower() == '?stat'):
            if len(content) == 2:
                user = msg.mentions[0]
            else:
                user = msg.author
            query = ("SELECT * FROM stats WHERE username=?")
            data = [i for i in cursorObj.execute(query, (str(user),))]
            if len(data) >= 1:
                data=data[0]
                embed = discord.Embed(title='Stats for ' + str(data[1]), color=0x1FB3FC)
                # ❓\'s answered'
                embed.add_field(name='Questions answered', value=str(data[2] + data[3]), inline=False)
                embed.add_field(name='Score', value='100%' if data[3] == 0 else str(round((data[2]/(data[2]+data[3])) * 100,2)) + '%', inline=False)
            else:
                embed = discord.Embed(title=str(user) + ' has not played', description='No stats for this user', color=0x1FB3FC)

            await msg.channel.send(embed=embed)

        '''
        ?triv | ?triv <subject id> | ?triv <difficulty> | ?triv <subject id> <difficulty> | ?triv <difficulty> <subject id>

        Generate a random question and send to user, once user reacts to 
        question check if user is correct. If no response in 30 seconds
        time the question out and dock the authors points

        Optional arguments include <subject id> and <difficulty>
        '''
        if len(content) >= 1 and content[0].lower() == '?triv':

            # get data                    
            url = get_url(content, subject_codes)

            # if user gave invalid subject ID
            if not url:
                embed = discord.Embed(title='Invalid subject given', description='A list of subjects can be found by typing `?help` or `?triv help` in chat!')
                await msg.channel.send(embed=embed)
                return

            # get the data from the API
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
            
            # shuffle possible answers if not a T/F question
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

            # set up emojis
            if not type == 'boolean':
                emotes = {'🇦': possible_ans[0], '🇧': possible_ans[1], '🇨': possible_ans[2], '🇩': possible_ans[3]}
            else:
                emotes = {'🇹': possible_ans[0], '🇫':possible_ans[1]}

            # react to post with selected emojis
            for emote in emotes:
                await m.add_reaction(emote)

            # wait for a response
            hasAnswered, ans = False, None
            time = 0

            # wait for a user to respond, if no response in 30 seconds
            # time out the problem
            while not hasAnswered and time <= 30:
                
                # get the bots message
                m = await msg.channel.fetch_message(m.id)

                # Check to see if any reactions have a new reaction
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

                # if question is T/F
                else:
                    T = get(m.reactions, emoji=list(emotes)[0])
                    F = get(m.reactions, emoji=list(emotes)[1])

                    if T and T.count > 1:
                        hasAnswered, ans = True, 0
                    elif F and F.count > 1:
                        hasAnswered, ans = True, 1

                # sleep for 1 second before checking again
                await asyncio.sleep(1)
                time += 1

            # get the user who answered
            user, username = await get_user(m, msg)

            # respond to the user
            if not hasAnswered and time >= 30:
                update_score(user, 0)
                embed = discord.Embed(title="⏰ Out of time!", description=f"Sorry! The correct answer was {correct_ans}", color=0xFC1F4E)
            elif possible_ans[ans] == correct_ans:
                update_score(user, 1)
                embed = discord.Embed(title="✅ Correct!", description=f"Good job {username}!", color=0x68FF38)
            else:
                update_score(user, 0)
                embed = discord.Embed(title="❌ Incorrect!", description=f"Sorry {username}! The correct answer was {correct_ans}", color=0xFC1F4E)       
            await msg.channel.send(embed=embed)
    
client.run(TOKEN)
con.close()