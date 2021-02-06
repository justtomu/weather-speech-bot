import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import config
import os

bot = telebot.TeleBot(config.token)  # поместите token в файл config.py

part1 = 'https://weather.com/ru-RU/weather/today/l/'
part2 = '?par=apple_TWC&locale=ru_RU&units=m'
result_filepath = 'speech.mp3'


def syntez(text):
    res = requests.get(f'https://tts.voicetech.yandex.net/tts?tl=ru&text={text}')
    output = open(result_filepath, 'wb')
    output.write(res.content)
    output.close()


def get_weather(loc):
    result = ''
    link = part1 + loc + part2
    res = requests.get(link)
    soup = BeautifulSoup(res.text, 'html.parser')
    geo = soup.find_all(class_='CurrentConditions--location--1Ayv3')[0].get_text()
    result += geo + ' '
    tim = soup.find_all(class_='CurrentConditions--timestamp--1SWy5')[0].get_text()
    result += tim + '. '
    tem = soup.find_all(class_='CurrentConditions--tempValue--3KcTQ')[0].get_text()
    result += 'Сейчас на улице ' + tem + ', '
    feel = soup.find_all(class_='TodayDetailsCard--feelsLikeTempValue--2aogo')[0].get_text()
    result += 'ощущается как ' + feel + '. '
    obl = soup.find_all(class_='CurrentConditions--phraseValue--2xXSr')[0].get_text()
    result += obl + '; '
    snow = soup.find_all(class_='CurrentConditions--precipValue--RBVJT')[0].get_text()
    result += snow + '. '
    result.replace(',', ';')
    return result


@bot.message_handler(commands=['start'])
def ss(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(types.KeyboardButton('Сюда погоду'))
    bot.send_message(message.chat.id, 'Отправьте свою геолокацию чтобы узнать погоду.\n'
                                      'Чтобы узнать погоду у меня нажмите "Сюда погоду"', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def mm(message):
    if message.text == 'Сюда погоду':
        std(message)


@bot.message_handler(content_types=['location'])
def get_location(message):
    if message.location is not None:
        keyboard = types.ReplyKeyboardMarkup()
        keyboard.add(types.KeyboardButton('Сюда погоду'))
        tmp = str(message.location.latitude)[:5] + ','
        tmp += str(message.location.longitude)[:5]
        syntez(get_weather(tmp))
        bot.send_voice(message.chat.id, voice=open(result_filepath, 'rb'), caption='Вот ваша погода',
                       reply_markup=keyboard)
        os.system('rm ' + result_filepath)


def std(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(types.KeyboardButton('Сюда погоду'))
    syntez(get_weather('59.93,30.35'))
    bot.send_voice(message.chat.id, voice=open(result_filepath, 'rb'), caption='Вот ваша погода', reply_markup=keyboard)
    os.system('rm ' + result_filepath)


while True:
    try:
        bot.polling(none_stop=True)
    except:
        pass
