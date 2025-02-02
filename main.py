import telebot
import time
import os
from dotenv import load_dotenv

from database import *
from rooms import *



load_dotenv()
bot = telebot.TeleBot(os.getenv('API_KEY'))
rooms = []




def roll(chat_id):
	value = bot.send_dice(chat_id, "🎰").dice.value
	MAX = 64
	value = (value - 1) / MAX
	probabilities = {30: 0.01, 15: 0.02, 5: 0.05, 2: 0.1, 1: 0.2}
	cumulative_prob = 0
	for result_value, prob in probabilities.items():
		cumulative_prob += prob
		if value <= cumulative_prob:
			return result_value
	return 0


@bot.message_handler(commands=['create'])
def create_room(message):
	args = message.text.split()
	print(len(rooms))
	if len(args) != 2:
		bot.send_message(message.chat.id, "Ошибка!")
	else:
		room = find_room_by_player(message.from_user.id,rooms)
		if (room is not None):
			bot.send_message(message.chat.id, "Вы уже состоите в другой комнате!")
		else:
			room_id = args[1]
			room = find_room_by_id(room_id, rooms)
			if (room is not None):
				bot.send_message(message.chat.id, "Такая комната уже есть!")
			else:
				room = Room(room_id)
				room.players.append(Player(message.chat.id))
				rooms.append(room)
				bot.send_message(message.chat.id, "Вы успешно создали комнату. Ожидаем соперника...")
				#while (len(room.players)<2):
				#    time.sleep(0.2)
				#bot.send_message(message.chat.id, "Соперник подключился. Игра началась!")

				


@bot.message_handler(commands=['join'])
def join_room(message):
	args = message.text.split()
	if len(args) != 2:
		bot.send_message(message.chat.id, "Ошибка!")
	else:
		room = find_room_by_player(message.from_user.id, rooms)
		if (room is not None):
			bot.send_message(message.chat.id, "Вы уже состоите в другой комнате!")
		else:
			room_id = args[1]
			room = find_room_by_id(room_id, rooms)
			print(room)
			if (room is None):
				bot.send_message(message.chat.id, "Такой комнаты нет!")
			else:
				room.players.append(Player(message.chat.id))
				room.started = True
				bot.send_message(message.chat.id,
						 "Вы присоедились к комнате. Игра началась!")



@bot.message_handler(commands=['throw'])
def throw_command(message):
	args = message.text.split()
	if len(args) != 2:
		bot.send_message(message.chat.id, "Ошибка!")
	else:
		room = find_room_by_player(message.from_user.id, rooms)
		if (room is None or not room.started):
			bot.send_message(message.chat.id,
					 "Вы не в комнате или игра еще не началась!")
		else:
			data = get_data(message.from_user.id)
			if (data is not None):
				points = data[0]
				try:
					num = int(args[1])
					if (num < 0):
						bot.send_message(
						    message.chat.id,
						    "Вы не можете поставить отрицательное количество монет!")
					elif (points >= num):
						user_index = 0
						if (room.players[0].id == message.from_user.id):
							user_index = 0
						else:
							user_index = 1
						room.players[user_index].score = bot.send_dice(
						    message.chat.id, "🎲").dice.value
						room.players[user_index].bet = num
						bot.send_message(
						    message.chat.id,
						    f"Вы поставили {num} монет. Ожидаем второго игрока!")
						time.sleep(2)
						while (room.players[0].score == 0 or room.players[1].score == 0):
							time.sleep(0.1)

						if (room.players[user_index].score
						    > room.players[(user_index + 1) % 2].score):
							diff = min(room.players[(user_index + 1) % 2].bet,
								   room.players[user_index].bet * 2)
							points += diff
							bot.send_message(
							    message.chat.id,
							    f"Ваш противник выкинул {room.players[(user_index+1)%2].score}. Вы выиграли {diff} монет!"
							)
						elif (room.players[user_index].score
						      < room.players[(user_index + 1) % 2].score):
							diff = min(room.players[(user_index + 1) % 2].bet * 2,
								   room.players[user_index].bet)
							points -= diff
							bot.send_message(
							    message.chat.id,
							    f"Ваш противник выкинул {room.players[(user_index+1)%2].score}. Вы Проиграли {diff} монет!"
							)
						else:
							bot.send_message(
							    message.chat.id,
							    "Ваш противник выкинул столько же сколько и вы. Ничего не произошло"
							)
						update_points(message.from_user.id, points)
						bot.send_message(message.chat.id,
								 f"Теперь у вас {str(points)} монет")
						time.sleep(3)
						room.players[0].score = 0
						room.players[0].bet = 0
						room.players[1].score = 0
						room.players[1].bet = 0
					else:
						bot.send_message(
						    message.chat.id,
						    "Ошибка! У вас нет столько денег! Введите /money для пополнения"
						)
				except ValueError:
					bot.send_message(message.chat.id, "Ошибка!")


