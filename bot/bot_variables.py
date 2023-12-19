#------------- bot data ---------------
bot_url = "https://t.me/IronChief_bot"
admin_help = "admin_help"
user_help = "user_help"
# ------------ database --------------
database_path = "./database/customers.db"
customer_table_field_list = [
    "id INTEGER PRIMARY KEY",
    "user_id INT",
    "name VARCHAR(100)",
    "last_name VARCHAR(100)",
    "phone_number VARCHAR(100)",
    "company VARCHAR(100)",
    "agreement BOOLEAN",
    "ticket_serial_number VARCHAR(100)"
]
admin_table_field_list = [
    "id INTEGER PRIMARY KEY",
    "user_id INT",
]
customer_table = 'customers'
customer_fields_full = ['id', 'user_id', 'name', 'last_name', 'phone_number', 'company', 'agreement', 'ticket_serial_number']
admin_table = 'admins'
# ------------- dialog ---------------
greetings = "Здравствуйте, рады вас видеть! Этот бот поможет зарегистрироваться на Depo Gala, которая пройдёт 26 января в Большом театре Беларуси. Чтобы мы зарегистрировали вас и напомнили о событии заранее, пожалуйста, ответьте на несколько вопросов."
ask_name = "Как вас зовут? Укажите ваше имя."
ask_last_name = "Какая у вас фамилия?"
ask_phone_number = "приятно познакомиться! 😊\nУкажите ваш номер телефона.\nПример: +375299909999"
ask_company = "Как называется ваша компания?"
ask_submit = "Вы можете изменить данные, если нужно. Если всё верно, нажмите «Подтвердить», чтобы продолжить регистрацию."

submit_text = {
    "name": "Ваши имя и фамилия: ",
    "phone_number": "Ваш телефон: ",
    "company": "Ваша компания: "
}

submit_inline_buttons = {
    "✅ Подтвердить данные": "confirm_data",
    "✏️ Изменить данные": "edit_data"
}

agreement_text = 'Последний штрих: чтобы мы могли присылать вам уведомления о событии, подтвердите согласие на обработку персональных данных.👇\nЯ даю согласие ООО «А100 Девелопмент» (1027700229193) и его партнёрам на обработку персональных данных на условиях Политики конфиденциальности в целях регистрации моего участия в мероприятии "Depo Gala" и получения информационных сообщений о нем.'
agreement_url = {"Политика конфеденциальности": "https://google.com"}
confirm_agreement_text = "Подтвердить согласие:"
confirm_inline_buttons = {
    "✅ Подтверждаю": "confirm",
    "Отказываюсь": "reject"
}
we_received_your_apply = "Мы получили вашу заявку. Рассмотрим её в течение трёх рабочих дней и вернёмся к вам с ответом.\nПожалуйста, дождитесь подтверждения регистрации.\nОстаёмся на связи!"
user_exists_already = "Извините, такой пользователь уже зарегистрирован"

admin_confirms_user = 'confirm_user'

# ------------------- file system -----------------
qrcode_read_path = "./media/read_qr_codes/read_qrcode.jpg"
qrcode_create_path = "./media/create_qr_codes/read_qrcode.jpg"

# ------------------- admin ---------------------
admin_user_id_list = [5884559465, ]
super_admin_user_id_list = admin_user_id_list
admin_instruction_text = "Вы - админ. Вам будут приходить на подтверждение данные от участников, которые прошли анкетирование и указали свои данные"
add_admin_text = "Type the user_id. You can see it by /user_id command"
user_id_error_int_text = "Произошла ошибка, убедитесь, пожалуйста, что вы вводите целое число"
you_have_been_added_as_admin = "Вас добавили как админа"
user_id_error_subscriber_text = f"Пользователь, которого Вы хотите добавить как админа должен быть зарегистрирован в боте. Для этого ему необходимо пройти по ссылке {bot_url} и нажать старт. Перешлите ему эту инструкцию"
admin_exists_already_text = "Такой админ уже есть в базе"
admin_has_been_added_text = "Админ успешно бодавлен в базу"