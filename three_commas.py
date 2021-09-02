# from config import Config
from py3cw.request import Py3CW
import requests

class Three_Commas():
    def __init__(self, parameter_dict, account_id="29787725"):
        self.account_id = account_id

        self.account = Py3CW( 
            key             = parameter_dict['threecommas_api_key'],
            secret          = parameter_dict['threecommas_secret_key'],
            request_options = {'request_timeout': 10, 'nr_of_retries': 3, 'retry_status_codes': [502]} )

    def ping(self):
        response_ping = None
        try:
            response_ping = requests.get("https://api.3commas.io/public/api")
        except Exception as e:
            print(e)

        return response_ping.status_code

    def get_account_stats(self):
        error, data = self.account.request(entity='bots', action='stats')
        for key, value in data.items():
            print(key, value)
        return data

    def get_account_balance(self):
        error, data = self.account.request(entity='accounts', action='load_balances', action_id=self.account_id)
        print(data)
        return data

    def get_single_bot_stats(self, bot_id: str):
        error, data = self.account.request(entity='bots', action='show', action_id=bot_id) 
        for key, value in data.items():
            print(key, value)


    def get_account(self):
        error, data = self.account.request(entity='accounts', action='')
        print(data)
        return data    

    def get_single_bot_active_deals(self, bot_id: str):
        error, data = self.account.request(entity='bots', action='show', action_id=bot_id) 
        return data['active_deals_count']


    def disable_test(self, id):
        r"""
        Exception in thread Thread-1:
        Traceback (most recent call last):
        File "C:\Users\Rory Glenn\AppData\Local\Programs\Python\Python39\lib\threading.py", line 954, in _bootstrap_inner
            self.run()
        File "C:\Users\Rory Glenn\AppData\Local\Programs\Python\Python39\lib\threading.py", line 892, in run
            self._target(*self._args, **self._kwargs)
        File "c:\Users\Rory Glenn\Desktop\Anti-Liquidation-Bot\main.py", line 316, in anti_liquidation_procedure
            threecommas.disable_test(4716685) # Key error
        File "c:\Users\Rory Glenn\Desktop\Anti-Liquidation-Bot\three_commas.py", line 54, in disable_test
            error, data = self.account.request(entity='bots', action=f'{id}/disable')
        File "C:\Users\Rory Glenn\AppData\Local\Programs\Python\Python39\lib\site-packages\py3cw\utils.py", line 14, in wrapper
            api = API_METHODS[entity][action]
        KeyError: '4716685/disable'        
        """
        # https://github.com/bogdanteodoru/py3cw/blob/master/py3cw/config.py
        error, data = self.account.request(entity='bots', action=f'{str(id)}/disable')

    def disable_all_bots(self, bot_id_list):
        # https://github.com/3commas-io/3commas-official-api-docs/blob/master/bots_api.md
            # POST /ver1/bots/{bot_id}/disable
        for id in bot_id_list:
            error, data = self.account.request(entity='bots', action=f'{id}/disable')



    def get_all_bots(self):
        """ Only gets the first 50 bots, not fully functional"""
        error, data = self.account.request(entity='bots', action='')
        pairs = list()
        for list_item in data:
            for key, value in list_item.items():
                if key == 'pairs':
                    pairs.append(value)
        return pairs


    def get_all_bot_ids(self):
        error, data = self.account.request(entity='bots', action='')
        id_list = list()
        for dictionary in data:
            id_list.append(dictionary['id'])
        return id_list


    def get_all_active_safety_orders(self):
        """ Getting outdated info, not function"""
        error, data = self.account.request(entity='deals', action='')
        active_safety_orders = dict()

        for dictionary in data:
            active_safety_orders[dictionary['bot_name']] = dictionary['current_active_safety_orders_count'] # current_active_safety_orders or current_active_safety_orders_count
        print(active_safety_orders)
        return active_safety_orders


    def get_active_trading_entities(self):
        error, data = self.account.request(entity='accounts', action='active_trading_entities', action_id=self.account_id)
        print(data)
        return data

    def create_bot(self):
        error, data = self.account.request(entity='bots', action='create_bot')
        print(error)
        print(data)


    def post_request(self):
        url = 'POST /ver1/bots/create_bot'
        myobj = {'name': 'somevalue'}
        x = requests.post(url, )


# if __name__ == '__main__':
#     param_dict = dict()
#     param_dict['threecommas_api_key']        = "cd2ad81a13f146daa4ca04dbd09d1c540dbaefcec10e4e869ae63e87b623e5b9"
#     param_dict['threecommas_secret_key'] = "8d71184f3a759a16d5f2aa0c7dd241f00f8c786d4c79a7b87de2cd5791b41991291ce4e7f1c05cab7807cfd760cae134d59f4fa77dfdb75df793332dc82e53170df8cab8cee1a3ffcefe43d3c7199d8a72cd75c3787878fce19f479859939340b060f8e5"
#     tc = Three_Commas(param_dict)

#     bots = tc.get_all_bots()
#     print(bots)
    