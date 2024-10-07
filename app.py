import  config
from flask import Flask, request, render_template, redirect
from api import api

app = Flask(__name__)
app.register_blueprint(api)

@app.errorhandler(404)
def page_not_found(e):
      config.log(config.system())
      return render_template('error/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    config.log("Server Error: ", e)
    config.log(config.system())
    return render_template('error/500.html'), 500

@app.errorhandler(405)
def method_not_allowed(e):return render_template('error/405.html'), 405

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/validate")
def validate():
    return render_template('pages/validate.html')

@app.route('/generate')
def generate():
    if  not config.is_manager(request.cookies.get("token")): return redirect("/login")
    return render_template('pages/generate.html')

@app.route("/dashboard")
def admin():
    manage_perm = config.is_manager(request.cookies.get("token"))
    if  not manage_perm: return redirect("/login")
    return render_template('pages/dashboard.html', event=config.event, admin=manage_perm)


if config.development:
    app.run(host='0.0.0.0', port=8787)
