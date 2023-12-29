from flask import Flask, render_template, request, redirect
import pandas as pd
from pathlib import Path
from datetime import datetime
import amznMissingApp as missing
from pathlib import Path
from flaskwebgui import FlaskUI

app = Flask(__name__)

ui = FlaskUI(app=app, server="flask", width=700, height=700) 

@app.route('/')
def root():
    return render_template('homePage.html', fill='')




@app.route('/data', methods = ['GET','POST'])
def data(): 
    global df
    try:
        if request.method == 'POST':

            if request.form.get('action') == 'Submit':
                form_data = request.form
                
                startDate,endDate = form_data['StartDate'], form_data['EndDate']
                
                
                #get df
                df = missing.GetMissingMain(startDate,endDate)
                num_items_found = df.shape[0]

                return render_template('foundPage.html', numItems=num_items_found) #titles=df.columns.values,tables=[df.to_html(classes='data')]
            
            
            if request.form.get('action')=='Download':
                date = datetime.today().strftime('%Y-%m-%d-%S')
                downloads_path = downloads_path = str(Path.home() / 'Downloads')
                df.to_csv(f'{downloads_path}\\amznMissing{date}.csv')

                return '', 204
            
    except Exception as e:
        # e holds description of the error
        error_text = '<p>/data - The error:<br>' + str(e) + '</p>'
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text



#Navigate to folder
#activate (conda) env
#run command to bundle
#pyinstaller -w -F --add-data "templates;templates" --add-data "static;static" main.py


if __name__ == '__main__':
    ui.run()