from database.database_methods import DBaseL
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class BotMethods:

    def __init__(self, self_bot):
        self.self_bot = self_bot
        self.db = DBaseL()

    async def start_greetings(self, message):
        self.db.create_customer_table()
        await self.self_bot.bot.send_message(message.chat.id, self.self_bot.variables.greetings)

    async def collect_user_data(self, message):
        await FormVerificationCode.name.set()
        await self.self_bot.bot.send_message(message.chat.id, self.self_bot.variables.ask_name)

    async def submit(self, message):
        submit_text = ""
        for key in self.self_bot.variables.submit_text:
            submit_text += f"{self.self_bot.variables.submit_text[key]}{self.self_bot.user_data[key]} {self.self_bot.user_data['last_name']}\n" if key == 'name' else f"{self.self_bot.variables.submit_text[key]}{self.self_bot.user_data[key]}\n"
        submit_text += f"\n{self.self_bot.variables.ask_submit}"

        inline_keyboard = await self.get_inline_keyboard(self.self_bot.variables.submit_inline_buttons)
        await self.self_bot.bot.send_message(message.chat.id, submit_text, reply_markup=inline_keyboard)

    async def agreement(self, message):
        await self.self_bot.bot.send_message(message.chat.id, self.self_bot.variables.agreement_text, reply_markup=await self.get_keyboard_with_link(button=self.self_bot.variables.agreement_url))
        await self.self_bot.bot.send_message(message.chat.id, self.self_bot.variables.agreement_text, reply_markup=await self.get_inline_keyboard(buttons=self.self_bot.variables.confirm_inline_buttons))

    async def we_received_apply(self, message):
        exists = await self.db.check_exists({'user_id': message.chat.id})
        if not exists:
            self.self_bot.user_data['user_id'] = message.chat.id
            self.self_bot.user_data['agreement'] = True
            self.self_bot.user_data['ticket_serial_number'] = await self.get_generated_code()
            self.db.insert_to_database(self.self_bot.user_data)
            await self.self_bot.bot.send_message(message.chat.id, self.self_bot.variables.we_received_your_apply)
        else:
            await self.self_bot.bot.send_message(message.chat.id, self.self_bot.variables.user_exists_already)

    async def get_keyboard_with_link(self, button:dict):
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        button = InlineKeyboardButton(list(button.keys())[0], list(button.values())[0])
        return keyboard.add(button)

    async def get_inline_keyboard(self, buttons:dict, row=3):
        inline_buttons_list = []
        buttons_row_list = []
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)

        counter = 1
        for key in buttons:
            if counter <= row:
                buttons_row_list.append(InlineKeyboardButton(str(key), callback_data=str(buttons[key])))
                counter += 1
            else:
                counter = 1
                inline_buttons_list.append(buttons_row_list)
                buttons_row_list = []
                buttons_row_list.append(InlineKeyboardButton(str(key), callback_data=str(buttons[key])))
        inline_buttons_list.append(buttons_row_list)

        for i in inline_buttons_list:
            keyboard.row(*i)

        self.self_bot.callbacks = list(buttons.values())
        return keyboard

    async def phone_number_validation(self, phone_number, message):
        if len(phone_number) <= 13 and len(phone_number) >= 12 and phone_number[0:1] == '+':
            return True
        else:
            await self.self_bot.bot.send_message(message.chat.id, "Некорректный номер, введите ,пожалуйста, еще раз")
            return False

    async def get_generated_code(self):
        return "Ghjfsd:hd^7sdjk"

class FormVerificationCode(StatesGroup):
    name = State()
    last_name = State()
    phone_number = State()
    company = State()
