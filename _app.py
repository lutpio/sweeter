# from flask import Flask, render_template
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)

client = MongoClient(
    "mongodb+srv://ahmadlutfi606:wolfattax@cluster0.xctxali.mongodb.net/?retryWrites=true&w=majority"
)
db = client.dbsparta_11

SECRET_KEY = "SPARTA"


@app.route("/", methods=["GET"])
def home():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"id": payload["id"]})
        return render_template("index.html", nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Login token Expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="there was an issue logging your in"))


@app.route("/login", methods=["GET"])
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)


@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")


@app.route("/api/register", methods=["POST"])
def api_register():
    id_receive = request.form.get("id_give")
    pw_receive = request.form.get("pw_give")
    nickname_receive = request.form.get("nickname_give")
    # cek disini
    result = db.user.find_one({"id": id_receive})
    if result:
        return jsonify({"result": "exists", "msg": f"akun dengan ID {id_receive} sudah terdaftar"})
    else:
        # cek disini
        pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()
        db.user.insert_one({"id": id_receive, "pw": pw_hash, "nick": nickname_receive})
        return jsonify({"result": "success", "msg": "Berhasil daftar"})



@app.route("/api/login", methods=["POST"])
def api_login():
    id_receive = request.form.get("id_give")
    pw_receive = request.form.get("pw_give")
    pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()
    result = db.user.find_one({"id": id_receive, "pw": pw_hash})
    if result:
        payload = {
            "id": id_receive,
            "exp": datetime.utcnow() + timedelta(seconds=5),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=["HS256"])
        return jsonify({"result": "success", "token": token})

    else:
        return jsonify({"result": "fail", "msg": "id atau password salah"})


@app.route("/api/nick", methods=["GET"])
def api_valid():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"id": payload.get("id")}, {"_id": 0})
        return jsonify({"result": "success", "nickname": user_info.get("nick")})
    except jwt.ExpiredSignatureError:
        msg = "Login token Expired"
        return jsonify({"result": "fail", "msg": msg})
    except jwt.exceptions.DecodeError:
        msg = "there was an issue logging your in"
        return jsonify({"result": "fail", "msg": msg})


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
