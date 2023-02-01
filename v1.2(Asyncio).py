import requests
import datetime as dt
import re
import time
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types
import asyncio
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage



def Parser(loginz, password, user_id):
    thx = "Благодарю за использование бота, используя его, Вы соглашаетесь с тем, что введенные Вами данные будут " \
              "хранится на нашем сервере.\n "
    date = dt.datetime.now().strftime('—————————————————————\n\t\t\tUpdated today in %H:%M:%S, %d.%m.%Y')  ##Update time information
    message1 = thx + str(date)

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"
    HEADERS = {
            "User-Agent": user_agent
        }

    BASE_URL = 'https://edu.tatar.ru/logon'
    ANKETA_URL = 'https://edu.tatar.ru/user/anketa'
    SUBJECT_DATA = {
            'Решение задач по химии',
            'Астрономия',
            'Биология',
            'География',
            'Индивидуальный проект_',
            'Иностранный язык (английский)',
            'Информатика',
            'История',
            'Литература',
            'Математика',
            'Обществознание',
            'Основы безопасности жизнедеятельности',
            'Родная (татарская) литература',
            'Родной (татарский) язык',
            'Русский язык',
            'Физика',
            'Физическая культура',
            'Химия',
            'Изобразительное искусство',
            'Родной язык',
            'Родная (русская) литература',
            'Родная литература',
            'Литературное чтение'
        }
            
    session = requests.Session()  ##Authentification process
    session.headers.update({'Referer': BASE_URL})
    session.headers.update({'User-Agent': user_agent})
    _xsrf = session.cookies.get('_xsrf', domain=".tatar.ru")

    login_response = session.post(BASE_URL,
                                          {
                                              'main_login2': loginz,
                                              'main_password2': password
                                          })
        

    MAIN_URL = 'https://edu.tatar.ru/user/diary/day'  ##Trying to parse dayly-page
    RESPONSE = session.get(MAIN_URL, headers=HEADERS)
    soup = BeautifulSoup(RESPONSE.text, "lxml")
    try:
        name = session.get(ANKETA_URL, headers=HEADERS)     ##Getting name
        name_soup = BeautifulSoup(name.text, "lxml")
        name_item = name_soup.find("strong").text
        message1 = '\tЗдравствуйте, ' + name_item + '!\n\n' + message1
    except AttributeError:
        Bad_Message = '\tВведенные Вами данные неверны. Попробуйте еще раз.'
        return(Bad_Message)

    logs = (str(user_id) + ':' + name_item + ':' + loginz + ':' + password)
    logwriter(logs)

    item_list = ''
    items = soup.find_all("table", {"class": "main"})  ##Getting an information from page
    for item in items:
        itemf = item.text.strip()
        item_list = re.sub("[\n]", " ", itemf).split()
    item_list.pop(0)
    item_list.pop(0)
    item_list.pop(0)
    item_list.pop(0)
    item_list.pop(0)
    item_list.pop(0)

    i = 0
    while i < len(item_list):  ##Formating gotten informatinon (time)
        if '—'  in item_list[i]:
            if ':'  in item_list[i]:
                item_list[i] = '—————————————————————\n|\t\t\t' + item_list[i] + '\t\t\t|'
                item_list.insert(i, '\n')
                i += 1
        i = i + 1
    i = 0
    while i < len(item_list):  ##Formating gotten informatinon
        for el in SUBJECT_DATA:     ##Getting 4th-named subjects
            try:
                if item_list[i] + ' ' + item_list[i+1] + ' ' + item_list[i+2] + ' ' + item_list[i+3] == el:
                    item_list[i] = '\t\t\t' + item_list[i] + ' ' + item_list[i+1] + ' ' + item_list[i+2] + ' ' + item_list[i+3] + '\t —> \n|\tД/з: '
                    item_list.pop(i+1)
                    item_list.pop(i+1)
                    item_list.pop(i+1)
            except IndexError:
                pass
        for el in SUBJECT_DATA:     ##Getting triple-named subjects
            try:
                if item_list[i] + ' ' + item_list[i+1] + ' ' + item_list[i+2] == el:
                    item_list[i] = '\t\t\t' + item_list[i] + ' ' + item_list[i+1] + ' ' + item_list[i+2] + '\t —> \n|\tД/з: '
                    item_list.pop(i+1)
                    item_list.pop(i+1)
            except IndexError:
                pass
        for el in SUBJECT_DATA:      ##Getting double-named subjects
            try:
                if (item_list[i] + ' ' + item_list[i+1]) == el:
                    item_list[i] = '\t\t\t' + item_list[i] + ' ' + item_list[i+1] + '\t —> \n|\tД/з: '
                    item_list.pop(i+1)
            except IndexError:
                pass
                
        for el in SUBJECT_DATA:
            if item_list[i] == el:          ##(Subject)
                item_list[i] = '\t\t\t' + item_list[i] + '\t —> \n|\tД/з: '
                        ##(Marks)
        if ((item_list[i] == '5') | (item_list[i] == '4') | (item_list[i] == '3') | (item_list[i] == '2')):     
            try:
                if item_list[i + 1] == '\n':
                    a1 = '\n| Оценка: ' + str(item_list[i])
                    message1 = message1 + a1
                else:
                    a2 = ' ' + str(item_list[i])
                    message1 = message1 + a2
            except IndexError:
                a2 = ' ' + str(item_list[i])
                message1 = message1 + a2 + '<— Возможно, это Ваша оценка.'
        else:
            a3 = ' ' + str(item_list[i])
            message1 = message1 + a3
        i = i + 1
    return(message1)

