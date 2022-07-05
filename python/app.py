from flask import Flask, request
import os
from datetime import timedelta
from text_password_protect import TextPasswordProtect
import redis
import uuid

app = Flask(__name__)

# Make sure to set the same SALT on all nodes, otherwise this is going to
# get wild
tpp = TextPasswordProtect()

r = redis.Redis(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 6379),
    password=os.getenv("DB_PASSWORD", None),
    # set to false in local dev
    ssl=os.getenv("DB_SSL", "True") == "True",
)


@app.route("/secrets", methods=["POST"])
def create_secret():
    print("here")
    content = request.get_json()
    if (
        content is None
        or all(key in content for key in ("passphrase", "message")) is not True
    ):
        return {"success": "False", "message": "Missing passphrase and/or message"}, 400
    passphrase = content["passphrase"]
    message = content["message"]
    if "expiration_time" in content:
        expiration_time = content["expiration_time"]
        if isinstance(expiration_time, int) is True:
            expiration_time = content["expiration_time"]
        else:
            if content["expiration_time"].isdigit():
                expiration_time = int(content["expiration_time"])
    else:
        expiration_time = 604800

    # create a unique id
    id = uuid.uuid4().hex

    # sha the password for safe storage
    sha = tpp.sha256hex(passphrase)

    # encrypt the message
    ciphertext = tpp.encrypt(message, passphrase)

    print("before redis")
    r.setex(
        id,
        timedelta(seconds=expiration_time),
        "{0}\n{1}".format(sha, ciphertext.decode("utf-8")),
    )
    return {"success": "True", "id": id}


@app.route("/secrets/<id>", methods=["POST"])
def get_secret(id):

    content = request.get_json()
    if "passphrase" not in content:
        return {"success": "False", "message": "Missing passphrase"}, 400
    passphrase = content["passphrase"]

    data = r.get(id)
    if data is None:
        return {
            "success": "False",
            "message": "This secret either never existed or it was already read",
        }, 404

    data = data.decode("utf-8")
    stored_sha, stored_ciphertext = data.split("\n")

    # sha the password for comparison
    sha = tpp.sha256hex(passphrase)

    if stored_sha != sha:
        return {
            "success": "False",
            "message": "This secret either never existed or it was already read",
        }

    r.delete(id)
    # If this doesn't return a value we say secret has either
    # never existed or it was already read
    plaintext = tpp.decrypt(stored_ciphertext.encode("utf-8"), passphrase)

    return {"success": "True", "message": plaintext}