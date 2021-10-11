from flask import Flask, send_from_directory, make_response
from flask import url_for, jsonify, render_template, request, redirect
import os
import pandas as pd 
import numpy as np
import copy
import json 
import uuid
import glob 
import time 


#====================================================
app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')


@app.route('/simulator', methods=['GET', 'POST'])
def simulator():
    return render_template('simulator.html', content = {})

@app.route('/editor', methods=['GET', 'POST'])
def editor():
    return render_template('jscut.html', content = {})    


if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0")

