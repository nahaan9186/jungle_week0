from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider

import json
import sys


app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.lookFace

#####################################################################################
# 이 부분은 코드를 건드리지 말고 그냥 두세요. 코드를 이해하지 못해도 상관없는 부분입니다.
#
# ObjectId 타입으로 되어있는 _id 필드는 Flask 의 jsonify 호출시 문제가 된다.
# 이를 처리하기 위해서 기본 JsonEncoder 가 아닌 custom encoder 를 사용한다.
# Custom encoder 는 다른 부분은 모두 기본 encoder 에 동작을 위임하고 ObjectId 타입만 직접 처리한다.
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


# 위에 정의되 custom encoder 를 사용하게끔 설정한다.
app.json = CustomJSONProvider(app)

# 여기까지 이해 못해도 그냥 넘어갈 코드입니다.
# #####################################################################################

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/sign', methods = ['POST'])
def sign_up():
    name_receive = request.form('give_name')
    img_receive = request.form('give_img')
    id_receive = request.form('give_id')
    password_receive = request.form('give_password')

    doc = { 'name' : name_receive, 'img' : img_receive, 'id' : id_receive, 'password' : password_receive}

    db.users.insert_one(doc)

    return jsonify({'result' : 'success'})

@app.route('/api/login', methods = ['POST'])
def login():
    login_id = request.form('give_id')
    login_password = request.form('give_password')
    registered_id = db.users.find_one({'id' : login_id })
    if not registered_id:
        return jsonify({'result': 'failure'})
    if registered_id:
        correct_password = db.users
        if

if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)
