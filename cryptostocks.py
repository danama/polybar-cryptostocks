#!/usr/bin/env python3

import sys
import requests
import yaml
from os.path import expanduser
from decimal import Decimal
from yahoo_fin import stock_info as si

# File must be opened with utf-8 explicitly
config = None
with open(expanduser('~/.config/polybar/cryptostocks-config'), 'r', encoding='utf-8') as ymlconfig:
    try:
        config = yaml.full_load(ymlconfig)
    except yaml.YAMLError as e:
        print(e)

# Variables
base_currency = config['general']['crypto_base_currency']
params = {'convert': base_currency}
roundNumber = int(config['general']['stock_roundnumber'])
up_color = config['general']['up_color']
down_color = config['general']['down_color']
reset_color = '%{F-}'


def stockdata(ticker,label,display,colors):
    tickerPrice = si.get_live_price(ticker)
    tickerData = si.get_quote_data(ticker)
    change_24 = round(float(tickerData['regularMarketChangePercent']),2)
    if colors == True:
        color = up_color if change_24 >= 0 else down_color
    else:
        color = reset_color
    if display == 'both' or display == 'none':
        output = label + ': ' + str(round(tickerPrice, roundNumber)) + ' ' + color + str(change_24) + '%' + reset_color
    elif display == 'percentage':
        output = color + str(change_24) + '%' + reset_color
    elif display == 'price':
        output = color + str(tickerPrice) + reset_color
    return output

def cryptodata(name,icon,display,colors):
    market_data = requests.get(f'https://api.coingecko.com/api/v3/coins/{name}').json()["market_data"]
    local_price = round(Decimal(market_data["current_price"][f'{base_currency.lower()}']), 2)
    change_24 = round(float(market_data['price_change_percentage_24h']),2)
    if colors == True:
        color = up_color if change_24 >= 0 else down_color
    else:
        color = reset_color
    if display == 'both' or display == 'none':
        output = icon + ' ' + str(local_price) + ' ' + color + str(change_24) + '%' + reset_color
    elif display == 'percentage':
        output = icon + ' ' + color + str(change_24) + '%' + reset_color
    elif display == 'price':
        output = icon + ' ' + color + str(local_price) + reset_color
    return output


for stock in config['stocks'].values():
    try:
        stocks = stockdata(stock['ticker'], stock['label'], stock['display'], config['general']['colors'])
        sys.stdout.write(f'{stocks} | ')
    except:
        sys.stdout.write('Failed to get info')
        break

for crypto in config['cryptos'].values():
    try:
        crypto_info = cryptodata(crypto['name'], crypto['icon'], crypto['display'], config['general']['colors'])
        sys.stdout.write(f'{crypto_info} | ')

    except requests.exceptions.ConnectionError as e:
        sys.stdout.write('Failed to get info')
        break
  
