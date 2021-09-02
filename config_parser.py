from log import Log
from datetime import datetime

"""Parses config.txt for all keys used in Anti-Liquidation bot

    config.txt should be in this format:
            binance_api_key                = "ihx8J0880DhluXHuE4wOGvttOkSPkNLnsZLrFHsV8StI4P4OXHoftD7tdVNFphCI"
            binance_secret_key             = "ucGl8rLZXtH4P5QRZqynA4GlTyjkzubUxfYTJRWEg68tdMFlyaMXrTYg1WeRjOy5"

            threecommas_api_key            = "cd2ad81a13f146daa4ca04dbd09d1c540dbaefcec10e4e869ae63e87b623e5b9"
            threecommas_secret_key         = "8d71184f3a759a16d5f2aa0c7dd241f00f8c786d4c79a7b87de2cd5791b41991291ce4e7f1c05cab7807cfd760cae134d59f4fa77dfdb75df793332dc82e53170df8cab8cee1a3ffcefe43d3c7199d8a72cd75c3787878fce19f479859939340b060f8e5"

            twilio_account_sid             = "AC237a0b1b5d91082f4a67b0aee90ff643"
            twilio_auth_token              = "2c5f4bb2f993713d8f07e28dd733ac2b"
            twilio_bot_phonenumber         = "+12075608869"
            my_cell_number                 = "+16617145194"

            hedge_symbol                   = "ETHUSDT"

            text                           = True
            phone_call                     = True
            rake                           = False
            buy_bnb                        = True

            margin_ratio_threshold         = 15
            rake_percent                   = 100
            hedge_leverage                 = 50
            hedge_stop_percent             = 10
            hedge_percent                  = 100
            short_long_ratio_limit_percent = 90
            close_percent                  = 0.50
"""


class ConfigParser():
    def __init__(self, log_file: Log):
        self.binance_api_key                = "binance_api_key"
        self.binance_secret_key             = "binance_secret_key"
        self.threecommas_api_key            = "threecommas_api_key"
        self.threecommas_secret_key         = "threecommas_secret_key"
        self.twilio_account_sid             = "twilio_account_sid"
        self.twilio_auth_token              = "twilio_auth_token"
        self.twilio_bot_phonenumber         = "twilio_bot_phonenumber"
        self.my_cell_number                 = "my_cell_number"
        self.margin_ratio_threshold         = "margin_ratio_threshold"
        self.rake_percent                   = "rake_percent"
        self.text                           = "text"
        self.phone_call                     = "phone_call"
        self.rake                           = "rake"
        self.hedge_symbol                   = "hedge_symbol"
        self.hedge_leverage                 = "hedge_leverage"
        self.hedge_percent                  = "hedge_percent"
        self.hedge_stop_percent             = "hedge_stop_percent"
        self.short_long_ratio_limit_percent = "short_long_ratio_limit_percent"
        self.close_percent                  = "close_percent"
        self.buy_bnb                        = "buy_bnb"
        self.log_file                       = log_file


    def get_current_time(self):
        return datetime.now().strftime("%H:%M:%S")


    def parse_config_file(self):
        """Read from config.txt. Strips out an unnecessary characters and store key/value pairs in dictionary.
             Args can be rearranged but I don't recommend doing so"""
        
        parameter_dict = dict()
        
        parameter_list = [self.binance_api_key,
                          self.binance_secret_key,
                          self.threecommas_api_key,
                          self.threecommas_secret_key,
                          self.twilio_account_sid,
                          self.twilio_auth_token,
                          self.twilio_bot_phonenumber,
                          self.my_cell_number,
                          self.margin_ratio_threshold,
                          self.rake_percent,
                          self.text,
                          self.phone_call,
                          self.rake,
                          self.hedge_symbol,
                          self.hedge_leverage,
                          self.hedge_percent,
                          self.hedge_stop_percent,
                          self.short_long_ratio_limit_percent,
                          self.close_percent,
                          self.buy_bnb ]

        try:
            with open('config.txt', mode='r') as file:
                for line in file.readlines():
                    edited_line = line.replace("\n", "").replace(" ", "").replace('"', "").replace("=", "")
                    for param in parameter_list:
                        if param in edited_line:
                            edited_line = edited_line.replace(param, "")
                            value       = edited_line
                            parameter_dict[param] = value
                            break
            return parameter_dict
        except Exception as e:
            print(e)
            self.log_file.write(f"[!] {self.get_current_time()} {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}")
            exit()
    