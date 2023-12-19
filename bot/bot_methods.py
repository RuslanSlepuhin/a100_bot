from database.database_methods import DBaseL
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.bot_variables import customer_table, qrcode_read_path

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

    async def confirm(self, message):
        self.self_bot.callbacks = []
        users_list = self.db.select(table=self.self_bot.variables.customer_table)
        for user in users_list:
            text = ''
            for key in user:
                text += f"{key}: {user[key]}\n"
            markup = InlineKeyboardMarkup()
            callback_data = f"{self.self_bot.variables.admin_confirms_user} {user['user_id']}"
            self.self_bot.callbacks.append(callback_data)
            markup.add(InlineKeyboardButton("Confirm", callback_data=callback_data))
            await self.self_bot.bot.send_message(message.chat.id, text, reply_markup=markup)

    async def provide_user_ticket(self, message, user_id):
        special_code = self.db.select(table=customer_table, where=f"user_id={int(user_id)}")[0]['ticket_serial_number']
        from QR.qr_codes import QRCodeCreateAndRead
        qr = QRCodeCreateAndRead()
        image_path = qr.qr_create(data=special_code)
        with open(image_path, 'rb') as file:
            try:
                await self.self_bot.bot.send_photo(chat_id=message.chat.id, photo=file, caption="Please take the ticket", parse_mode='html')
            except Exception as ex:
                print('photo sending error')

    async def read_qr_code(self, message):
        from QR.qr_codes import QRCodeCreateAndRead
        qr_code = QRCodeCreateAndRead()
        data = qr_code.read(qrcode_read_path)
        if data:
            text = ''
            await self.self_bot.bot.send_message(message.chat.id, data)
            user = self.db.select(table=customer_table, where=f"ticket_serial_number='{data}'")
            for key in user[0]:
                text += f"{key}: {user[0][key]}\n"
            return await self.self_bot.bot.send_message(message.chat.id, text)

        else:
            return await self.self_bot.bot.send_message(message.chat.id, "Sorry, I couldn't read")

    async def admin_greetings(self, message):
        await self.db.add_users([message.chat.id])
        await self.self_bot.bot.send_message(message.chat.id, self.self_bot.variables.admin_instruction_text)

    async def add_admin(self, message, admin_id=None):
        admin_id = await self.add_admin_check_int(admin_id=admin_id)
        if admin_id:
            if await self.add_admin_check_subscriber(admin_id, message):
                await self.add_admin_add_to_database(admin_id, message)
        else:
            await self.self_bot.bot.send_message(message.chat.id, self.self_bot.variables.user_id_error_int_text)
            await self.add_admin_fill_form(message)

    async def add_admin_check_int(self, admin_id):
        try:
            admin_id = int(admin_id)
            return admin_id
        except Exception as ex:
            print(ex)
            return False

    async def add_admin_check_subscriber(self, admin_id, message):
        try:
            await self.self_bot.bot.send_message(admin_id, self.self_bot.variables.you_have_been_added_as_admin)
            return True
        except:
            await self.self_bot.bot.send_message(message.chat.id, self.self_bot.variables.user_id_error_subscriber_text)
            return False

    async def add_admin_add_to_database(self, admin_id, message):
        if await self.db.check_exists(table_name=self.self_bot.variables.admin_table, user_data={'user_id': admin_id}):
            await self.self_bot.bot.send_message(message.chat.id, self.self_bot.variables.admin_exists_already_text)
        else:
            self.db.insert_to_database(user_data={'user_id': admin_id}, table_name=self.self_bot.variables.admin_table)
            await self.self_bot.bot.send_message(message.chat.id, self.self_bot.variables.admin_has_been_added_text)

    async def add_admin_fill_form(self, message):
        await AddAdmin.user_id.set()
        await self.self_bot.bot.send_message(message.chat.id, self.self_bot.variables.add_admin_text)

    async def delete_user(self):
        pass

    def get_admin_list(self):
        return [i['user_id'] for i in self.db.select(table=self.self_bot.variables.admin_table, requested_columns=['user_id'])]

class FormVerificationCode(StatesGroup):
    name = State()
    last_name = State()
    phone_number = State()
    company = State()

class AddAdmin(StatesGroup):
    user_id = State()