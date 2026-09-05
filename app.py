import os 
import threading
from flask import Flask
from bot import bot

app = Flask(__name__)

@app.route('/')
def home():
    return 'Бот workaet'

@app.route('/health')
def health():
    return 'OK'

def запустить_бота():
    print(f'Бот запускается!')
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f'Ошибка: {e}')

if __name__ == '__main__':
    поток = threading.Thread(target=запустить_бота)
    поток.daemon = True
    поток.start()
    порт = int(os.environ.get('PORT', 5000))
    app.run(host = '0.0.0.0', port = порт)
    