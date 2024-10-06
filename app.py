import  config
from flask import Flask, request, render_template, redirect
from api import api
app = Flask(__name__)
app.register_blueprint(api)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    if request.cookies.get("token") != config.authToken:return redirect("/login")
    return render_template('generate.html')

# if config.development:
#     app.run(host='0.0.0.0', port=8787)