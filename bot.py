from config import ТОКЕН, АДМИН_ID
from datetime import datetime
import telebot
from telebot import types
import database as db
import logging

bot = telebot.TeleBot(ТОКЕН)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

db.создать_базу_админов()

состояния = {}
введенный_текст = {}
номер_и_обращение = {}

def главное_меню(chat_id, is_admin = False):
    клавиатура = types.ReplyKeyboardMarkup(resize_keyboard=True)
    клавиатура.row('✍️ ПОДАТЬ ОНЛАЙН ОБРАЩЕНИЕ')
    клавиатура.row('❓ О БОТЕ')

    if is_admin or chat_id == АДМИН_ID:
        клавиатура.row('⚙️ АДМИН-ПАНЕЛЬ')

    bot.send_message(chat_id, 'Выберите одно из действий в меню:', reply_markup= клавиатура)

@bot.message_handler(commands=['start'])
def команда_start(message):
    chat_id = message.chat.id
    имя = message.from_user.first_name or 'Пользователь'
    результаты = db.получить_всех_пользователей()
    telegram_id_users = []
    for результат in результаты:
        telegram_id_users.append(результат[1])
    print(telegram_id_users)    
    if chat_id not in telegram_id_users:
        bot.send_message(chat_id,
                     f"""
    {имя}, добро пожаловать в НАДЗОРНУЮ КОМИССИЮ ССПФ!
    Пройдите небольшую регистрацию для авторизации в боте-помощнике.
    Напишите своё ФИО и №группы.

    К примеру, 'Иванов Иван Иванович 2413'""")
        состояния[chat_id] = 'регистрация'
        logger.info(f'Пользователь с ID {chat_id} (первая регистрация) активировал бота!')
    else:
        bot.send_message(chat_id, f'{имя}, добро пожаловать в НАДЗОРНУЮ КОМИССИЮ ССПФ!')
        is_admin = db.проверить_статус_админа(chat_id)
        logger.info(f'Пользователь с ID {chat_id} активировал бота!')
        главное_меню(chat_id, is_admin)


@bot.message_handler(func = lambda message: message.text == '⚙️ АДМИН-ПАНЕЛЬ')
def команда_админ_панель(message):
    chat_id = message.chat.id
    клавиатура = types.ReplyKeyboardMarkup(resize_keyboard=True)
    клавиатура.row('✅ НАЗНАЧИТЬ АДМИНИСТРАТОРА')
    клавиатура.row('❌ УБРАТЬ АДМИНИСТРАТОРА')
    клавиатура.row('🔍 ОТВЕТИТЬ НА ОБРАЩЕНИЕ')
    клавиатура.row('ТЕХВОПРОС')
    клавиатура.row('🔙 НАЗАД')
    bot.send_message(chat_id, 'Вы успешно зашли в админ-панель!', reply_markup=клавиатура)

@bot.message_handler(func=lambda message: message.text == '❓ О БОТЕ')
def команда_о_боте(message):
    chat_id = message.chat.id
    клавиатура = types.ReplyKeyboardMarkup(resize_keyboard=True)
    клавиатура.row('🔙 НАЗАД')
    bot.send_message(chat_id,"""
    БОТ наздорной комисии Студенческого совета педиатрического факульта - инструмент связи со студентами педиатрического факультета.
Используя этого бота, вы можете:
• Подать электронное обращение.
• Задать вопрос декану/заместителю декана/студенческому совету напрямую.
• Получить ответ от деканата с персональным уведомлением. """, reply_markup=клавиатура)

@bot.message_handler(func=lambda message: message.text == '✍️ ПОДАТЬ ОНЛАЙН ОБРАЩЕНИЕ')
def команда_подать(message):
    chat_id = message.chat.id
    состояния[chat_id] = 'ожидание текста'
    клавиатура = types.ReplyKeyboardMarkup(resize_keyboard=True)
    клавиатура.row('🔙 НАЗАД')
    bot.send_message(chat_id, 'Отправьте краткое описание вашего обращения/вопроса:', reply_markup=клавиатура)

@bot.message_handler(func=lambda message: message.text == '🔙 НАЗАД')
def команда_назад(message):
    chat_id = message.chat.id
    is_admin = db.проверить_статус_админа(chat_id)
    состояния[chat_id] = 'НАЗАД'
    главное_меню(chat_id, is_admin)

@bot.message_handler(func=lambda message: message.text == '✅ НАЗНАЧИТЬ АДМИНИСТРАТОРА')
def команда_назначить_администратор(message):
    chat_id = message.chat.id
    if not chat_id == АДМИН_ID:
        bot.send_message(chat_id, "⛔ У тебя нет прав!")
        return

    bot.send_message(chat_id, f'Отправьте telegram_id\nНапример: #{АДМИН_ID}')

