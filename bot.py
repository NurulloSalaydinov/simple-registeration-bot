import logging
import random
import os
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from config import BOT_TOKEN, BOT_GROUP

logging.basicConfig(level=logging.INFO)

API_TOKEN = BOT_TOKEN

def generate_image_name():
    letters = 'qwertyuiopasdfghjklmnpqwertyui'
    name_len = 20
    text = ''
    for i in range(0, name_len+1):
        text += random.choice(letters)
    return text

bot = Bot(token=API_TOKEN)
print("STARTED 27 LINE BOT.PY")
# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Form(StatesGroup):
    name = State()  # Will be represented in storage as 'Form:name'
    surname = State()  # Will be represented in storage as 'Form:surname'
    phone = State() # Will be represented in storage as 'Form:phone'
    image = State()  # Will be represented in storage as 'Form:image'
    confirm = State() # Will be represented in storage as 'Form:confirm'


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    print(message)
    # Set state
    await Form.name.set()

    await message.reply("Assalomu alaykyum, Ismingiz ?")


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='ortga')
@dp.message_handler(Text(equals='ortga', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Royhatdan otkazish tohtatildi', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['name'] = message.text

    await Form.next()
    await message.reply("Familyangiz ?")


@dp.message_handler(state=Form.surname)
async def process_surname(message: types.Message, state: FSMContext):
    """
    Process user surname
    """
    async with state.proxy() as data:
        data['surname'] = message.text

    await Form.next()
    await message.reply("Telefon raqamingiz ?")


@dp.message_handler(state=Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    """
    Process user phone
    """
    async with state.proxy() as data:
        data['phone'] = message.text

    await Form.next()
    await message.reply("Tanlov uchun tayyorlagan materialingizni yuboring.")


@dp.message_handler(content_types=['photo'], state=Form.image)
async def process_image(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['image'] = message.photo[-1]
        # Remove keyboard
        markup = types.InlineKeyboardMarkup(row=2)
        button1 = types.InlineKeyboardButton(text='Ha', callback_data='yes')
        button2 = types.InlineKeyboardButton(text='Yoq', callback_data='no')
        markup.add(button1)
        markup.add(button2)
        unique_name = generate_image_name() + '.png'
        await message.photo[-1].download(unique_name)
        # And send message
        msg = f"""
        Ushbu ma'lumotlar to'grimi?
        """
        await bot.send_photo(message.chat.id, open(unique_name, 'rb'), f"{data['name']}\n{data['surname']}")
        await bot.send_message(message.chat.id, f"{data['phone']}")
        await bot.send_message(message.chat.id, msg, reply_markup=markup)
        if os.path.exists(unique_name):
            os.remove(unique_name)
    # Form next
    await Form.next()
    # await state.finish()

@dp.message_handler(content_types=['video'], state=Form.image)
async def process_image(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['video'] = message.video.file_id
        # Remove keyboard
        markup = types.InlineKeyboardMarkup(row=2)
        button1 = types.InlineKeyboardButton(text='Ha', callback_data='yes')
        button2 = types.InlineKeyboardButton(text='Yoq', callback_data='no')
        markup.add(button1)
        markup.add(button2)
        unique_name = generate_image_name() + '.mp4'
        file_id = message.video.file_id # Get file id
        file = await bot.get_file(file_id) # Get file path
        await bot.download_file(file.file_path, unique_name)
        # And send message
        msg = f"""
        Ushbu ma'lumotlar to'grimi?
        """
        await bot.send_video(message.chat.id, open(unique_name, 'rb'), f"{data['name']}\n{data['surname']}")
        await bot.send_message(message.chat.id, f"{data['phone']}")
        await bot.send_message(message.chat.id, msg, reply_markup=markup)
        if os.path.exists(unique_name):
            os.remove(unique_name)
    # Form next
    await Form.next()
    # await state.finish()


@dp.callback_query_handler(state=Form.confirm)
async def process_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'yes':
        async with state.proxy() as data:
            image = data.get('image', None)
            video = data.get('video', None)
            if image:
                unique_name = generate_image_name() + '.png'
                image = data['image']
                file = await bot.get_file(image.file_id)
                file_path = file.file_path
                await bot.download_file(file_path, unique_name)
                # group
                await bot.send_photo(BOT_GROUP, open(unique_name, 'rb'), f"{data['name']}\n{data['surname']}")
                await bot.send_message(BOT_GROUP, f"{data['phone']}")
                # other
                await bot.send_photo("5149289550", open(unique_name, 'rb'), f"{data['name']}\n{data['surname']}")
                await bot.send_message("5149289550", f"{data['phone']}")
                # client
                await bot.send_message(call.from_user.id, "🥳 Muvaffaqiyatli yuborildi !!!")
                if os.path.exists(unique_name):
                    os.remove(unique_name)
                await state.finish()
            elif video:
                unique_name = generate_image_name()
                video = data['video']
                file = await bot.get_file(video)
                file_path = file.file_path
                await bot.download_file(file_path, unique_name)
                # group
                await bot.send_video(BOT_GROUP, open(unique_name, 'rb'), f"{data['name']}\n{data['surname']}")
                await bot.send_message(BOT_GROUP, f"{data['name']}\n{data['surname']}\n{data['phone']}")
                # other
                await bot.send_video("5149289550", open(unique_name, 'rb'), f"{data['name']}\n{data['surname']}")
                await bot.send_message("5149289550", f"{data['name']}\n{data['surname']}\n{data['phone']}")
                # client
                await bot.send_message(call.from_user.id, "🥳 Muvaffaqiyatli yuborildi !!!")
                if os.path.exists(unique_name):
                    os.remove(unique_name)
                await state.finish()
            else:
                await bot.send_message(call.from_user.id, "Hatolik yuz berdi keginroq urinib ko'ring.")
    elif call.data == 'no':
        await state.finish()
        await bot.send_message(call.from_user.id, f"Royhatdan o'tkazish to'htatildi.\nQayta topshirish uchun /start")
    # async with state.proxy() as data:
    #     data['image'] = call.photo[-1]



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)