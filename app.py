#!/usr/bin/env python3
import os,csv,time,requests,json
from datetime import datetime
from statistics import mean
from flask import Flask, jsonify
import pandas as pd
from threading import Thread

app = Flask(__name__)
poll_interval_seconds = 60
max_array_len = 604800
url = 'https://gasstation-mainnet.matic.network/v2'

def json_request(url):
    try:
        return requests.get(url).json()
    except Exception as error:
        print('{} [ERROR] JSON query errored out: {}'.format(datetime.now(),error))
        pass

def query_gas_price():
    try:
        response = json_request(url)
        std_gas_price_gwei = response.get('standard').get('maxFee')
        print('{} [INFO] Standard Gas Price GWEI: {}'.format(datetime.now(),std_gas_price_gwei))
        std_gas_price_wei = int(std_gas_price_gwei * (10 ** 18))
        return std_gas_price_wei
    except Exception as error:
        print('{} [ERROR] JSON query errored out: {}'.format(datetime.now(),error))
        pass

def request_success(data):
    result = {
        "data": {
        "avg_gas_price": data
        },
        "statusCode": 200,
    }
    return result

def request_error(error):
    result = {
        "error": "{}".format(error),
        "statusCode": 500,
    }
    return result

@app.route('/')
def main():
    try:
        df = pd.read_csv(filename, header=None)
        df[0] = df[0].astype(float)
        average_price = int(df[0].mean())
        print('{} [INFO] Average Gas Price: {}'.format(datetime.now(),average_price))
        return_response = request_success(average_price)
        return jsonify(return_response)
    except Exception as error:
        return_response = request_error(error)
        return jsonify(return_response)

def store_price():
    while True:
        std_gas_price_wei = query_gas_price()
        df = pd.DataFrame({0:std_gas_price_wei},index=[0])
        if os.path.exists(filename) and os.stat(filename).st_size > 0:
            df_existing = pd.read_csv(filename, header=None)
            if len(df_existing) >= max_array_len:
                df_existing = df_existing.drop(df_existing.index[0])
            df = pd.concat([df_existing, df], ignore_index=True)
            df.to_csv(filename, index=False, header=False)
        else:
            df.to_csv(filename, encoding='utf-8', index=False, header=False)
        print('{} [INFO] Polling Standard Gas Price GWEI in {} seconds'.format(datetime.now(),poll_interval_seconds))
        time.sleep(poll_interval_seconds)


if __name__ == '__main__':
    print('{} [INFO] External Adapter Initialized, listening on port 8080'.format(datetime.now()))
    filename = 'prices.csv'
    t = Thread(target=store_price)
    t.start()
    app.run(host='0.0.0.0', port='8080')
