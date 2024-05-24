import datetime
import random
import subprocess
import sqlite3

from phrases import *
from dotenv import dotenv_values

config = dotenv_values(".env")

def get_from_config(query) -> str:
    """Get variable from .env config"""
    try:
        result = config[query]
    except:
        result = "not found"
    return result


def def_words(message, user_name, cursor, user_id, duel=False, aim=None):
    ulang = lang(user_id, cursor)
    if duel:
        search = cursor.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
        name11 = search.fetchone()[0]
        search = cursor.execute('SELECT tea_count FROM users WHERE user_id = ?', (user_id,))
        tc1 = search.fetchone()[0]

        search = cursor.execute("SELECT name FROM users WHERE user_id = ?", (aim.id,))
        name22 = search.fetchone()[0]
        search = cursor.execute('SELECT tea_count FROM users WHERE user_id = ?', (aim.id,))
        tc2 = search.fetchone()[0]
        if tc2 is None:
            return ["нельзя сбивать того кто непользуется ботом", [-128]]

        name1, name2 = name11, name22
        chance = random.random()
        tc = random.randint(1, 10)
        if tc1 < 25:
            chance = 0.6
        elif tc2 < 25:
            chance = 0.1
        trtext = "всего сбито"
        if chance > 0.5:
            am = random.choice(duels_plus).format(name1, name2)
            if tc1 < 0:
                tc1 = 0
            if tc2 < 0:
                tc2 = 0
            am += f'\n\n {name1} {trtext} {int(tc1) + int(tc)} (+{tc})'
            am += f'\n {name2} {trtext} {int(tc2) - int(tc)} (-{tc})'

            return [am, [int(tc1) + int(tc), int(tc2) - int(tc)]]
        else:
            if tc1 < 0:
                tc1 = 0
            if tc2 < 0:
                tc2 = 0
            am = random.choice(duels_minus).format(name1, name2)
            am += f'\n\n {name1} {trtext} {int(tc1) - int(tc)} (-{tc})'
            am += f'\n {name2} {trtext} {int(tc2) + int(tc)} (+{tc})'

            return [am, [int(tc1) - int(tc), int(tc2) + int(tc)]]

    result = cursor.execute("SELECT tea_count FROM users WHERE user_id = ?", (user_id,))
    existing_cups = result.fetchone()
    if existing_cups:
        tea_count = existing_cups[0]
    else:
        tea_count = 0
    chances = [1, 2, -1, -2, 3, 4, 5, 0, random.randint(30, 89), random.randint(-53, -19)]
    weights = [0.5, 0.5, 0.5, 0.4, 0.6, 0.4, 0.4, 0.1, 0.01, 0.01]
    change = random.choices(chances, weights)[0]
    es = change
    tea_count += change

    kek = {
        1: odin,
        0: null,
        -1: minus_odin,
        -2: minus_dva,
        2: dva,
        3: tri,
        4: chetire,
        5: pyat,
        -15: antijackpot,
        100: jackpot
    }
    if change < -2:
        es = -15  # шкибиди доп доп ес ес
    if change >= 30:
        es = 100
    try:
        am = random.choice(kek[es]).format(user_name)
    except KeyError:
        am = f"{user_name} взломал бота и накрутил себе черных"
    if tea_count < 0:
        tea_count = 0

    if change >= 0:
        am += f'\n\nвсего сбито {tea_count} (+{abs(change)} шт)'
    else:
        am += f'\n\nвсего сбито {tea_count} (-{abs(change)} шт)'

    return am, tea_count


def login(message):
    with open('log.txt', mode='a', encoding="utf-8") as file:
        file.write(f'\n{message} on {datetime.datetime.now()}\n')


def find(string):
    regex = ["/", ".", "@"]
    return any([x in string for x in regex])


def lang(user_id, cursor):
    cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    user_lang = cursor.fetchone()
    return user_lang


def give_nih(cursor, message, user_id, target, aim=None):
    if aim is None:
        return [f"Напишите команду ответом на чье-то сообщение", 0, 0]
    if user_id == aim.id:
        return ["Самому себе не передаем", 0, 0]
    if target > 10:
        return [f"Передавать можно до 10 негров в день!", 0, 0]
    if target <= 0:
        return ["Так не делаем, а иначе будет добавлено 24 часовое кд и минус 50 за такие запросы", 0, 0]
    search = cursor.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
    name11 = search.fetchone()[0]
    search = cursor.execute('SELECT tea_count FROM users WHERE user_id = ?', (user_id,))
    tc1 = search.fetchone()[0]

    search = cursor.execute("SELECT name FROM users WHERE user_id = ?", (aim.id,))
    name22 = search.fetchone()[0]
    search = cursor.execute('SELECT tea_count FROM users WHERE user_id = ?', (aim.id,))
    tc2 = search.fetchone()[0]

    name1, name2 = name11, name22
    
    if tc1 < target:
        return ["нельзя отдать больше негров чем у тебя есть", 0, 0]
    text = f"{name1} отдал своих негров {name2} в количестве {target}"
    text += f"\n\n{name1} {tc1 - target}(-{target})"
    text += f"\n{name2} {tc2 + target}(+{target})"
    return [text, int(tc1 - target), int(tc2 + target)]


def evaluate(primer):
    try:
        return float(eval(primer))
    except (SyntaxError, ZeroDivisionError):
        return ""
    except TypeError:
        return float(eval(primer.replace('(', '*(')))
    except Exception as e:
        print(e)
        return ""
