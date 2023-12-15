from aiogram import types, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from bot import bot_variables as variables
from bot.bot_methods import BotMethods, FormVerificationCode

class BotHandlers:

    def __init__(self, token):
        self.bot = Bot(token=token)
        storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=storage)
        self.variables = variables
        self.methods = BotMethods(self)
        self.user_data = {}
        self.callbacks = []

    def handlers(self):

        @self.dp.message_handler(commands=['start'])
        async def start(message: types.Message):
            await self.methods.start_greetings(message)
            await self.methods.collect_user_data(message)

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

        executor.start_polling(self.dp, skip_updates=True)