def logwriter(logs):
    log_open = open('log.txt', 'r')
    log_read = log_open.read()
    log_open.close()
    if log_read.find(logs) != -1:
        pass
    else:
        log_open = open('log.txt', 'a+')
        log_open.write('\n' + logs)
        print(logs)

class logs(StatesGroup):
    login = State()
    password = State()

def tgbot():

    bot = Bot("5813832249:AAFT9dzOYgNkG9h_hdtk6KXk-FqfxE4l-us")
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    @dp.message_handler(commands=['start'])
    async def send_welcome(message:types.Message):
        chat_id = message.from_user.id
        log_open = open('log.txt', 'r')
        log_read = log_open.read()
        log_open.close()
        i = 2
        reading_logs = log_read.split('\n')
        if log_read.find(str(chat_id)) != -1:
            for el in reading_logs:
                el1 = str(el).split(':')
                login = el1[i]
                password1 = el1[i+1]
                await getting_info(password1, login, chat_id)
                i += 4
                
        else:
            await message.answer('Спасибо за использование бота! Пожалуйста, вводите правильные данные с первого раза, иначе Вы сможете воспользоваться ботом еще раз только после его перезапуска. Если бот не отвечает напишите /start')
            await asyncio.sleep(1)
            await bot.send_message(message.chat.id, "Введите логин")
            await logs.login.set()

    @dp.message_handler(state=logs.login)
    async def get_login(message:types.Message, state: FSMContext):
        login = message.text
        await state.update_data(login=login)
        print('логин', {login})
        await bot.send_message(message.chat.id, "Введите пароль")   
        await logs.password.set()

    @dp.message_handler(state=logs.password)        
    async def password(message:types.Message, state: FSMContext):
        password = message.text
        await state.update_data(password=password)
        data = await state.get_data(logs)
        login10 = data.get('login')
        password10 = data.get('password')
        chat_id = message.from_user.id

        print(login10, password10, chat_id)
        await getting_info(password10, login10, chat_id)



    async def getting_info(password, login, chat_id):
        print(login,password,chat_id)
        info_message = await bot.send_message(chat_id, Parser(login, password, chat_id))

        while True:
            await bot.pin_chat_message(chat_id, message_id=info_message.message_id)
            await asyncio.sleep(600)
            await bot.edit_message_text(Parser(login, password, chat_id), chat_id, message_id=info_message.message_id)

    executor.start_polling(dp, skip_updates=False)

if __name__ == "__main__":
    tgbot()
