from aiogram import Bot, Dispatcher, executor
from config import botToken
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(botToken, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)

if __name__ == '__main__':
    from handlers import dp, send_to_admin, send_picture

    # register handlers
    dp.register_message_handler(send_picture, lambda msg: msg, text='q')

    executor.start_polling(dp, on_startup=send_to_admin)
