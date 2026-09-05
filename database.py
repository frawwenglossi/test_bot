import sqlite3

def создать_базу_админов():
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute("""
    CREATE TABLE IF NOT EXISTS admins(
        telegram_id INTEGER PRIMARY KEY NOT NULL,  
        admin_role TEXT DEFAULT 'no',
        дата_назначения TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE
        )
    """)

    курсор.execute("""
    CREATE TABLE IF NOT EXISTS obr(
        id INTEGER PRIMARY KEY AUTOINCREMENT,  --  новый первичный ключ
        telegram_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        answer_by TEXT,
        answer_by_admin_id INTEGER,
        дата_создания TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE,
        FOREIGN KEY (answer_by_admin_id) REFERENCES admins(telegram_id) ON DELETE SET NULL
        )
    """)

    курсор.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    second_name TEXT NOT NULL,
    fam TEXT NOT NULL,
    user_group INTEGER,
    дата_регистрации TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    print(f'База "users" = id, telegram_id*, first_name, second_name, fam, user_group, дата_регистрации СОЗДАНА')
    print(f'База "admins" = telegram_id*, admin_role, дата_назначения СОЗДАНА')
    print(f'База "obr" = id*, telegram_id, text, answer_by, anser_by_admin_id, дата_создания СОЗДАНА')
    соединение.commit()
    соединение.close()
    return

def добавить_пользователя(first_name, second_name, fam, telegram_id, user_group = None):
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute("""
    INSERT INTO users (telegram_id, first_name, second_name, fam, user_group)
    VALUES (?, ?, ?, ?, ?)""", (telegram_id, first_name, second_name, fam, user_group))
    соединение.commit()
    соединение.close()
    return

def удалить_пользователя(telegram_id):
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id, ))
    соединение.commit()
    соединение.close()
    return

def получить_всех_пользователей():
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute("SELECT * FROM users")
    результаты = курсор.fetchall()
    соединение.close()
    return результаты

def проверить_статус_админа(telegram_id):
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute('SELECT admin_role FROM admins WHERE telegram_id = ?', (telegram_id, ))
    результат = курсор.fetchone()
    if результат and результат[0].lower() == "yes":
        соединение.close()
        return True
    else:
        соединение.close()
        return False

def назначить_админа(telegram_id):
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute("SELECT * FROM admins WHERE telegram_id = ?", (telegram_id, ))
    результат = курсор.fetchone()
    if результат and результат[0] == "yes":  
        return False
    
    курсор.execute("""
    INSERT INTO admins (telegram_id, admin_role)
    VALUES (?, ?)""", (telegram_id, 'yes'))
    соединение.commit()
    соединение.close()
    id_последнего_добавленного_админа = курсор.lastrowid
    return id_последнего_добавленного_админа

def убрать_админа(telegram_id):
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute('DELETE FROM admins WHERE telegram_id = ?', (telegram_id, ))
    соединение.commit()
    соединение.close()

def показать_весь_список_админов():
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute("SELECT * FROM admins")
    результаты = курсор.fetchall()
    соединение.close()
    return результаты

def добавить_обращение(telegram_id, text):
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute("""
    INSERT INTO obr (telegram_id, text)
    VALUES (?, ?) """, (telegram_id, text))
    соединение.commit()
    соединение.close()

def посмотреть_все_обращения():
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute("""
    SELECT
        obr.id,
        obr.telegram_id,
        obr.text,
        answer_by,
        obr.дата_создания
    FROM obr
    """)
    результаты = курсор.fetchall()
    return результаты

def посмотреть_одно_обращение(id):
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute("""
    SELECT
        obr.id,
        users.fam || ' ' || users.first_name || ' ' || users.second_name,
        obr.text,
        obr.answer_by,
        obr.answer_by_admin_id,
        obr.дата_создания
    FROM obr
    LEFT JOIN users ON obr.telegram_id = users.telegram_id
    WHERE obr.
    id = ?
    """, (id, ))
    результат = курсор.fetchone()
    return результат

def ответить_на_обращение(number_obr, answer, answer_by_admin_id):
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute("""
    UPDATE obr SET answer_by = ?, answer_by_admin_id = ? WHERE id = ?""", (answer, answer_by_admin_id, number_obr))
    соединение.commit()
    соединение.close()  
    return

def посмотреть_ответы_все():
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute("SELECT answer_by FROM obr")
    результаты = курсор.fetchall()
    for результат in результаты:
        print(f'{результат}')
    соединение.commit()
    соединение.close() 

def данные_по_телеграм_id(telegram_id):
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute("""
    SELECT
        users.first_name,
        users.second_name,
        users.fam
    FROM users
    WHERE telegram_id = ?""", (telegram_id, ))
    результат = курсор.fetchone()
    соединение.close()
    return результат

#ДЛЯ РАЗРАБОТЧИКА!!!!!!
def УДАЛИТЬ_ВСЕ_ТАБЛИЦЫ():
    соединение = sqlite3.connect('BOT.db')
    курсор = соединение.cursor()
    курсор.execute('DROP TABLE IF EXISTS users')
    курсор.execute("DROP TABLE IF EXISTS obr")
    курсор.execute('DROP TABLE IF EXISTS admins')
    соединение.commit()
    соединение.close()