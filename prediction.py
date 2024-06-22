

import pandas as pd
import joblib
from flask import Flask, redirect, url_for, request, render_template

app = Flask(__name__)
#load index.html/ first page. receive input variable from user
@app.route("/")
def index():
	return render_template('index.html')

#load result.html. the result of prediction is presented here. 
@app.route('/result/', methods=["POST"])
def prediction_result():
    
    return render_template('result.html')

if __name__ == "__main__":
    #host= ip address, port = port number
    #app.run(host='127.0.0.1', port='5001')
    app.run()