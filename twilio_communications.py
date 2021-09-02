# How to get first phone number
    # https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account


from twilio.rest import Client
from log         import Log
from datetime    import datetime
from enums       import *


class Twilio_Communications():
    def __init__(self, parameter_dict: dict, log_file: Log):
        self.has_sent_warning1_text   = False
        self.has_sent_phone_call      = False
        self.client                   = Client(parameter_dict['twilio_account_sid'], parameter_dict['twilio_auth_token'])
        self.my_cell_number           = parameter_dict['my_cell_number']
        self.bot_phonenumber          = parameter_dict['twilio_bot_phonenumber']
        self.log_file                 = log_file
        self.sent_usdt_text = False
    

    def get_current_time(self):
        return datetime.now().strftime("%H:%M:%S")


    def print_and_log(self, message, e=False):
        if e:
            print(           f"[!] {self.get_current_time()} ERROR: {message}")
            print(           f"[!] {self.get_current_time()} {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}")
            self.log_file.write(f"[!] {self.get_current_time()} ERROR: {message}")
            self.log_file.write(f"[!] {self.get_current_time()} {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}")
            return

        print(              f"[*] {self.get_current_time()} {message}")
        self.log_file.write(f"[*] {self.get_current_time()} {message}")        


    def send_text(self, margin_ratio):
        if TEXT:
            try:
                if not self.has_sent_warning1_text:
                    body = f"WARNING, your margin ratio is {margin_ratio}%.\nSign into Binance immediately!",
                    
                    self.client.messages.create(
                            from_ = self.bot_phonenumber,
                            to    = self.my_cell_number,
                            body  = body)
                    
                    self.has_sent_warning1_text = True
                    self.print_and_log(message="Sent margin ratio text")
            except Exception as e:
                self.print_and_log(message="could not send margin ratio text", e=e)


    def send_disconnected_text(self, message):
        if TEXT:
            try:
                self.client.messages.create(
                        from_ = self.bot_phonenumber,
                        to    = self.my_cell_number,
                        body  = message)
                self.has_sent_warning1_text = True
                self.print_and_log(message="sent disconnected text")
            except Exception as e:
                self.print_and_log(message="could not send disconnected text", e=e)


    def send_usdt_text(self):
        if TEXT:
            try:
                if not self.sent_usdt_text:
                    message = "Warning, you have no USDT available!"
                    self.client.messages.create(
                            from_ = self.bot_phonenumber,
                            to    = self.my_cell_number,
                            body  = message)
                    self.print_and_log(message="Sent USDT text")
                    self.sent_usdt_text = True
            except Exception as e:
                self.print_and_log(message="could not send USDT text", e=e)


    def send_phone_call(self):
        if PHONE_CALL:
            try:
                if not self.has_sent_phone_call:
                    self.client.calls.create(
                            url   = "https://demo.twilio.com/docs/voice.xml",
                            from_ = self.bot_phonenumber,
                            to    = self.my_cell_number)

                    self.has_sent_phone_call = True
                    self.print_and_log(message="Sent phone call")
                    
            except Exception as e:
                self.print_and_log(message="could not send phone call", e=e)
