import random, string
from flask import Flask, request, render_template, redirect
from gevent.pywsgi import WSGIServer


app = Flask(__name__)

tokens = []
def get_token():
    token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    if token not in tokens:
        tokens.append(token)
        return token
    return get_token()
    
print(get_token())


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    token = get_token()
    return render_template('generate.html', token=token)

@app.route('/api/gen', methods=['POST'])
def gen():
    data = request.form.to_dict()
    print(data)
    token = get_token()
    return redirect(f'/ticket/{token}')


@app.route('/ticket/<token>')
def ticket(token:str):
    # sanitize token
    token = token.strip().lower()
    if token not in tokens: return render_template("error/invalidTicket.html")
    return render_template('ticket.html', token=token)

http_server = WSGIServer(('', 8787), app)
http_server.serve_forever()
# app.run(host='0.0.0.0', port=8787)

