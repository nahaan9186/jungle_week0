from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider

import json
import sys
import random


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
    return render_template('login.html')

@app.route('/sign.html')
def sign_page():
    return render_template('sign.html')

@app.route('/gameStart.html')
def gamestrat_page():
    return render_template('gameStart.html')

@app.route('/game.html')
def game_page():
    return render_template('game.html')


@app.route('/api/sign', methods = ['GET','POST'])
def sign_up():
    name_receive = request.form.get('give_name')
    img_receive = request.form.get('give_img')
    id_receive = request.form.get('give_userId')
    registered_id = db.users.find_one({'id' : id_receive })
    if registered_id:
        return jsonify({'result': 'failure'})
    password_receive = request.form.get('give_password')

    doc = { 'name' : name_receive, 'img' : img_receive, 'id' : id_receive, 'password' : password_receive}

    db.users.insert_one(doc)

    return jsonify({'result' : 'success'})

@app.route('/api/login', methods = ['GET','POST'])
def login():
    login_id = request.form.get('give_id')
    login_password = request.form.get('give_password')
    registered_user = db.users.find_one({'id' : login_id })
    if not registered_user:
        return jsonify({'result': 'failure'})
    if registered_user['password'] == login_password:
        return jsonify({'result' : 'success'})
    else:
        return jsonify({'result': 'failure'})
    
@app.route('/api/list', methods = ['GET'])
def addProblem():
    mateList = list(db.users.find({}))
    imgList = [user['img'] for user in mateList]  # 사용자 이미지만 추출
    print('이미지 리스트 :', imgList)
    return render_template('game.html', imgList=imgList)

if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)
