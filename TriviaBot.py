import asyncio, html, json, os, random, discord, requests
from urllib.request import urlopen
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

        subjects = ['Animals', 'Art', 'Celebrities', 'Entertainment', 'Entertainment: Board Games', 'Entertainment: Books', 'Entertainment: Cartoon & Animations', 'Entertainment: Comics', 'Entertainment: Film', 'Entertainment: Japanese Anime & Manga', 'Entertainment: Music', 'Entertainment: Musicals & Theatres', 'Entertainment: Television', 'Entertainment: Video Games', 'General Knowledge', 'Geography', 'History', 'Mythology', 'Politics', 'Science', 'Science & Nature', 'Science: Computers', 'Science: Gadgets', 'Science: Mathematics', 'Sports', 'Vehicles']
        entertainment_list = ['5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
        science_list = ['21', '22', '23', '24']
        subject_codes = {'1': 27, '2': 25, '3': 26, '5': 16, '6': 10, '7': 32, '8': 29, '9': 11, '10': 31, '11': 12, '12': 13, '13': 14, '14': 15, '15': 9, '16': 22, '17': 23, '18': 20, '19': 24, '21': 17, '22': 18, '23': 30, '24': 19, '25': 21, '26': 28}
        subject_codes['4'] = subject_codes[entertainment_list[random.randint(0, len(entertainment_list)-1)]]
        subject_codes['20'] = subject_codes[science_list[random.randint(0, len(science_list)-1)]]

        if len(content) == 1 and content[0] == '?help':
            # help prompt
            embed = discord.Embed(title='Help', color=0x1FB3FC)
            embed.add_field(name='Welcome to TriviaBot!', value='To play, type `?triv` in chat!', inline=False)#, value="""How to use:\n• To play: type ```?triv``` in chat\n• OPTIONAL: You can also specify a subject ID by doing ```?triv <subject id>```\n• OPTIONAL: You can also specify difficulty using one of the three keywords, i.e ```?triv hard```\n• OPTIONAL: Finally, you can combine both these in any order, i.e ```?triv 10 hard``` or ```?triv hard 10```\n• To respond: TriviaBot will automatically react with the possible options, click on the option you think is correct!\n\nSubject IDs:\n1) General Knowledge\n2) Entertainment: Books\n3) Entertainment: Film\n4) Entertainment: Music\n5) Entertainment: Musicals & Theatres\n6) Entertainment: Television\n7) Entertainment: Video Games\n8) Entertainment: Board Games\n9) Science & Nature\n10) Science: Computers\n11) Science: Mathematics\n12) Mythology\n13) Sports\n14) Geography\n15) History\n16) Politics\n17) Art\n18) Celebrities\n19) Animals\n20) Vehicles\n21) Entertainment: Comics\n22) Science: Gadgets\n23) Entertainment: Japanese Anime & Manga\n24) Entertainment: Cartoon & Animations\n\nDifficulties:\n• Easy\n• Medium\n• Hard""")
            embed.add_field(name='Optional choices', value='• To specify a subject, type `?triv <subject id>` in chat!\n• To specify a difficulty, type `?triv <difficulty>` in chat!\n\n*Note: These two optional statements can be combined in any order, e.g.*\n`?triv hard 10`\n*or*\n`?triv 10 hard`', inline=False)
        
            subject_str = ''
            for x in range(len(subjects)):
                subject_str += str(x+1) + ') ' + list(subjects)[x] + '\n'
            embed.add_field(name='Subjects', value=subject_str)
            embed.add_field(name='Difficulties', value='• Easy\n• Medium\n• Hard')
            embed.set_footer(text='Create by Ethan Shealey | https://github.com/ethanshealey/TriviaBot')
            await msg.channel.send(embed=embed)

        elif len(content) >= 1 and content[0] == '?triv':
            # get data                    
            url = 'https://opentdb.com/api.php?amount=1' #+ (('&category=' + str(int(content[1])+8)) if len(content) > 1 else '')
            
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
            while not hasAnswered and time <= 25:
                
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

            user = set()

            for react in m.reactions:
                async for u in react.users():
                    user.add(u.mention)

            user = list(user)[1]

            print(user)

            # respond
            if not hasAnswered and time >= 25:
                embed = discord.Embed(title="⏰ Out of time!", description=f"Sorry! The correct answer was {correct_ans}", color=0xFC1F4E)
            elif possible_ans[ans] == correct_ans:
                embed = discord.Embed(title="✅ Correct!", description="Good job!", color=0x68FF38)
            else:
                embed = discord.Embed(title="❌ Incorrect!", description=f"Sorry! The correct answer was {correct_ans}", color=0xFC1F4E)       
            await msg.channel.send(embed=embed)
    
client.run(TOKEN)
