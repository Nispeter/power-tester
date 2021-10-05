from flask import Flask, send_file, request, render_template, abort, make_response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import os, subprocess, random


app = Flask(__name__)

CORS(app)

def security_check(file_dir):
    return True;

@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@app.route('/image', methods=['GET'])
def image():
    return send_file("static/favicon.ico", mimetype="image/gif")

@app.route('/sendcode', methods=['POST'])
def cap_code():
    code = request.form['code']
    name = str(random.randint(0, 13458345324))
    outputfile = "test/"+name+".out"
    name = "test/"+name+".cpp"
    f = open(name, "w", newline="\n")
    f.write(code)
    f.close()
    if not security_check: 
        abort(409)
    new_compile = subprocess.Popen(["g++", name, "-o", outputfile], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    try:
        new_compile.wait(timeout=15)
    except TimeoutExpired:
        new_compile.kill()
    outputfile = "./" + outputfile
    new_execute = subprocess.Popen([outputfile], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    try:
        output, outerr = new_execute.communicate(timeout=15)
    except TimeoutExpired:
        new_execute.kill()
        output, outerr = new_execute.communicate()
    print(output)
    return '<h1>200 OK</h1>', 200