@bot.message_handler(commands=['leave'])
def leave_room(message):
	room = find_room_by_player(message.from_user.id, rooms)
	if (room is None):
		bot.send_message(message.chat.id, "Вы не в комнате!")
	else:
		room.players.clear()
		room.id=0
		del room
		bot.send_message(message.chat.id,
				 "Вы вышли из комнаты! Комната будет удалена")


@bot.message_handler(commands=['roll'])
def roll_command(message):
	args = message.text.split()
	if len(args) != 2:
		bot.send_message(message.chat.id, "Ошибка!")
	else:
		data = get_data(message.from_user.id)
		if (data is not None):
			points = data[0]
			try:
				num = int(args[1])
				if (num < 0):
					bot.send_message(
					    message.chat.id,
					    "Вы не можете поставить отрицательное количество монет!")
				elif (points >= num):
					points -= num
					rolled = roll(message.chat.id)
					time.sleep(0.5)
					points += rolled * num
					if (rolled > 0):
						bot.send_message(
						    message.chat.id,
						    f"Вы выиграли {str((rolled-1)*num)} монет. Теперь у вас {str(points)} монет"
						)
					else:
						bot.send_message(
						    message.chat.id,
						    f"Вы проиграли. У вас осталось {str(points)} монет")
					update_points(message.from_user.id, points)
				else:
					bot.send_message(
					    message.chat.id,
					    "Ошибка! У вас нет столько денег! Введите /money для пополнения")
			except ValueError:
				bot.send_message(message.chat.id, "Ошибка!")


@bot.message_handler(commands=['money'])
def add_money(message):
	cooldown = 5 * 60
	data = get_data(message.from_user.id)
	if (data is not None):
		points, time = data
		current_time = message.date
		if (current_time - time >= cooldown):
			points += 100
			bot.send_message(
			    message.chat.id,
			    f"Вы пополнили 100 монет! Теперь у вас {str(points)} монет")
			update_time(message.from_user.id, current_time)
			update_points(message.from_user.id, points)
		else:
			bot.send_message(
			    message.chat.id,
			    f"Вы сможете пополниться только через {str(cooldown-(current_time-time))} секунд"
			)


@bot.message_handler(commands=['check'])
def check_money(message):
	data = get_data(message.from_user.id)
	if (data is not None):
		points = data[0]
		bot.send_message(message.chat.id, f"У вас {points} монет")


def get_username_by_id(user_id):
	try:
		chat = bot.get_chat(user_id)
		return chat.username
	except telebot.apihelper.ApiTelegramException as e:
		print(f"Error getting chat info: {e}")
		return None


@bot.message_handler(commands=['top'])
def show_top(message):
	user_data = get_data(message.from_user.id)
	all_users = get_alldata()
	if (user_data is not None and all_users is not None):
		all_users = sorted(all_users, key=lambda x: x[1], reverse=True)
		out_message = ''
		top = 0
		for user in all_users[:3]:
			out_message += f"{'🥇🥈🥉'[top]} :  @{get_username_by_id(user[0])} - {user[1]} монет" + '\n'
			top += 1

		out_message += ".....\n"
		user_top = all_users.index(
		    (message.from_user.id, user_data[0], user_data[1]))
		out_message += f"Ваше место в топе: {user_top+1}"
		bot.send_message(message.chat.id, out_message)


bot.polling()
