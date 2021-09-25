from flask import Flask, send_file
from flask_cors import CORS


app = Flask(__name__)

CORS(app)

@app.route('/', methods=['GET'])
def home():
    return( "Hello, world!")

@app.route('/image', methods=['GET'])
def image():
    return send_file(f"static/favicon.ico", mimetype="image/gif")