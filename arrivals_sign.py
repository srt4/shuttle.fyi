from flask import Flask, session, render_template
from arrivals_provider import ArrivalsProvider
import os


app = Flask(__name__)
app.secret_key = 'A0zR98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def get_arrivals():
    return render_template('main.html', arrivals_provider=ArrivalsProvider())

if __name__ == '__main__':
    app.run(debug=True)
