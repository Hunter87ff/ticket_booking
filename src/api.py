from flask import Blueprint, request, redirect, render_template, Response
import config, datetime


api = Blueprint('api', __name__)


# authentication decorator



@api.route('/api/gen', methods=['POST'])
def gen():
    if not config.authorised(): return redirect("/login")
    data = request.form.to_dict()
    ticket = config.Ticket(data).save()
    return redirect(f'/ticket/{ticket.token}')


@api.route('/ticke2/<token>')
def ticket(token:str):
    # sanitize token
    doc = dict(config.tokendb.find_one({"token": token}) or {})
    if not doc or doc.get("status")=="used": return render_template("error/invalidTicket.html", err=doc.get("status") or "invalid")
    if config.authorised() and str(datetime.datetime.date(datetime.datetime.now())) == config.event_date: 
        config.event.update_ticket(token, "used")
    return render_template('pages/ticket.html', token=token)


@api.route("/ticket/<token>")
def tickets(token:str):
    doc = dict(config.tokendb.find_one({"token": token}) or {})
    if not doc or doc.get("status")=="used": return render_template("error/invalidTicket.html", err=doc.get("status") or "invalid")
    if config.authorised() and str(datetime.datetime.date(datetime.datetime.now())) == config.event_date: 
        config.event.update_ticket(token, "used")
    return render_template('pages/ticket2.html', doc=doc)


@api.route("/api/update_date")
def update_date():
    if config.authorised():
        try:
            date = request.args.get("date")
            print("Date: ", date)
            config.event_date(date)
            config.event._date = date
            return {"status": "success", "date": date}, 200
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500
        
    return {"status": "error", "message": "Unauthorized"}, 401


@api.route("/api/delete_ticket/<token>")
def delete_ticket(token:str=None):
        if not token:return {"status": "error", "message": "Invalid token"}, 400
        if config.authorised():
            config.tokendb.delete_one({"token": token})
            return {"status": "success"}, 200
        return {"status": "error", "message": "Unauthorized"}, 401




@api.route("/login", methods=["GET", "POST"])
def login():
    if config.authorised():return redirect("/dashboard")
    if request.method == "POST":
        data = request.form.to_dict() or {"email":"", "password":""}
        user = dict(config.userdb.find_one(data) or {})
        if user:
            resp = Response("<script>document.location.href=`${document.location.origin}/dashboard`</script>")
            resp.set_cookie("token", user.get("token"), expires=datetime.datetime.now() + datetime.timedelta(days=30))
            return resp
        return render_template("pages/login.html", err="Invalid credentials")

    return render_template("pages/login.html")