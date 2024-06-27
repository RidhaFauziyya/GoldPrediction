from App.Helpers import MainHelper as helper
from flask import Flask, redirect, url_for, request, render_template, jsonify
from datetime import datetime
import os, json, pandas as pd

working_dir = helper.get_curr_work_dir()
app = Flask(__name__, template_folder=working_dir['templates_dir'], static_url_path='', static_folder=working_dir['static_dir'])

@app.route("/")
def index():
    return render_template('Templates/index.html')

@app.route("/api/chart/get_gold_data", methods=['GET'])
def get_gold_data():
    try:
        gold_data_path = os.path.join(working_dir['static_dir'], 'Dataset/gold_historical_data.json') 
        with open(gold_data_path) as test_file:
            data = json.load(test_file)
            dataframe = pd.DataFrame.from_dict(data)

            histories = dict()
            histories['date_data'] = dataframe['Date'].tolist()
            histories['close_data'] = dataframe['Close'].tolist()
        
        return jsonify(
            {
                'response': histories,
                'status': '200 OK',
                'messages': 'success'
            }
        )
    except Exception as e:
        return jsonify(
            {
                'response': str(e),
                'status': '500 ERROR',
                'messages': 'An Error has occured!'
            }
        )

@app.route("/api/chart/get_ranges_gold_data", methods=['GET'])
def get_ranges_gold_data():
    data = request.get_json()

    try:
        return jsonify(
            {
                'response': helper.get_gold_data(data['start_date'], data['end_date']),
                'status': '200 OK',
                'messages': 'success'
            }
        )
    except Exception as e:
        return jsonify(
            {
                'response': str(e),
                'status': '500 ERROR',
                'messages': 'An Error has occured!'
            }
        )

@app.route("/api/chart/get_ranges_gold_surge_data", methods=['POST'])
def get_ranges_gold_surge_data():
    data = request.get_json()

    try:
        data_window, model_name, nums_data = helper.check_data_window_conf(data['window'].lower().split(' ')[1], algorithm='mlp', check_nums_data=True)
        prev_gold_prices = helper.get_historical_gold_prices(data_window)
        return jsonify(
            {
                'response': helper.get_potential_price_surge(nums_data, data['currency'], prev_gold_prices, model_name),
                'status': '200 OK',
                'messages': 'success'
            }
        )
    except Exception as e:
        return jsonify(
            {
                'response': str(e),
                'status': '500 ERROR',
                'messages': 'An Error has occured!'
            }
        )

@app.route("/api/get_prediction", methods=['GET'])
def get_prediction():
    data = request.get_json()

    try:
        prediction_range = data['model_ranges'].lower().split(' ')[1]
        pref_currency = data['pred_prefered_currency']
        model_algorithm = data['model']
        
        data_window, model_name = helper.check_data_window_conf(prediction_range, algorithm=model_algorithm)
        prev_gold_prices = helper.get_historical_gold_prices(data_window)

        return jsonify(
            {
                'response': helper.predict_gold_price(model_name, prev_gold_prices, prefered_currency=pref_currency),
                'status': '200 OK',
                'messages': 'success'
            }
        )
    except Exception as e:
        return jsonify(
            {
                'response': str(e),
                'status': '500 ERROR',
                'messages': 'An error has occured'
            }
        )
    
@app.route("/api/table/post_prediction_data", methods=['POST'])
def post_prediction_data():
    # get user raw json data
    data = request.get_json()

    try:
        curr_date = datetime.today().strftime('%Y-%m-%d')
        prediction_range = data['model_ranges'].lower().split(' ')[1]
        pref_currency = data['pred_prefered_currency'].lower()
        model_algorithm = data['model']
        
        # get prediction prerequisites
        data_window, model_name = helper.check_data_window_conf(prediction_range, algorithm=model_algorithm)
        prev_gold_prices = helper.get_historical_gold_prices(data_window)

        # perform prediction
        pred_result = helper.predict_gold_price(model_name, prev_gold_prices, prefered_currency=pref_currency)

        # save data
        with open(os.path.join(working_dir['static_dir'], 'Dataset/prediction_histories.json')) as file:
            json_data = json.load(file)
            dataframe = pd.DataFrame.from_dict(json_data)
        
            dataframe.loc[len(dataframe)] = [curr_date, pref_currency, str(helper.get_gold_price_today()), data['model_ranges'], str(pred_result)]
            dataframe.astype({'Date': str}).to_json(os.path.join(working_dir['static_dir'], 'Dataset/prediction_histories.json'), orient='records', lines=False)

        # load and return updated json
        with open(os.path.join(working_dir['static_dir'], 'Dataset/prediction_histories.json')) as file:
            updated_json = json.load(file)

        return jsonify(
            {
                'response': updated_json,
                'status': '200 OK',
                'messages': 'success'
            }
        )
    except Exception as e:
        return jsonify(
            {
                'response': str(e),
                'status': '500 ERROR',
                'messages': 'An error has occured'
            }
        )

@app.route("/api/table/get_prediction_table_data", methods=['GET'])
def get_prediction_table_data():
    # load and return updated json
    with open(os.path.join(working_dir['static_dir'], 'Dataset/prediction_histories.json')) as file:
        updated_json = json.load(file)

    try:
        return jsonify(
            {
                'response': updated_json,
                'status': '200 OK',
                'messages': 'success'
            }
        )
    except Exception as e:
        return jsonify(
            {
                'response': str(e),
                'status': '500 ERROR',
                'messages': 'An error has occured'
            }
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0")