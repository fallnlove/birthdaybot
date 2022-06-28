import asyncio
import sqlite3
import json
import datetime
from time import sleep
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)

API_TOKEN = '' #YOUR TOKEN HERE

bot = Bot(token = API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'start@chat_birthday_bot'])
async def start_message(message: types.Message):
    await message.answer('Привет ✌️\nТеперь ваш чат подключен к боту!\n')

@dp.message_handler(commands=['help', 'help@chat_birthday_bot'])
async def help_message(message: types.Message):
    await message.answer('Этот бот будет напоминать вам о Дне рождении ваших друзей в чате\n\nСписок доступных комманд\n/help@chat_birthday_bot - вывести это сообщение\n/add_birth дата - установить дату своего рождения в формате день.месяц\n/del_birth - удалить упоминание о своем ДР\n/imhere - добавить упоминание о своем ДР в этом чате')

@dp.message_handler(commands=['imhere', 'imhere@chat_birthday_bot'])
async def add_chat(message: types.Message):
	with open('usernames.json', "r") as f:
		file = json.load(f)
	if str(message.from_user.id) in file:
		if not(str(message.chat.id) in file[str(message.from_user.id)]["chats"]):
			file[str(message.from_user.id)]["chats"].append(str(message.chat.id))
		else:
			await message.answer('Похоже ты уже есть в списках этого чата')
			return
	else:
		await message.answer('Бот еще не знает дату твоего рождения :(')
		return
	with open('usernames.json', "w") as f:
		json.dump(file, f)

@dp.message_handler(commands=['add_birth', 'add_birth@chat_birthday_bot'])
async def add_birth(message: types.Message):
	msg = message.text.split(' ')[1].split('.')
	if not(msg[0].isdigit() and msg[1].isdigit() and int(msg[0]) < 32 and int(msg[1]) < 13):
		await message.answer('Ты что-то наврал, такой даты не может быть')
		return
	msg[0] = str(int(msg[0]))
	msg[1] = str(int(msg[1]))
	date = msg[0] + '.' + msg[1]
	d = datetime.date.today()
	date1 = str(d.day) + '.' + str(d.month)
	if date == date1:
	    await bot.send_message(message.chat.id, 'Поздравляем с Днем рождения @' + str(message.from_user.username) + '!🎉\n\nЖелаем ему(ей) всего самого наилучшего!🎉\n\nСердечки для именинника(цы) в студию!❤️')
	with open('birthdays.json', "r") as f:
		data = json.load(f)
	if not(date in data):
		await message.answer('Ты что-то наврал, такой даты не может быть')
		return
	with open('usernames.json', "r") as f:
		file = json.load(f)
	if not(str(message.from_user.id) in file):
		list = []
		list.append(str(message.chat.id))
		file.update({str(message.from_user.id) : {"name" : message.from_user.username, "chats" : list}})
	else:
	    data[file[str(message.from_user.id)]["date"]].remove(str(message.from_user.id))
	data[date].append(str(message.from_user.id))
	with open('birthdays.json', "w") as f:
		json.dump(data, f)
	file[str(message.from_user.id)].update({"date" : date})
	with open('usernames.json', "w") as f:
		json.dump(file, f)
	await message.reply('Успешно добавил тебя!')

@dp.message_handler(commands=['del_birth', 'del_birth@chat_birthday_bot'])
async def del_birth(message: types.Message):
	with open('usernames.json') as f:
		file_names = json.load(f)
	with open('birthdays.json') as f:
		file = json.load(f)
	if not(str(message.from_user.id) in file_names):
		await message.answer('Ты что-то наврал, тебя похоже и не было')
		return
	file[file_names[str(message.from_user.id)]["date"]].remove(str(message.from_user.id))
	del file_names[str(message.from_user.id)]
	with open('usernames.json', 'w') as f:
		json.dump(file_names, f)
	with open('birthdays.json', 'w') as f:
		json.dump(file, f)
	await message.reply('Удалил тебя, возвращайся еще :(')

async def sending():
	d = datetime.date.today()
	date = str(d.day) + '.' + str(d.month)
	with open('birthdays.json') as f:
		file = json.load(f)
	with open('usernames.json') as f:
		usernames = json.load(f)
	for user in file[date]:
		for chat in usernames[user]["chats"]:
			await bot.send_message(chat, 'Поздравляем с Днем рождения @' + usernames[user]["name"] + '!🎉\n\nЖелаем ему(ей) всего самого наилучшего!🎉\n\nСердечки для именинника(цы) в студию!❤️')
	if date == '1.3' and d.year % 4 != 0:
		date = '29.2'
		with open('birthdays.json') as f:
			file = json.load(f)
		with open('usernames.json') as f:
			usernames = json.load(f)
		for user in file[date]:
			for chat in usernames[user]["chats"]:
				await bot.send_message(chat, 'Поздравляем с Днем рождения @' + usernames[user]["name"] + '!🎉\n\nЖелаем ему(ей) всего самого наилучшего!🎉\n\nСердечки для именинника(цы) в студию!❤️')

if __name__ == '__main__':
	sched = AsyncIOScheduler()
	sched.add_job(sending, 'cron', hour='10')
	sched.start()
	executor.start_polling(dp, skip_updates=True)
