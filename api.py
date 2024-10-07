from flask import Blueprint, request, redirect, render_template, Response
import config, datetime


api = Blueprint('api', __name__)

@api.route('/api/gen', methods=['POST'])
def gen():
    if not config.is_manager(request.cookies.get("token")): return redirect("/login")
    data = request.form.to_dict()
    ticket = config.Ticket(data)
    ticket.save()
    return redirect(f'/ticket/{ticket.token}')


@api.route('/ticket/<token>')
def ticket(token:str):
    # sanitize token
    doc = dict(config.tokendb.find_one({"token": token}) or {})
    if not doc or doc.get("status")=="used": return render_template("error/invalidTicket.html", err=doc.get("status") or "invalid")
    if config.is_manager(request.cookies.get("token")) and str(datetime.datetime.date(datetime.datetime.now())) == config.event_date: config.tokendb.update_one({"token": token}, {"$set": {"status": "used"}})
    return render_template('ticket.html', token=token)


@api.route("/login", methods=["GET", "POST"])
def login():
    if config.is_manager(request.cookies.get("token")):return redirect("/generate")
    if request.method == "POST":
            data = request.form.to_dict() or {}
            if config.userdb.find_one(data):
                resp = Response("<script>document.location.href=`${document.location.origin}/generate`</script>")
                resp.set_cookie("token", config.authToken)
                return resp
    return render_template("login.html")