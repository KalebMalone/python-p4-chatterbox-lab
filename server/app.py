from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=["GET", "POST"])
def messages():
    try:
        if request.method == "GET":
            messages = Message.query.all()
            return make_response(jsonify([message_obj.to_dict() for message_obj in messages]), 200)
        else:
            data = request.get_json()
            new_message = Message(
                body=data.get("body", "default text"), 
                username=data.get("username")
            )
            db.session.add(new_message)
            db.session.commit()
            return make_response(jsonify(new_message.to_dict()), 201)
    except Exception as e:
        return make_response({"error": str(e)}, 400)

@app.route('/messages/<int:id>', methods=["GET", "PATCH", "DELETE"])
def messages_by_id(id):
    try:
        message = db.session.get(Message, id)
        if not message:
            return make_response({"error": "Message not found"}, 404)

        if request.method == "GET":
            return make_response(jsonify(message.to_dict()), 200)

        if request.method == "PATCH":
            data = request.get_json()
            message.body = data.get("body", message.body)
            message.username = data.get("username", message.username)
            db.session.commit()
            return make_response(jsonify(message.to_dict()), 200)

        if request.method == "DELETE":
            db.session.delete(message)
            db.session.commit()
            return make_response(jsonify(message.to_dict()), 200)

    except Exception as e:
        return make_response({"error": str(e)}, 400)

if __name__ == '__main__':
    app.run(port=5555)