@bot.message_handler(func=lambda message: message.text == '❌ УБРАТЬ АДМИНИСТРАТОРА')
def команда_убрать_администратора(message):
    chat_id = message.chat.id
    клавиатура = types.ReplyKeyboardMarkup(resize_keyboard=True)
    результаты = db.показать_весь_список_админов()
    for index, результат in enumerate(результаты, 1):
        клавиатура.row(f'{index}. Telegram_id: {результат[0]}')
    клавиатура.row('🔙 НАЗАД')
    bot.send_message(chat_id, 'Выберите администратора:', reply_markup=клавиатура)

@bot.message_handler(func=lambda message: message.text == '🔍 ПОСМОТРЕТЬ ОБРАЩЕНИЯ')
def команда_посмотреть_обращения(message):
    chat_id = message.chat.id
    результаты = db.посмотреть_все_обращения()
    for результат in результаты:
        bot.send_message(chat_id,f"""
ОБРАЩЕНИЕ НОМЕР №{результат[0]}.

Telegram ID пользователя: {результат[1]}.
Cодержание обращения: {результат[2]}.

Ответ: {результат[3] if результат[3] else 'Нет ответа'}

Дата создания: {результат[4]}
""")

@bot.message_handler(func=lambda message: message.text == '🔍 ОТВЕТИТЬ НА ОБРАЩЕНИЕ')
def команда_ответить_на_обращение(message):
    chat_id = message.chat.id
    результаты = db.посмотреть_все_обращения()
    клавиатура = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for результат in результаты:
        клавиатура.row(f'{'✅' if результат[3] else '⌛'} ОБРАЩЕНИЕ №{результат[0]}')
    клавиатура.row('🔙 НАЗАД')
    bot.send_message(chat_id, 'Выберите обращение:', reply_markup=клавиатура)

@bot.message_handler(func=lambda message: message.text.startswith('⌛ ОБРАЩЕНИЕ №'))
def команда_продолжить_отвечать_на_обращение(message):
    chat_id = message.chat.id
    номер = message.text.replace('⌛ ОБРАЩЕНИЕ №', '')
    bot.send_message(chat_id, f'Вы выбрали ОБРАЩЕНИЕ №{номер}.')
    результат = db.посмотреть_одно_обращение(номер)
    bot.send_message(chat_id,f"""
ОБРАЩЕНИЕ НОМЕР №{результат[0]}.

Telegram ID пользователя: {результат[1]}.
Cодержание обращения: {результат[2]}.

Ответ: {результат[3] if результат[3] else 'Нет ответа'}.

Дата создания: {результат[4]}.
""")
    номер_и_обращение[chat_id] = номер
    bot.send_message(chat_id, f'Отправьте ваш ответ на ОБРАЩЕНИЕ №{номер_и_обращение[chat_id]}.')
    состояния[chat_id] = 'отвечает'

@bot.message_handler(func = lambda message: message.text.startswith('✅ ОБРАЩЕНИЕ №'))
def посмотреть_обращение(message):
    chat_id = message.chat.id
    номер = message.text.replace('✅ ОБРАЩЕНИЕ №', '')
    клавиатура = types.ReplyKeyboardMarkup(resize_keyboard=True)
    клавиатура.row('🔙 НАЗАД')
    обращение = db.посмотреть_одно_обращение(номер)
    bot.send_message(chat_id,f"""
ОБРАЩЕНИЕ НОМЕР №{обращение[0]}.

Telegram ID пользователя | ФИО: {обращение[1]}.
Cодержание обращения: {обращение[2]}.

Ответ: {обращение[3] if обращение[3] else 'Нет ответа'}\n({обращение[4]}).

Дата создания: {обращение[5]}.
""", reply_markup=клавиатура)

@bot.message_handler(func=lambda message: message.text.lower() == 'техвопрос')
def тренинг(message):
    chat_id = message.chat.id
    клавиатура = types.InlineKeyboardMarkup(row_width=2)
    кнопка1 = types.InlineKeyboardButton('Да', callback_data = 'yes')
    кнопка2 = types.InlineKeyboardButton('Нет', callback_data = 'net')
    клавиатура.add(кнопка1, кнопка2)
    bot.send_message(
    chat_id,
    "👋 Добро пожаловать! Выберите действие:",
    reply_markup=клавиатура
    )


