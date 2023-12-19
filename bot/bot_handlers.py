from aiogram import types, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from bot import bot_variables as variables
from bot.bot_methods import BotMethods, FormVerificationCode, AddAdmin


class BotHandlers:

    def __init__(self, token):
        self.bot = Bot(token=token)
        storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=storage)
        self.variables = variables
        self.methods = BotMethods(self)
        self.user_data = {}
        self.callbacks = []
        self.admin = False
        self.admin_user_id_list = []

    def handlers(self):

        self.admin_user_id_list = self.methods.get_admin_list()

        @self.dp.message_handler(commands=['start'])
        async def start(message: types.Message):

            if message.chat.id in self.admin_user_id_list:
                self.admin = True
            if self.admin:
                await self.methods.admin_greetings(message)
            else:
                await self.methods.start_greetings(message)
                await self.methods.collect_user_data(message)

        @self.dp.message_handler(commands=['help'])
        async def start(message: types.Message):
            help_text = self.variables.admin_help if message.chat.id in self.admin_user_id_list else self.variables.user_help
            await self.bot.send_message(message.chat.id, help_text)


        @self.dp.message_handler(commands=['confirm'])
        async def confirm(message: types.Message):
            await self.methods.confirm(message)

        @self.dp.message_handler(commands=['user_id'])
        async def user_id(message: types.Message):
            await self.bot.send_message(message.chat.id, message.chat.id)

        @self.dp.message_handler(commands=['add_admin'])
        async def add_admin(message: types.Message):
            if message.chat.id in self.admin_user_id_list:
                await self.methods.add_admin_fill_form(message)

        @self.dp.message_handler(commands=['delete_admin'])
        async def delete_admin(message: types.Message):
            if message.chat.id in self.variables.super_admin_user_id_list:
                await self.methods.delete_admin(message)


        @self.dp.message_handler(content_types=types.ContentType.PHOTO)
        async def handle_photo(message: types.Message):
            await message.photo[-1].download(destination_file=variables.qrcode_read_path)
            await self.methods.read_qr_code(message)

        @self.dp.message_handler(state=FormVerificationCode.name)
        async def name(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data['name'] = message.text
            self.user_data['name'] = message.text
            await FormVerificationCode.last_name.set()
            await self.bot.send_message(message.chat.id, self.variables.ask_last_name)

        @self.dp.message_handler(state=FormVerificationCode.last_name)
        async def last_name(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data['last_name'] = message.text
            self.user_data['last_name'] = message.text
            await FormVerificationCode.phone_number.set()
            await self.bot.send_message(message.chat.id, f"{self.user_data['name']}, {self.variables.ask_phone_number}")

        @self.dp.message_handler(state=FormVerificationCode.phone_number)
        async def phone_number(message: types.Message, state: FSMContext):
            validation = await self.methods.phone_number_validation(message.text, message)
            if validation:
                async with state.proxy() as data:
                    data['phone_number'] = message.text
                self.user_data['phone_number'] = message.text
                await FormVerificationCode.company.set()
                await self.bot.send_message(message.chat.id, self.variables.ask_company)
            else:
                await FormVerificationCode.phone_number.set()
                await self.bot.send_message(message.chat.id, f"{self.user_data['name']}, {self.variables.ask_phone_number}")

        @self.dp.message_handler(state=FormVerificationCode.company)
        async def company(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data['company'] = message.text
            await state.finish()
            self.user_data['company'] = message.text
            await self.methods.submit(message)

        @self.dp.message_handler(state=AddAdmin.user_id)
        async def get_user_id(message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data['user_id'] = message.text
            await state.finish()
            await self.methods.add_admin(message, admin_id=message.text)

        @self.dp.callback_query_handler()
        async def catch_callback(callback: types.CallbackQuery):
            if callback.data in self.callbacks:

                if callback.data in list(self.variables.submit_inline_buttons.values()):
                    match callback.data:
                        case "confirm_data": await self.methods.agreement(callback.message)
                        case "edit_data": await self.methods.collect_user_data(callback.message)

                if callback.data in list(self.variables.confirm_inline_buttons.values()):
                    match callback.data:
                        case "confirm": await self.methods.we_received_apply(callback.message)
                        case "reject": await self.bot.send_message(callback.message.chat.id, "reject")

                if self.variables.admin_confirms_user in callback.data:
                    user_id = callback.data.split(' ')[1]
                    await self.methods.provide_user_ticket(callback.message, user_id)

        executor.start_polling(self.dp, skip_updates=True)
