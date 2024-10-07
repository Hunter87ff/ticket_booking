from flask import Blueprint, request, redirect, render_template, Response
import config, datetime


api = Blueprint('api', __name__)

@api.route('/api/gen', methods=['POST'])
def gen():
    if not config.is_manager(request.cookies.get("token")): return redirect("/login")
    data = request.form.to_dict()
    ticket = config.Ticket(data).save()
    return redirect(f'/ticket/{ticket.token}')


@api.route('/ticket/<token>')
def ticket(token:str):
    # sanitize token
    doc = dict(config.tokendb.find_one({"token": token}) or {})
    if not doc or doc.get("status")=="used": return render_template("error/invalidTicket.html", err=doc.get("status") or "invalid")
    if config.is_manager(request.cookies.get("token")) and str(datetime.datetime.date(datetime.datetime.now())) == config.event_date: config.tokendb.update_one({"token": token}, {"$set": {"status": "used"}})
    return render_template('pages/ticket.html', token=token)

@api.route("/api/update_date")
def update_date():
    if config.is_manager(request.cookies.get("token")):
        config.event_date = request.args.get("date")
        return {"status": "success", "date": config.event_date}
    return {"status": "error", "message": "Unauthorized"}


@api.route("/login", methods=["GET", "POST"])
def login():
    # refered page
    refered_page = request.headers.get("Referer")
    print(refered_page)
    if config.is_manager(request.cookies.get("token")):return redirect("/dashboard")
    if request.method == "POST":
        data = request.form.to_dict() or {"email":"", "password":""}
        user = dict(config.userdb.find_one(data) or {})
        if user:
            resp = Response("<script>document.location.href=`${document.location.origin}/dashboard`</script>")
            resp.set_cookie("token", user.get("token"), expires=datetime.datetime.now() + datetime.timedelta(days=30))
            return resp
        return render_template("pages/login.html", err="Invalid credentials")

    return render_template("pages/login.html")