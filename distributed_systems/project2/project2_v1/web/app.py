from subprocess import call,Popen,PIPE,run
from flask import Flask, render_template, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cnf1miou0vdt9d1qe8sx164zejp3fnay'


# Basic flask call to start web app
@app.route("/", methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        code = request.form['codespace']
        print("code: " + code)
        f = open('program.py', 'w')
        f.write(code)
        f.close()
        f = open('program.py', 'r')
        code = f.read()
        call("docker build -t dc_flask:latest .")
        call("docker run -d -p 5000:5000 dc_flask:latest")
        pid = Popen("docker container ps -a -l -q", stdout=PIPE).communicate()[0].decode('utf-8')
        cmd = "docker container logs " + pid
        cmd = cmd.rstrip()
        print(cmd)
        logs = Popen(cmd, stdout=PIPE).communicate()[0].decode('utf-8')
        return render_template("result.html", codespace=code, result=logs)
    else:
        return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')