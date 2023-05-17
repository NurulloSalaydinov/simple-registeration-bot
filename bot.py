import logging
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
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
# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Form(StatesGroup):
    name = State()  # Will be represented in storage as 'Form:name'
    surname = State()  # Will be represented in storage as 'Form:surname'
    age = State()  # Will be represented in storage as 'Form:age'
    phone = State() # Will be represented in storage as 'Form:phone'
    address = State() # Will be represented in storage as 'Form:address'
    desc = State() # Will be represented in storage as 'Form:desc'
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

    await message.reply("Assalomu alaykyum, Ismingiz?")


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
    await message.reply("Familyangiz?")


@dp.message_handler(state=Form.surname)
async def process_surname(message: types.Message, state: FSMContext):
    """
    Process user surname
    """
    async with state.proxy() as data:
        data['surname'] = message.text

    await Form.next()
    await message.reply("Yoshingiz?")


@dp.message_handler(state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    """
    Process user age
    """
    async with state.proxy() as data:
        data['age'] = message.text

    await Form.next()
    await message.reply("Telefon raqamingiz?")


@dp.message_handler(state=Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    """
    Process user phone
    """
    async with state.proxy() as data:
        data['phone'] = message.text

    await Form.next()
    await message.reply("Yashash manzilingiz?")


@dp.message_handler(state=Form.address)
async def process_address(message: types.Message, state: FSMContext):
    """
    Process user address
    """
    async with state.proxy() as data:
        data['address'] = message.text

    markup = types.ReplyKeyboardRemove()
    await Form.next()
    await message.reply("Murojaatingiz", reply_markup=markup)


@dp.message_handler(state=Form.desc)
async def process_desc(message: types.Message, state: FSMContext):
    """
    Process user desc
    """
    async with state.proxy() as data:
        data['desc'] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(text='Rasm yoki Video yoq 🚫')
    markup.add(button)
    await Form.next()
    await message.reply("📸Rasm yoki 🎞Video yuklang", reply_markup=markup)



@dp.message_handler(state=Form.image)
async def process_not_exist(message: types.Message, state: FSMContext):
    """
    Process File or Image that does not exis
    """
    async with state.proxy() as data:
        data['detail'] = "Mavjud emas"
        markup = types.InlineKeyboardMarkup(row=2)
        button1 = types.InlineKeyboardButton(text='Ha', callback_data='yes')
        button2 = types.InlineKeyboardButton(text='Yoq', callback_data='no')
        msg = f"Ism: {data['name']}\nFamilya: {data['surname']}\nYosh: {data['age']}\nTelefon raqam: {data['phone']}\nManzil: {data['address']}\nMurojaat: {data['desc']}\nUshbu ma'lumotlar to'grimi?"
        markup.add(button1)
        markup.add(button2)
        await bot.send_message(message.chat.id, msg, reply_markup=markup)
    await Form.next()
    

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
        msg = f"Ism: {data['name']}\nFamilya: {data['surname']}\nYosh: {data['age']}\nTelefon raqam: {data['phone']}\nManzil: {data['address']}\nMurojaat: {data['desc']}\n Ushbu ma'lumotlar tog'rimi?"
        await bot.send_photo(message.chat.id, open(unique_name, 'rb'), msg, reply_markup=markup)
        if os.path.exists(unique_name):
            os.remove(unique_name)
    # Form next
    await Form.next()
    # await state.finish()

@dp.message_handler(content_types=['video'], state=Form.image)
async def process_video(message: types.Message, state: FSMContext):
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
        msg = f"Ism: {data['name']}\nFamilya: {data['surname']}\nYosh: {data['age']}\nTelefon raqam: {data['phone']}\nManzil: {data['address']}\nMurojaat: {data['desc']}\nUshbu ma'lumotlar to'grimi?"
        await bot.send_video(message.chat.id, open(unique_name, 'rb'), msg, reply_markup=markup)
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
            markup = types.ReplyKeyboardRemove()
            if image:
                unique_name = generate_image_name() + '.png'
                image = data['image']
                file = await bot.get_file(image.file_id)
                file_path = file.file_path
                await bot.download_file(file_path, unique_name)
                # group
                msg = f"Ism: {data['name']}\nFamilya: {data['surname']}\nYosh: {data['age']}\nTelefon raqam: {data['phone']}\nManzil: {data['address']}\nMurojaat: {data['desc']}"
                await bot.send_photo(BOT_GROUP, open(unique_name, 'rb'), msg)
                # client
                await bot.send_message(call.from_user.id, "🥳 Muvaffaqiyatli yuborildi !!!", reply_markup=markup)
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
                msg = f"Ism: {data['name']}\nFamilya: {data['surname']}\nYosh: {data['age']}\nTelefon raqam: {data['phone']}\nManzil: {data['address']}\nMurojaat: {data['desc']}"
                await bot.send_video(BOT_GROUP, open(unique_name, 'rb'), msg)
                # client
                await bot.send_message(call.from_user.id, "🥳 Muvaffaqiyatli yuborildi !!!", reply_markup=markup)
                # finish
                if os.path.exists(unique_name):
                    os.remove(unique_name)
                await state.finish()
            else:
                # group
                msg = f"Ism: {data['name']}\nFamilya: {data['surname']}\nYosh: {data['age']}\nTelefon raqam: {data['phone']}\nManzil: {data['address']}\nMurojaat: {data['desc']}"
                await bot.send_message(BOT_GROUP, msg)
                # client
                await bot.send_message(call.from_user.id, "🥳 Muvaffaqiyatli yuborildi !!!", reply_markup=markup)
                # finish
                await state.finish()

    elif call.data == 'no':
        await state.finish()
        await bot.send_message(call.from_user.id, f"Royhatdan o'tkazish to'htatildi.\nQayta topshirish uchun /start")
    # async with state.proxy() as data:
    #     data['image'] = call.photo[-1]



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)