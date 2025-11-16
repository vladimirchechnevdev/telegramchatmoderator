import sqlite3
import telebot

nums = {0: 'first', 1: 'second', 2: 'third'}
bad_words = ('fuck')
warnings = ("got a warning for using profanity.",
            "was muted for an hour for using profanity.", "was permanently banned.")

token = ''
bot = telebot.TeleBot(token)


def response_get(response, message):
    connection = sqlite3.connect('UsersDatabase.sqlite')
    cursor = connection.cursor()

    if response == 0:
        bot.send_message(chat_id=message.chat.id,
                         text=message.from_user.first_name + ' ' + warnings[0])
        cursor.execute(f'DELETE FROM [{message.chat.id}] WHERE {nums[response]} = ?',
                       [message.from_user.first_name, ])
        cursor.execute(
            f'INSERT INTO [{message.chat.id}] ({nums[response + 1]}) VALUES (?)',
            [message.from_user.first_name])
        connection.commit()
        connection.close()

        return None

    elif response == 1:
        bot.send_message(chat_id=message.chat.id,
                         text=message.from_user.first_name + ' ' + warnings[1])
        bot.restrict_chat_member(chat_id=message.chat.id, user_id=message.from_user.id,
                                 until_date=3600, can_send_messages=False)
        cursor.execute(f'DELETE FROM [{message.chat.id}] WHERE {nums[response]} = ?',
                       [message.from_user.first_name, ])
        cursor.execute(
            f'INSERT INTO [{message.chat.id}] ({nums[response + 1]}) VALUES (?)',
            [message.from_user.first_name])
        connection.commit()
        connection.close()

        return None

    elif response == 2:
        bot.send_message(chat_id=message.chat.id,
                         text=message.from_user.first_name + ' ' + warnings[2])
        bot.ban_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
        connection.close()

        return None

    else:
        bot.send_message(chat_id=message.chat.id,
                         text=message.from_user.first_name + ' ' + warnings[0])
        cursor.execute(f'INSERT INTO [{message.chat.id}] (first) VALUES (?)',
                       [message.from_user.first_name])
        connection.commit()
        connection.close()

        return None


#checks user
def check_user(message):
    username = message.from_user.first_name

    connection = sqlite3.connect('UsersDatabase.sqlite')
    cursor = connection.cursor()
    cursor.execute(f'SELECT * FROM [{message.chat.id}]')

    everything = cursor.fetchall()
    connection.close()
    flag = False

    if type(everything) == list:
        for i in range(len(everything)):
            for j in range(0, 3):
                if username == everything[i][j]:
                    flag = True
                    return j
                else:
                    continue

    if not flag:
        return None

    if everything != list:
        return None


#cheks if group is in database
def check_table(message):
    connection = sqlite3.connect('UsersDatabase.sqlite')
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    response = cursor.fetchall()
    flag = False

    for i in range(len(response)):
        if str(message.chat.id) == str(response[i][0]):
            flag = True
            break
        else:
            continue

    if not flag:
        cursor.execute(
            f"CREATE TABLE [{message.chat.id}] (first  TEXT, second TEXT, third  TEXT, options TEXT, name TEXT);")
        cursor.execute(f"INSERT INTO [{message.chat.id}] (options, name) VALUES (?, ?)", ["False", "Бот"])
        connection.commit()
        connection.close()

        return 'False'

    else:
        cursor.execute(f"SELECT options FROM [{message.chat.id}]")

        return cursor.fetchall()[0][0]

#advertisement
def advertisement(message):
    connection = sqlite3.connect('UsersDatabase.sqlite')
    cursor = connection.cursor()
    response_database = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()

    for i in range(len(response_database)):
        try:
            bot.send_message(chat_id=response_database[i][0], text=message.text)

        except telebot.apihelper.ApiTelegramException as err:
            response = str(err)[91:]

            if 'chat not found' in response:
                continue

    connection.close()

    return None


