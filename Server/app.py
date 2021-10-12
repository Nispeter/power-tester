from flask import Flask, request, render_template, abort#, make_response , send_file
from flask_cors import CORS
#from werkzeug.exceptions import HTTPException
from ftplib import FTP
import subprocess, random#, os


app = Flask(__name__)

CORS(app)

def security_check(file_dir):
    return True;

@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")

'''@app.route('/image', methods=['GET'])
def image():
    return send_file("static/favicon.ico", mimetype="image/gif")'''

@app.route('/sendcode', methods=['POST'])
def cap_code():
    code = request.form['code']
    name = str(random.randint(0, 13458345324))
    name2 = name
    outputfile = "test/"+name+".out"
    name = "test/"+name+".cpp"
    f = open(name, "w", newline="\n")
    f.write(code)
    f.close()
    ftp = FTP(host='192.168.56.101', user='diego', passwd='holahola01k')  #Cambiar para utilizar lista de ips de esclavos. Red local, no es necesario proteger passwd
    ftp.cwd('Desktop')
    f = open(name, 'rb')
    ftp.storlines('STOR '+ name2 + '.cpp', f)
    ftp.quit()
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
    
    return '<h1>200 OK</h1>', 200