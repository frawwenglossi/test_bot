import os
from dotenv import load_dotenv
import logging


logger = logging.getLogger(__name__)
load_dotenv()

АДМИН_ID = int(os.environ.get('ADMIN_ID', 0))
ТОКЕН = os.environ.get('TELEGRAM_TOKEN')

if not ТОКЕН:
    logger.critical('Токен не найден!')
    raise ValueError("Токен не найден!")
if not АДМИН_ID:
    logger.warning('ADMIN ID не найден!')

logger.info ('Конфигурация загружена успешна!')