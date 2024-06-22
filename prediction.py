

import pandas as pd
import joblib
from flask import Flask, redirect, url_for, request, render_template, jsonify

app = Flask(__name__)
#load index.html/ first page. receive input variable from user
@app.route("/")
def index():
    df = pd.read_csv('data.csv')
    
    # Convert data to list for Chart.js
    dates = df['DATE'].tolist()
    prices_idr = df['IDR'].tolist()

    return render_template('index.html', dates=dates, prices_idr=prices_idr )

@app.route('/data')
def data():
    # Load data from Excel file
    df = pd.read_csv('data.csv')
    # Prepare data for JSON response
    data = {
        'dates': df['Date'].tolist(),
        'prices_idr' : df['IDR'].tolist()
    }
    return jsonify(data)

#load result.html. the result of prediction is presented here. 
@app.route('/result/', methods=["POST"])
def prediction_result():
    
    return render_template('result.html')

if __name__ == "__main__":
    app.run()