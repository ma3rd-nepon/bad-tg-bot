import sqlite3
import random
import subprocess
import random
import time
import datetime
import asyncio
import re

import logging

from pyrogram import *
from pyrogram.types import *
from pyrogram.errors import MessageTooLong, MessageEmpty
from utils import *
from math import sqrt

logging.basicConfig(filename="log.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

likes = dict()
inline_calc_text = dict()

game_bot = get_from_config("game_bot")
bot_id = get_from_config("bot_id")

api_id = get_from_config("api_id")
app = Client(name=get_from_config("name"),
             api_id=api_id,
             api_hash=get_from_config("api_hash"),
             bot_token=bot_id
             )

conn = sqlite3.connect('nigs.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    tea_count INTEGER DEFAULT 0,
    lang TEXT,
    name TEXT
)
""")

last_masturbation_time = {}
last_giving_time = {}
admins = [5942050664, 1242755674]
bot_ids = [6801563080, 6891506611]
bans = []
note = None

with open('log.txt', 'w', encoding="utf-8") as file:
    file.write(f'bot started on {datetime.datetime.now()}\n')


def filter_word(query):
    async def filtor(self, client, message):
        if message.text:
            target = (message.text.split(" ", maxsplit=1)[0]).lower()
            return target == self.query if type(self.query) == str else target in self.query
        return False

    return filters.create(filtor, query=query)


def calc_btn(uid, toc="callback_") -> InlineKeyboardMarkup:
    """Calculator buttons, toc - type of callback"""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("(", callback_data=f"{toc}calc;{uid};("),
                InlineKeyboardButton(")", callback_data=f"{toc}calc;{uid};)"),
                InlineKeyboardButton("CE", callback_data=f"{toc}calc;{uid};DEL"),
                InlineKeyboardButton("C", callback_data=f"{toc}calc;{uid};C"),
            ],
            [
                InlineKeyboardButton("1/x", callback_data=f"{toc}calc;{uid};**-1"),
                InlineKeyboardButton("^2", callback_data=f"{toc}calc;{uid};**2"),
                InlineKeyboardButton("√", callback_data=f"{toc}calc;{uid};sqrt"),
                InlineKeyboardButton("÷", callback_data=f"{toc}calc;{uid};/"),
            ],
            [
                InlineKeyboardButton("7", callback_data=f"{toc}calc;{uid};7"),
                InlineKeyboardButton("8", callback_data=f"{toc}calc;{uid};8"),
                InlineKeyboardButton("9", callback_data=f"{toc}calc;{uid};9"),
                InlineKeyboardButton("×", callback_data=f"{toc}calc;{uid};*"),
            ],
            [
                InlineKeyboardButton("4", callback_data=f"{toc}calc;{uid};4"),
                InlineKeyboardButton("5", callback_data=f"{toc}calc;{uid};5"),
                InlineKeyboardButton("6", callback_data=f"{toc}calc;{uid};6"),
                InlineKeyboardButton("-", callback_data=f"{toc}calc;{uid};-"),
            ],
            [
                InlineKeyboardButton("1", callback_data=f"{toc}calc;{uid};1"),
                InlineKeyboardButton("2", callback_data=f"{toc}calc;{uid};2"),
                InlineKeyboardButton("3", callback_data=f"{toc}calc;{uid};3"),
                InlineKeyboardButton("+", callback_data=f"{toc}calc;{uid};+"),
            ],
            [
                InlineKeyboardButton("%", callback_data=f"{toc}calc;{uid};*0.01"),
                InlineKeyboardButton("0", callback_data=f"{toc}calc;{uid};0"),
                InlineKeyboardButton(".", callback_data=f"{toc}calc;{uid};."),
                InlineKeyboardButton("=", callback_data=f"{toc}calc;{uid};="),
            ],
        ]
    )


async def edit_inline_query_likes_buttons(callback) -> None:
    global likes
    like = 0
    dislike = 0
    for i in likes[callback.inline_message_id]:
        if likes[callback.inline_message_id][i] == "like":
            like += 1
        if likes[callback.inline_message_id][i] == "dislike":
            dislike += 1
    await app.edit_inline_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(f"👍 {like}", callback_data='like'),
         InlineKeyboardButton(f"👎 {dislike}", callback_data='dislike')]
    ]))

#@bot.message_handler(func=lambda message: message.text.lower().split(' ')[0] in ['сбить', 'збить', 'збити', 'збиць'])
@app.on_message(filter_word(["сбить", "збити", "збить", "сбитб", "сбиьь", "сбитт", "сбмтт", "сбмть", "сбииь"]))
async def count_tea_cups(_, message):
    if message.chat.id in bans:
        return
    try:
        user_id = message.from_user.id

        cursor.execute("SELECT tea_count FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result is None:
            namee = str(message.from_user.first_name).encode().decode('utf-8', 'ignore')
            cursor.execute("INSERT OR REPLACE INTO users (user_id, name) VALUES (?, ?)",
                           (user_id, namee))
            conn.commit()
            cursor.execute("SELECT tea_count FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

        cursor.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
        name = cursor.fetchone()
        if name is None:
            name = message.from_user.first_name
            
        if message.reply_to_message is not None:
            aim = message.reply_to_message.from_user
            user = message.from_user
            if aim.id == user.id:
                await message.reply(f'{name[0]} еблан раз пытается сбить себя')
                last_masturbation_time[user_id] = [datetime.datetime.now(), 900]
                return

            elif aim.id in bot_ids:
                await message.reply("меня нельзя сбивать э\nща получиш")
                last_masturbation_time[user_id] = [datetime.datetime.now(), 3600]
                return

            else:
                pass

        if last_masturbation_time.get(user_id) is not None:
            time_since_last_masturbation = (datetime.datetime.now() - last_masturbation_time[user_id][0]).total_seconds()
            if time_since_last_masturbation < last_masturbation_time[user_id][1]:
                time_to_wait = datetime.timedelta(seconds=last_masturbation_time[user_id][1] - time_since_last_masturbation)
                minutes = int(time_to_wait.total_seconds() // 60)
                seconds = int(time_to_wait.total_seconds() % 60)
                if len(str(seconds)) == 1:
                    seconds_n = f'0{seconds}'
                    seconds = seconds_n
                if minutes > 60:
                    answer = f"{minutes // 60}:{minutes % 60}:{seconds}"
                else:
                    answer = f"{minutes}:{seconds}"
                await message.reply(f"{name[0]}, ты уже сбивал негров, приходи через {answer}")
                return

        if message.reply_to_message is not None:
            aim = message.reply_to_message.from_user
            user = message.from_user
            arr = def_words(message, name[0], cursor, user_id, True, aim)
            if len(arr[1]) == 2:
                cursor.execute("UPDATE users SET tea_count = ? WHERE user_id = ?", (arr[1][0], user.id))
                conn.commit()
                conn.commit()
                cursor.execute("UPDATE users SET tea_count = ? WHERE user_id = ?", (arr[1][1], aim.id))
                conn.commit()
                conn.commit()
            await message.reply(arr[0])
            last_masturbation_time[user_id] = [datetime.datetime.now(), 900]
            return

        am = def_words(message=message, user_name=name[0], cursor=cursor, user_id=user_id, duel=False, aim=None)
        count = am[1]
        await message.reply(am[0])
        last_masturbation_time[user_id] = [datetime.datetime.now(), 900]
        cursor.execute("UPDATE users SET tea_count = ? WHERE user_id = ?", (count, user_id))
        conn.commit()
        conn.commit()
        return
    except Exception as e:
        login(f"in сбить: {e}")


#@bot.message_handler(func=lambda message: message.text.lower() == "сброс статы")
@app.on_message(filter_word("сброс статы"))
async def remove_stats(_, message):
    if message.chat.id in bans:
        return
    try:
        user_id = message.from_user.id
        cursor.execute("UPDATE users SET tea_count = ? WHERE user_id = ?", (0, user_id))
        cursor.execute("UPDATE users SET name = ? WHERE user_id = ?", (message.from_user.first_name, user_id))
        login(f'игрок {message.from_user.id}|{message.from_user.username} сбросил стату в чате {message.chat.id}|{message.chat.title}')
        await message.reply("Поздравляю {}, вы успешно возродили всех сбитых вами негренков".format(name))
        conn.commit()
        conn.commit()
    except Exception as e:
        login(f"in remove_stats: {e}")


#@bot.message_handler(func=lambda message: message.text.lower().split()[0] in ['топ'])
@app.on_message(filter_word("топ"))
async def top_users(_, message):
    user_id = message.from_user.id
    cursor.execute("SELECT name FROM users WHERE user_id = ?", (message.from_user.id,))
    name = cursor.fetchone()[0]
    if message.chat.id in bans:
        return
    try:
        cursor.execute("SELECT user_id, name, tea_count FROM users ORDER BY tea_count DESC LIMIT 15")
        top_users = cursor.fetchall()
        response = f'{name}, '
        response += "топ пользователей бота:\n"
        count = 0
        for i, (user_id, name, tea_count) in enumerate(top_users):
            response += f"{i + 1}. {name} - {tea_count} негров\n"
            count += tea_count
        if note is not None:
            response += f'\n{note}'
        response += f'\n\nвсего негров сбито - {count}'
        await message.reply(response)
    except Exception as e:
        login(f'in top_users: {e}')


#@bot.message_handler(commands=['setnote'])
@app.on_message(filters.command("setnote", "/"))
async def send_log(_, message):
    global note
    if message.from_user.id in admins:
        text = str(message.text.split(' ', maxsplit=1)[1])
        if text.lower() == 'none':
            note = None
            return
        note = text
        return


#@bot.message_handler(func=lambda message: message.text.lower().startswith('имя'))
@app.on_message(filter_word("имя"))
async def handle_change_name(_, message):
    try:
        user_id = message.from_user.id
        ulang = lang(user_id, cursor)
        cursor.execute("SELECT tea_count FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        answer = message.text.split(' ', maxsplit=1)
        if result is None:
            cursor.execute("INSERT INTO users (user_id, name) VALUES (?, ?)",
                           (user_id, message.from_user.first_name))
            conn.commit()
            cursor.execute("SELECT tea_count FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

        if len(answer) == 1:
            await message.reply("Введите новый ник после команды")
            return
        new_name = answer[1].encode().decode('utf-8', 'ignore')
        if new_name:
            if len(new_name) > 32:
                await message.reply("Слишком длинное имя")
                return
            if find(new_name):
                await message.reply(' ["/", ".", "@"] {}'.format('запрещены'))
                login(f"попытка ссылки в ник от {message.from_user.id}")
                return
            
        user_id = message.from_user.id
        cursor.execute("UPDATE users SET name = ? WHERE user_id = ?", (new_name, user_id))
        conn.commit()
        await message.reply(f"{new_name} ну аче норм")
        login(f'{user_id}|{message.from_user.username} сменил ник на {new_name} в чате {message.chat.id}|{message.chat.title}')
    except Exception as e:
        login(f'in handle_change_name: {e}')


# @bot.message_handler(func=lambda message: message.text.lower().startswith('язык'))
# async def handle_change_lang(message):
#     try:
#         user_id = message.from_user.id
#         cursor.execute("SELECT tea_count FROM users WHERE user_id = ?", (user_id,))
#         result = cursor.fetchone()
#         answer = message.text.split(' ', maxsplit=1)
#         if result is None:
#             cursor.execute("INSERT OR REPLACE INTO users (user_id, name) VALUES (?, ?)",
#                            (user_id, message.from_user.first_name))
#             conn.commit()
#
#         if len(answer) == 1:
#             await bot.send_message(message.chat.id, text="Введите язык после команды")
#             return
#         new_lang = answer[1]
#         if len(new_lang) > 3:
#             await bot.send_message(message.chat.id,
#                                    'Некорректный ввод языка, вот пример:\nen ru pl uk\nЕсли вы незнаете как написать нужный вам язык то напишите /langs')
#             return
#         user_id = message.from_user.id
#         cursor.execute("UPDATE users SET lang = ? WHERE user_id = ?", (new_lang, user_id))
#         await bot.send_message(message.chat.id, text='язык изменен на {}'.format(new_lang))
#         conn.commit()
#         utils.login(
#             f'{user_id}|{message.from_user.username} сменил язык на {new_lang} в чате {message.chat.id}|{message.chat.title}')
#         return
#     except Exception as e:
#         utils.login(f'in handle_change_lang: {e}')
#         return


#@bot.message_handler(func=lambda message: message.text.lower().split()[0] == "топчата")
@app.on_message(filter_word("топчата"))
async def chatt(_, message):
    if message.chat.id == message.from_user.id:
        return await message.reply("Данный топ работает только в чатах!")

    start_time = time.time()
    cursor.execute("SELECT name FROM users WHERE user_id = ?", (message.from_user.id,))
    name = cursor.fetchone()[0]
    
    chat_users = [] 
    async for m in app.get_chat_members(chat_id=message.chat.id): 
        chat_users.append(str(m.user.id))
        
    try:
        string = f'{name}, '
        string += "топ пользователей бота в этом чате:\n"
        cursor.execute(f"SELECT user_id, name, tea_count FROM users WHERE user_id IN ({', '.join(chat_users)})")
        top_users = sorted(cursor.fetchall(), key=lambda x: x[2])[::-1]
        count = 0
        kek = 1
        for i, (user_id, name, tea_count) in enumerate(top_users):
            string += f"{kek}. {name} - {tea_count} негров\n"
            count += tea_count
            kek += 1
            if kek == 16:
                break
        
        if note is not None:
            string += f'\n\n{note}'
        string += f'\n\nвсего в этом чате негров сбито {count}'
        end_time = time.time()
        string += f"\n{round(int(end_time - start_time), 2)} sec"
        text = string
    except Exception as e:
        text = f"error: {str(e)}"
    
    await message.reply(text)


#@bot.message_handler(commands=['help'])
@app.on_message(filters.command("help", "/"))
async def help_with_commands(_, message):
    text = '''
мои команды:
имя (имя) - сменить имя в боте
сбить - сбить негри
топ - топ игроков в боте
топчата - топ игроков этого чата (в чатах)
выдать (колво) - выдать кому то негриков (адм)
фриз - заморозить кому то негров (адм)

/start - старт бота
/help - вывести этот список
/cd - изменить кд игрока (адм)
    '''
    await message.reply(text)
    return


@app.on_message(filters.command("start", "/"))
async def help_with_commands(_, message):
    cursor.execute("SELECT name, tea_count FROM users WHERE user_id = ?", (message.from_user.id,))
    answer = cursor.fetchone()
    if answer is None:
        cursor.execute("INSERT INTO users (user_id, name) VALUES (?, ?)", (message.from_user.id, message.from_user.first_name))
        return await message.reply(f"Здарова {message.from_user.first_name}, на твоем счету 0 негров. Пиши сбить чтобы начать")
    return await message.reply(f"шо надо {answer[0]}\nколво негров: {answer[1]}")


#@bot.message_handler(func=lambda message: message.text.lower().startswith('выдать'))
@app.on_message(filter_word("выдать"))
async def give_nig(_, message):
    if message.chat.id in bans or not message.text.startswith("выдать"):
        return
    try:
        if message.from_user.id not in admins:
            await message.reply("у вас нет прав")
            login(f'чебурек {message.from_user.id}|{message.from_user.username} хотел выдать негров в чате {message.chat.id}|{message.chat.title}')
            return
        aim = message.reply_to_message.from_user
        if aim.id in bot_ids:
            return await message.reply("смотри кому выдаеш ало")
        result = cursor.execute("SELECT tea_count, name FROM users WHERE user_id = ?", (aim.id,))
        existing_cups = result.fetchone()
        login(f"выдача негров игроку {aim.username} в чате {message.chat.id}|{message.chat.title}")
        if existing_cups:
            tea_count = existing_cups[0]
        else:
            tea_count = 0
        dat = int(message.text.split(' ', maxsplit=1)[1])
        tea_count += dat
        cursor.execute("UPDATE users SET tea_count = ? WHERE user_id = ?", (tea_count, aim.id))
        await message.reply('Игроку {} прилетело {} черних'.format(existing_cups[1], dat))
        conn.commit()
        conn.commit()
    except Exception as e:
        login(f'in give_nig: {e}')
        
#@bot.message_handler(func=lambda message: message.text.lower().startswith("казино"))
async def cazk(message):
    if message.chat.id in bans:
        return
    stavka = int(message.text.split(" ")[1])
    coff = round(random.random(), 2)
    await app.send_message(chat_id=message.chat.id, text=f"{message.from_user.username} {coff} {stavka}")


#@bot.message_handler(func=lambda message: message.text.lower().startswith("отдать"))
@app.on_message(filter_word("отдать"))
async def otdat_blacks(_, message):
    if not message.text.startswith("отдать"):
        return
    user_id = message.from_user.id
    if last_giving_time.get(user_id) is not None:
        time_since_last_masturbation = (datetime.datetime.now() - last_giving_time[user_id][0]).total_seconds()
        if time_since_last_masturbation < last_giving_time[user_id][1]:
            time_to_wait = datetime.timedelta(seconds=last_giving_time[user_id][1] - time_since_last_masturbation)
            minutes = int(time_to_wait.total_seconds() // 60)
            seconds = int(time_to_wait.total_seconds() % 60)
            if len(str(seconds)) == 1:
                seconds_n = f'0{seconds}'
                seconds = seconds_n
            if minutes > 60:
                answer = f"{minutes // 60}:{minutes % 60}:{seconds}"
            else:
                answer = f"{minutes}:{seconds}"
            await message.reply(f"ты уже отдавал негров, приходи через {answer}")
            return 
    if len(message.text.split(" ")) < 2:
        await message.reply("Укажите сколько вы хотите передать")
        return
    try:
        a = int(message.text.split(" ")[1])
    except Exception as e:
        return
    if message.reply_to_message.from_user.id in bot_ids:
        return await message.reply("зач мне твои негри")
    result = give_nih(cursor=cursor, message=message, user_id=message.from_user.id, aim=message.reply_to_message.from_user, target=int(message.text.split(" ")[1]))
    if result[1] == 0 and result[2] == 0:
        await message.reply(result[0])
        return
    cursor.execute("UPDATE users SET tea_count = ? WHERE user_id = ?", (int(result[1]), message.from_user.id))
    conn.commit()
    conn.commit()
    cursor.execute("UPDATE users SET tea_count = ? WHERE user_id = ?", (int(result[2]), message.reply_to_message.from_user.id))
    conn.commit()
    conn.commit()
    await message.reply(result[0])
    last_giving_time[message.from_user.id] = [datetime.datetime.now(), 43200]



# @bot.message_handler(commands=['test'])
# async def test_function(message):
#     await bot.send_message(message.chat.id, f'[test](tg://resolve?domain={message.from_user.username})')

#@bot.message_handler(commands=['cooldown'])


@app.on_message(filters.command("cd", "/"))
async def cooldown_control(_, message):
    if message.reply_to_message is None:
        return
    if message.from_user.id not in admins:
        return await message.reply("у вас нет прав")
    user_id = message.reply_to_message.from_user.id
    if user_id in bot_ids:
        return await message.reply("ты кому кд крутиш чепух")
    search = cursor.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
    name = search.fetchone()[0]
    time = int(message.text.split(" ")[1])
    func = message.text.lower().split(" ")[2]
    if time == 0:
        if func == "сбить":
            last_masturbation_time[user_id] = None
        if func == "отдать":
            last_giving_time[user_id] = None
        await message.reply("user {0} removed cooldown for {1}".format(name, func))
        return
    else:
        if func == "сбить":
            last_masturbation_time[user_id] = [datetime.datetime.now(), time]
        if func == "отдать":
            last_giving_time[user_id] = [datetime.datetime.now(), time]
        await message.reply("user {0} added cooldown for {1}".format(name, func))
        return
    return


@app.on_message(filter_word("фриз"))
async def freeze_nigs(_, message):
    if message.from_user.id not in admins:
        return await message.reply("у вас нет прав")
    if message.reply_to_message is None:
        return
    
    return await message.reply("потом, щас лень")


@app.on_callback_query()
async def catch_callbacks(_, callback) -> None:
    if callback.data == "dislike":
        if likes.get(callback.inline_message_id) is None:
            likes[callback.inline_message_id] = dict()
        if 'dislike' == likes[callback.inline_message_id].get(callback.from_user.id):
            likes[callback.inline_message_id][callback.from_user.id] = "nichego"
            return
        likes[callback.inline_message_id][callback.from_user.id] = 'dislike'

        await edit_inline_query_likes_buttons(callback)

    elif callback.data == "like":
        if likes.get(callback.inline_message_id) is None:
            likes[callback.inline_message_id] = dict()

        if 'like' == likes[callback.inline_message_id].get(callback.from_user.id):
            likes[callback.inline_message_id][callback.from_user.id] = "nichego"
            return

        likes[callback.inline_message_id][callback.from_user.id] = 'like'

        await edit_inline_query_likes_buttons(callback)

    

    elif "calc" in callback.data:
        _, user_id, button = callback.data.split(";")

        if callback.from_user.id != int(user_id):
            return await callback.answer("Не тваи кнопки", show_alert=True, cache_time=5)

        try:
            if inline_calc_text.get(callback.inline_message_id) is None:
                inline_calc_text[callback.inline_message_id] = ""

            text = callback.message.text.split("\n")[0].strip().split("=")[0].strip() if callback.message \
                else inline_calc_text.get(callback.inline_message_id).split("\n")[0].strip().split("=")[0].strip()
            text = '' if f"Калькулятор" in text else text
            target = text + callback.data
            result = ""
            stay = False

            if button == "=":
                result = evaluate(text)
                text = ""

            elif button == "DEL":
                text = text[:-1]

            elif button == "C":
                text = ""

            elif button == "sqrt":
                result = sqrt(evaluate(text))
                stay = True

            elif button == "**2":
                text = f"{text}**2"
                result = evaluate(text)

            elif button == "**-1":
                text = f"{text}**-1"
                result = evaluate(text)

            else:
                tochki = re.findall(r"(\d*\.\.|\d*\.\d+\.)", target)
                operators = re.findall(r"([/\+-]{2,})", target)
                if not tochki and not operators:
                    if re.findall(r"(\.\d+|\d+\.\d+|\d+)", target):
                        text += button
                        result = evaluate(text)

            text = f"{result}" if stay else f"{text:<50}"
            if result:
                if text:
                    text += f"\n{result:>50}"
                else:
                    text = result
            text += f"\n\nКалькулятор {callback.from_user.first_name}"

            edit_params = {
                "text": text,
                "parse_mode": pyrogram.enums.ParseMode.DISABLED
            }

            if "inline_calc" in callback.data:
                edit_msg = app.edit_inline_text
                edit_params["inline_message_id"] = callback.inline_message_id
                markup = calc_btn(user_id, "inline_")
            else:
                edit_msg = callback.edit_message_text
                markup = calc_btn(user_id)
            edit_params["reply_markup"] = markup
            aim = text.split("\n")[0].strip().split("=")[0].strip()

            inline_calc_text[callback.inline_message_id] = aim if aim != '' else text.split("\n")[1].strip()
            await edit_msg(**edit_params)

        except Exception as error:
            print(error)


@app.on_inline_query()
async def answering(_, inline) -> None:
    try:
        await inline.answer(
            results=[
                InlineQueryResultArticle(
                    title="Like or dislike",
                    description="send to chat",
                    input_message_content=InputTextMessageContent(inline.query),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("👍", callback_data='like'),
                         InlineKeyboardButton("👎", callback_data='dislike')]])
                ),
                InlineQueryResultArticle(
                    title="Калькулятор",
                    description="на кнопках",
                    input_message_content=InputTextMessageContent(f"Калькулятор {inline.from_user.first_name}"),
                    reply_markup=calc_btn(inline.from_user.id, "inline_")
                )
            ],
            cache_time=1
        )
    except Exception as e:
        if "[400 MESSAGE_EMPTY]" in str(e):
            return
        print(str(e))


@app.on_message(filters.command("calculator", "/"))  # калькулятор
async def calculate_handler(_, message):
    await message.reply(
        text=f"Калькулятор {message.from_user.first_name}",
        reply_markup=calc_btn(message.from_user.id))

print("bot vkl")
app.run()