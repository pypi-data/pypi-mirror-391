import json
from osonbot import Bot, KeyboardButton, InlineKeyboardButton, URLKeyboardButton

class JsonBot(Bot):
    def __init__(self, token, configure: str | dict):
        self.token = token
        super().__init__(token, auto_db=False)
        if isinstance(configure, str):
            with open(configure, 'r') as file:
                self.configure = json.load(file)
        else:
            self.configure = configure

    def setter(self):
        for text, data in self.configure['messages'].items():
            response = data.get("response", "")
            parse_mode = data.get("parse_mode", None)
            buttons = data.get("reply_markup")

            self.when(condition=text, text=response, parse_mode=parse_mode, reply_markup=buttons)
        
        for text, data in self.configure.get('inline_messages', {}).items():
            response = data.get("response", "")
            parse_mode = data.get("parse_mode", None)
            buttons = data.get("reply_markup")

            self.c_when(condition=text, text=response, parse_mode=parse_mode, reply_markup=buttons)

    def generate_code(self, library: str, file: str):
        code = ""
        if library == "osonbot":
            code += "from osonbot import Bot\n"
            code += f"bot = Bot(\"{self.token}\")\n\n"
            for text, data in self.configure.items():
                response = data.get("response", "")
                parse_mode = data.get("parse_mode", None)
                buttons = data.get("reply_markup")
                
                code += f"bot.when(\"{text}\", \"{response}\", parse_mode={parse_mode}, reply_markup={buttons})\n"
            
            code += "\nbot.run()"

            with open(file, "w") as f:
                f.write(code)
            
            self.logger.info(f"Code generated in {file}")
        if library == "pytelegrambotapi":
            code += "from telebot import Bot\n"

    def run(self):
        self.setter()
        return super().run()
