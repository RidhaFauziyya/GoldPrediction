from configparser import ConfigParser
from datetime import datetime, timedelta
import os, psycopg2, yfinance as yf, pandas as pd, json, requests, math, joblib

base_dir = os.getcwd()

def get_curr_work_dir():
    directories = dict()

    directories['templates_dir'], directories['static_dir'] = os.path.join(base_dir, 'Views'), os.path.join(base_dir, 'Public')
    directories['controllers_dir'], directories['helpers_dir'] = os.path.join(base_dir, 'App\\Controllers'), os.path.join(base_dir, 'App\\Helpers')
    directories['js_dir'], directories['css_dir'] = os.path.join(base_dir, 'Public\\Scripts\\css'), os.path.join(base_dir, 'Public\\Scripts\\js')
    
    return directories

def get_gold_data(start_date, end_date, ticker='GC=F'):
    try:
        gold_data = yf.download(ticker, start=start_date, end=end_date)
        gold_data = gold_data.reset_index()

        histories = dict()
        histories['date_data'] = gold_data['Date'].tolist()
        histories['close_data'] = gold_data['Close'].tolist()

        '''
        gold_data = gold_data[['Date','Close']]
        gold_data.astype({'Date': str}).to_json(os.path.join(base_dir, 'Public\\Dataset\\gold_historical_data.json'), orient='records', lines=False)
        '''

        return histories
    except Exception as e:
        print(e) 

def convert_currencies(amount, curr_currency, prefered):
    url = f'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{curr_currency}.json'
    response = requests.get(url)
    exchange_rate = response.json()
    converted_amount = "{:0,.2f}".format(float(amount * exchange_rate[curr_currency][prefered]))

    return converted_amount

def get_gold_price_today():
    url = 'https://api.gold-api.com/price/XAU'
    response = requests.get(url).json()
    return "{:0,.2f}".format(float(response['price'])) 

def get_historical_gold_prices(window, date_start=None, date_end=None, ticker='GC=F'):
    if (date_start == None) and (date_end == None):
        date_start = datetime.today()-timedelta(days = window * 2)
        date_end = datetime.today()

    response = yf.download(ticker, start=date_start, end=date_end)
    if len(response) < window:
        get_historical_gold_prices(window*2)
    else:
        return [list(round(price, 2) for price in response['Close'][-window:])]

def predict_gold_price(model_name, data, prefered_currency='idr'):
    loaded_model = joblib.load(os.path.join(base_dir, f'App\\Models\\{model_name}'))
    if prefered_currency != 'usd':
        result = convert_currencies(loaded_model.predict(data)[0], 'usd', prefered_currency)
    else:
        result = "{:0,.2f}".format(float(loaded_model.predict(data)[0]))

    return result

def check_data_window_conf(model_window, algorithm='mlp'):
    if model_window == 'day':
        data_window, model_name = 7, f'{algorithm}_model_daily.sav'
    elif model_window == 'week':
        data_window, model_name = 11, f'{algorithm}_model_weekly.sav'
    elif model_window == 'month':
        data_window, model_name = 10, f'{algorithm}_model_monthly.sav'
    elif model_window == 'year':
        data_window, model_name = 10, f'{algorithm}_model_yearly.sav'
    
    return data_window, model_name

def load_config(filepath=os.path.join(base_dir, 'database.ini'), section='postgresql'):
    parser = ConfigParser()
    parser.read(filepath)

    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filepath))

    return config

def connect(config):
    try:
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)