@bot.message_handler(commands=['start'])
def start_message(message):
    group_status = bot.get_chat(chat_id=message.chat.id).type
    connection = sqlite3.connect('UsersDatabase.sqlite')
    cursor = connection.cursor()

    if group_status == 'group' or group_status == 'supergroup':
        bot.send_message(chat_id=message.chat.id,
                         text='This bot was created to moderate groups. \n\n/start shows this message; \n/ban turns on / off '
                              'punishments for using profanity; \n/name "text" will set the name for me here so you can call me.')
        id = str(message.chat.id)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        response = cursor.fetchall()
        flag = False

        for i in range(len(response)):
            if id == str(response[i][0]):
                flag = True
                break
            else:
                continue

        if not flag:
            cursor.execute(
                f"CREATE TABLE [{message.chat.id}] (first  TEXT, second TEXT, third  TEXT, options TEXT, name TEXT);")
            cursor.execute(f"INSERT INTO [{message.chat.id}] (options, name) VALUES (?, ?)", ["False", "Бот"])
            connection.commit()
            connection.close()

            return None
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Hi! I was created only for moderation of group chats. If you want to see my potential '
                              'you should add me to your group and give me administrator rights. '
                              'If you did that, write /start in the group and I will send you instructions for use.')
        bot.send_sticker(chat_id=message.chat.id,
                         sticker='CAACAgIAAxkBAAJOvWYSrvx7emh-acTzaw88Ufdj4gYrAAKqFQAC_QcYS-3YFx7pAAEqfDQE')
        connection.close()

        return None


@bot.message_handler(commands=['ban'])
def on_off_restricts(message):
    status = bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id).status
    id = message.chat.id
    check_table(message)

    connection = sqlite3.connect('UsersDatabase.sqlite')
    cursor = connection.cursor()

    if status == 'creator' or status == 'administrator':
        cursor.execute(f"SELECT options FROM [{id}]")
        ban = cursor.fetchall()

        if ban[0][0] == 'False':
            cursor.execute(f"UPDATE [{id}] SET options = ? WHERE options = ?", ['True', 'False'])
            bot.send_message(chat_id=id, text='Punishments for using profanity are on now✅')
            connection.commit()
            connection.close()

            return None

        elif ban[0][0] == 'True':
            cursor.execute(f"UPDATE [{id}] SET options = ? WHERE options = ?", ['False', 'True'])
            bot.send_message(chat_id=id, text='Punishments for using profanity are off now❌')
            connection.commit()
            connection.close()

            return None
    else:
        bot.send_message(chat_id=message.chat.id, text='You do not have enough authority.')
        bot.send_sticker(chat_id=message.chat.id,
                         sticker='CAACAgIAAxkBAAJOwGYSsTnGiVnIE99iRvH8VMn42cboAAKJGAACTHkQSzneMpLK0M3VNAQ')
        connection.close()

        return None


@bot.message_handler(content_types=['text'])
def text(message):
    status = bot.get_chat_member(message.chat.id, message.from_user.id).status
    group_status = bot.get_chat(chat_id=message.chat.id).type

    advertisement_group_id = 'place id of your group for advertisement as an integer here'

    connection = sqlite3.connect('UsersDatabase.sqlite')
    cursor = connection.cursor()

    id = message.chat.id
    cursor.execute(f"SELECT options FROM [{id}]")
    ban = cursor.fetchall()

    connection.commit()
    connection.close()

    #if the chat type is a group
    if group_status == 'group' or group_status == 'supergroup':
        
        #if the chat is for advertisement it replies the message from it to each group where the bot is
        if message.chat.id == advertisement_group_id:
            advertisement(message=message)

        else:
            if ban[0][0] == 'False':
                pass

            else:
                check_table(message=message)
                message_list = message.text.split()

                for i in range(len(message_list)):
                    if message_list[i] in bad_words:
                        if status == 'administrator' or status == 'creator':
                            bot.reply_to(message=message, text='Easy, buddy.')

                        else:
                            response = check_user(message=message)

                            if response is not None:
                                response_get(response=response, message=message)

                                return None

                            else:
                                response_get(response=0, message=message)

                    else:
                        continue

    else:
        bot.send_message(chat_id=message.chat.id,
                        text='I was created only for moderation of group chats. If you want to see my potential '
                             'you should add me to your group and give me administrator rights. '
                             'If you did that, write /start in the group and I will send you instructions for use.')

        bot.send_sticker(chat_id=message.chat.id,
                        sticker='CAACAgIAAxkBAAJOvWYSrvx7emh-acTzaw88Ufdj4gYrAAKqFQAC_QcYS-3YFx7pAAEqfDQE')


bot.infinity_polling()
