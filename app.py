from bson import ObjectId
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider
import json
import sys
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

# MongoDB setup
client = MongoClient('localhost', 27017)
db = client.lookFace

# Custom JSON encoder to handle ObjectId
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)

app.json = CustomJSONProvider(app)

# Secret key for JWT encoding/decoding
app.config['SECRET_KEY'] = 'your_secret_key'

# Function to generate JWT token
def generate_token(user_id):
    payload = {
        'user_id': str(user_id),
        'exp': datetime.utcnow() + timedelta(days=1)  # Token expiration time
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

@app.route('/')
def home():
    return render_template('index.html')

# Route for user sign up
@app.route('/api/sign', methods=['POST'])
def sign_up():
    name_receive = request.form.get('give_name')
    img_receive = request.form.get('give_img')
    id_receive = request.form.get('give_id')
    password_receive = request.form.get('give_password')

    doc = {'name': name_receive, 'img': img_receive, 'id': id_receive, 'password': password_receive}
    db.users.insert_one(doc)

    return jsonify({'result': 'success'})

# Route for user login
@app.route('/api/login', methods=['POST'])
def login():
    login_id = request.form.get('give_id')
    login_password = request.form.get('give_password')
    registered_user = db.users.find_one({'id': login_id, 'password': login_password})
    
    if not registered_user:
        return jsonify({'result': 'failure', 'message': 'Invalid username or password'})

    # Generate JWT token upon successful login
    token = generate_token(registered_user['_id'])

    return jsonify({'result': 'success', 'token': token.decode('utf-8')})

if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)
