import pandas as pd
import numpy as np
import streamlit as st
import time
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from numba import njit
import asyncio
#import gzip
import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
st.set_page_config(page_title= 'Testing Grounds :tada:', page_icon='snake', layout='wide', initial_sidebar_state='expanded')




#Данные для аккаунта +7 9273091197
#Получать данные для аккаунтов через БД/скрипт (?)
api_id = 24931692 
api_hash = '7acc18430237abb56186b10546ee2cd3'
client = TelegramClient('anon', api_id, api_hash, system_version='4.16.30-vxCUSTOM')
target_chat = '@eyeofgodrbot'

#Страны, доступные для выбора в боте
countries = ['Россия', 'Украина', 'Беларусь', 'Казахстан', 'Турция', 'Мексика', 'Германия', 'Аргентина', 'Грузия'
             'Армения', 'Африка', 'Франция', 'Мальта', 'Норвегия', 'Малайзия', 'Узбекистан', 'Таджикистан',
             'Нидерланды', 'ОАЭ', 'Румыния', 'Польша', 'Испания']

socnetworks = ['Вконтакте', 'Instagram', 'Telegram', 'Пароли']

key_words = ['ФИО', 'Город', 'Имя', 'Адрес', 'ИНН', 'Адрес', 'Номер', 'VIN', 'База данных', 'СНИЛС', 'Совпадения', 'Номер', 'ОГРН', 'Арендованный хостинг', 'Кадастровый номер']

decline_words = ['ограничил', 'не удалось', 'не найдено', 'не найдены']

#Пример данных для поиска, потом подгружать с БД/запроса (?)
keys_search = ['Антонов Вячеслав Олегович', 'Антонов Георгий Олегович', '+79173286889', '+79173649678'] # 'Сидоров Вячеслав Олегович', 
               #'Куприн Вячеслав Александрович']
#['Антонов Вячеслав Олегович'] 

#Ведем подсчет запросов к боту
action_count = 0



#Начинаем общение с ботом
async def starter():
    await client.send_message(target_chat, '/start')


#async def starter(starter_stop):
 #   global action_count
  #  await client.send_message(target_chat, '/start')
   # action_count += 1
    #if not starter_stop.is_set():
     #   threading.Timer(1, starter, [starter_stop]).start()
# starter_stop = threading.Event()
# starter(starter_stop)

#Получаем ответ на /start
@client.on(events.NewMessage(chats=target_chat, pattern=r'Добро пожаловать!'))
async def greet_handler(event):
    await event.reply(keys_search[action_count])  #subject to change


# if keys_search[action_count].isnumeric() and len(keys_search[action_count]) == 14:
#       await client.send_message(target_chat, '/inf' + keys_search[action_count])
#       await client.send_message(target_chat, '/snils' + keys_search[action_count])
#       await client.send_message(target_chat, )
#Получаем данные html ответа бота
@njit
@client.on(events.NewMessage(chats=target_chat))
async def doc_handler(event):
    global action_count
    if event.media:
        await event.download_media()#Можно задать конкретный путь при запуске на VM
    if any([substr in event.text for substr in key_words]):
        st.text(f"{event.text}")
        with open ('messages.txt', 'a', encoding='utf-8') as file:
            file.write(event.text)
        try:
            action_count += 1
            await client.send_message(target_chat, keys_search[action_count]) #subject to change
        except IndexError:
            pass

#Работаем с query-ответами бота, выбираем страну для посика, проверяем, удачный ли ответ и продолжаем опрашивать бота
@client.on(events.NewMessage(chats=target_chat, pattern=r'Выберите доступные действия:'))
async def query_handler(event):
    global action_count
    await event.message.click(countries.index('Россия')+1)


#Обработка сообщений о невозможности поиска, достижении предела запросов на день
@njit
@client.on(events.NewMessage(chats=target_chat))
async def decline_handler(event):
    global action_count
    async for message in client.iter_messages(entity=target_chat, limit=1):
        try:
            if any([substr in message.text for substr in decline_words]):
                #Позже отправлять в БД (?) соответствующее неудачному запросу сообщение
                action_count += 1
                await client.send_message(target_chat, keys_search[action_count]) #subject to change
            elif 'Вы слишком часто выполняете это действие' in message.text:
                await asyncio.sleep(1)
                await client.send_message(target_chat, keys_search[action_count]) #subject to change
        except IndexError:
            #Это означает, кончились ФИО для опроса бота
            pass
        if 'заблокирована' in message.text:
            #Это означает, что исчерпаны запросы для конкретного аккаунта telegram на сегодня
            return

#Вступаем в чат при соответствующем требовании
@client.on(events.NewMessage(chats=target_chat))
async def group_handler(event):
    if 'Обязательным условием' in event.text:
        link = event.buttons[0][0].url
        await client(JoinChannelRequest(link))
        await asyncio.sleep(0.001)
        await event.click(1)



#Получаем ответ на подпику на группу
@client.on(events.NewMessage(chats=target_chat))
async def greet_handler(event):
    if 'Вы можете прислать боту запросы в следующем формате:' in event.text:
        await event.reply(keys_search[action_count]) #subject to change


#Выбираем все соцсети при поиске по имени пользователя
@client.on(events.NewMessage(chats=target_chat))
async def socnet_handler(event):
    if 'Выберите направление поиска' in event.text:
        await event.message.click(socnetworks.index('Вконтакте'))
        await asyncio.sleep(0.1)
        await event.message.click(socnetworks.index('Instagram'))
        await asyncio.sleep(0.1)
        await event.message.click(socnetworks.index('Telegram'))    


#Выбираем дополнительную информацию в меню бота, в которых есть подобная возможность
@client.on(events.NewMessage(chats=target_chat))
async def group_handler(event):
    if 'VIN' in event.text:
        try:
            await event.click(4)
        except:
            pass
    elif 'Транзакций' in event.text or 'Арендованный хостинг' in event.text:
        try:
            await event.click(0)
        except:
            pass


#Запускаем в работу
if __name__ == "__main__":
    with client:
        #client.loop.run_until_complete(starter())
        client.loop.run_forever()
    st.sidebar.title('Параметры общения с EOG')


    if st.sidebar.button('Начать общение'):
        client.send_message(target_chat, '/start')


    st_name = st.sidebar.text_input("Введите имя для поиска"
    )

    keys_search.append(st_name)
#with open('styles.css') as f:
#    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
#progress_bar in for-loop for usage with loading elements, styles.css for sugarcoating some visuals
#wide modes, dark modes are implemented by default, pandas support, altair for some visualization
#make a scheduler app?

#Or make a menu to help me automate some of mine work process> Need to think about it
#Using DETA (deta.space) nosql database to keep info (maybe)