@bot.message_handler(func = lambda message: True)
def обработать_текст(message):
    chat_id = message.chat.id
    if message.text.startswith('#'):
        telegram_id = int(message.text.replace('#', ''))
        try:
            if db.проверить_статус_админа(telegram_id) == True:
                bot.send_message(chat_id, f'Пользователь {telegram_id} уже является администратором!')
                return

            db.назначить_админа(telegram_id)
            bot.send_message(
            chat_id,
            f"✅ Пользователь {telegram_id} назначен администратором!")
            bot.send_message(telegram_id,"👑 Вас назначили администратором бота!")
        except ValueError:
            bot.send_message(chat_id, f'Неверный формат! Введите число (telegram_id).')
            return
    if 'Telegram_id' in message.text:
        текст = message.text.split()
        if not db.проверить_статус_админа(текст[2]):
            bot.send_message(chat_id, f'{текст[2]} не является администратором!')
            return
        db.убрать_админа(текст[2])
        bot.send_message(chat_id, f'{текст[2]} снят с должности администора')
        bot.send_message(текст[2], 'Вы сняты администоратором с должности.')
        is_admin = db.проверить_статус_админа(текст[2])
        главное_меню(текст[2], is_admin)    
    if chat_id in состояния and состояния[chat_id] == 'ожидание текста':
        введенный_текст[chat_id] = message.text
        текст = введенный_текст.get(chat_id)
        del состояния[chat_id]
        db.добавить_обращение(chat_id, текст)
        bot.send_message(
            chat_id,
            f"✅ Текст сохранён!\n\n"
            f"📝 Твой текст:\n"
            f"{текст}\n"
            f"Обращение сохранено в базе данных, ожидайте ответа.",
            parse_mode="Markdown"
        )
        
        for админ in db.показать_весь_список_админов():
            bot.send_message(админ[0], f'⚠️ Поступило новое обращение!')

        del введенный_текст[chat_id]
        is_admin = db.проверить_статус_админа(chat_id)
        главное_меню(chat_id, is_admin)
    if chat_id in состояния and состояния[chat_id] == 'отвечает':
        текст = message.text    
        db.ответить_на_обращение(номер_и_обращение[chat_id], текст, chat_id)
        bot.send_message(chat_id, f'Ответ на обращение №{номер_и_обращение[chat_id]} отправлено!')
        telegram_id = db.посмотреть_одно_обращение(номер_и_обращение[chat_id])[0]
        результат = db.данные_по_телеграм_id(chat_id)
        bot.send_message(telegram_id, f'Ваша обращение рассмотрено!\nОтвет: {текст}\nОтветил(-а): {результат[2]} {результат[0]} {результат[1]}')
        del состояния[chat_id]
        del номер_и_обращение[chat_id]
        is_admin = db.проверить_статус_админа(chat_id)
        главное_меню(chat_id, is_admin)
    if chat_id in состояния and состояния[chat_id] == 'регистрация':
        chat_id = message.chat.id
        текст = message.text.split()
        if len(текст) == 4:
            фамилия = текст[0]
            имя = текст[1]
            отчество = текст[2]
            группа = текст[3]
            db.добавить_пользователя(имя, отчество, фамилия, chat_id, группа)
            bot.send_message(chat_id, f'Вы успешно авторизовались в помощнике!')
            del состояния[chat_id]
            db.проверить_статус_админа(chat_id)
            главное_меню(chat_id)
        else:
            bot.send_message(chat_id, f'Вводите строго по форме!')

#========

def создать_клавиатуру():
    """
    Создаёт клавиатуру с кнопками разной ширины.
    """
    клавиатура = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # row() — кнопки в одной строке
    клавиатура.row("📚 Каталог", "🛒 Корзина")  # 2 кнопки
    
    # add() — добавляет кнопки, автоматически распределяя по строкам
    клавиатура.add("📞 Контакты", "❓ Помощь", "⚙️ Настройки")  # 3 кнопки
    
    # кнопка на всю ширину
    клавиатура.row("🏠 Главное меню")  # 1 кнопка на всю строку
    
    return клавиатура

def скрыть_клавиатуру(chat_id):
    """
    Убирает клавиатуру после завершения действия.
    """
    # ReplyKeyboardRemove — удаляет клавиатуру
    убрать = types.ReplyKeyboardRemove()
    
    bot.send_message(
        chat_id,
        "Введите текст вручную:",
        reply_markup=убрать
    )
#========



if __name__ == "__main__":
    print("🤖 Бот запущен!")
    logger.info('Бот запущен!')
    print("Нажми Ctrl+C для остановки.")
    print('=' * 10)
    print('АДМИНЫ')
    print('=' * 10)
    print(f'{db.показать_весь_список_админов()}')
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен.")

