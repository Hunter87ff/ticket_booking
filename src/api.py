from flask import Blueprint, request, redirect, render_template, Response
import config, datetime


api = Blueprint('api', __name__)




@api.route('/api/gen', methods=['POST'])
def gen():
    if not config.authorised(): return redirect("/login")
    data = request.form.to_dict()
    ticket = config.Ticket(data).save()
    config.log(f"New ticket generated: {ticket.token} | {config.get_ip(request)}")
    return  redirect(f"/api/ticket/preview/{ticket.token}")   #redirect(f'/ticket/{ticket.token}')


@api.route("/ticket/<token>")
def tickets(token:str):
    doc = dict(config.tokendb.find_one({"token": token}) or {})
    if not doc or doc.get("status")=="used": 
        return render_template("error/invalidTicket.html", err=doc.get("status") or "invalid")
    if config.authorised() and str(datetime.datetime.date(datetime.datetime.now())) == config.event_date(): 
        config.event.update_ticket(token, "used")
        config.log(f"Ticket used: {token} | {config.get_ip(request)}")
    return render_template('pages/ticket2.html', doc=doc)


@api.route("/api/ticket/preview/<token>")
def preview_ticket(token:str):
    doc = dict(config.tokendb.find_one({"token": token}) or {})
    if not doc or doc.get("status")=="used": return render_template("error/invalidTicket.html", err=doc.get("status") or "invalid")
    return render_template('pages/ticket2.html', doc=doc)


@api.route("/api/update_date")
def update_date():
    if config.authorised():
        try:
            date = request.args.get("date")
            config.event_date(date)
            config.event._date = date
            config.log(f"Event date updated to : {date}  | {config.get_ip(request)}")
            return {"status": "success", "date": date}, 200
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500
        
    return {"status": "error", "message": "Unauthorized"}, 401


@api.route("/api/delete_ticket/<token>")
def delete_ticket(token:str=None):
        if not token:return {"status": "error", "message": "Invalid token"}, 400
        if config.authorised():
            config.tokendb.delete_one({"token": token})
            config.log(f"Ticket deleted: {token} | {config.get_ip(request)}")
            return {"status": "success"}, 200
        return {"status": "error", "message": "Unauthorized"}, 401

# TODO : Ticket Transfer


@api.route("/login", methods=["GET", "POST"])
def login():
    if config.authorised():return redirect("/dashboard")
    if request.method == "POST":
        data = request.form.to_dict() or {"email":"", "password":""}
        user = dict(config.userdb.find_one(data) or {})
        if user:
            resp = Response("<script>document.location.href=`${document.location.origin}/dashboard`</script>")
            resp.set_cookie("token", user.get("token"), expires=datetime.datetime.now() + datetime.timedelta(days=30))
            # Log new user's IP
            config.log(f"New login: {config.get_ip(request)}")
            return resp
        return render_template("pages/login.html", err="Invalid credentials")

    return render_template("pages/login.html")
