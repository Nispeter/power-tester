from flask import Flask, send_file, request, render_template
from flask_cors import CORS


app = Flask(__name__)

CORS(app)

@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@app.route('/image', methods=['GET'])
def image():
    return send_file(f"static/favicon.ico", mimetype="image/gif")

@app.route('/sendcode', methods=['POST'])
def cap_code():
    code = request.form['code']
    f = open("test/demofile.cpp", "w", newline="\n")
    f.write(code)
    f.close()
    return 'OK', 200