from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request, make_response
from flask.json.provider import JSONProvider

import json
import sys

import jwt
import datetime


app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.lookFace

all_user = list(db.users.find({}))

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

app.config['SECRET_KEY'] = 'user_secret_key'

app.route('/check_cookie')
def check_cookie():
    jwt_token = request.cookies.get('jwt_token')
    if jwt_token:
        return f"JWT 토큰이 쿠키게 저장되어 있습니다: (jwt_token)"
    else:
        return "쿠키에 JWT 토큰이 저장되어 있지 않습니다."

@app.route('/index.html')
def base():
    return render_template('index.html')

@app.route('/')
def login_page():
    title = '로그인 페이지'
    return render_template('login.html', title=title)

@app.route('/game.html')
def game_page():
    title = '게임 페이지'
    return render_template('game.html', title=title)

@app.route('/gameStart.html')
def gameStart_page():
    title = '게임 페이지'
    return render_template('gameStart.html', title=title)

# 랭킹 페이지 화면 랜더링
@app.route('/ranking.html')
def ranking_page():
    title = '랭킹 페이지'
    return render_template('ranking.html', title=title)

# 랭킹 API 역할을 하는 부분
@app.route('/api/ranking', methods = ['POST'])
def ranking():
    score_receive = request.form.get('give_score')
    
    db.users.update_one({'score': score_receive})
    
    return jsonify({'result': 'success'})

# 랭킹 API 역할을 하는 부분
@app.route('/api/ranking', methods = ['GET'])
def show_score():
    score = list(db.users.find({}, {'_id':False}, {'password':False}, {'id':False}.sort('score',-1)))
    return jsonify({'result': 'success', 'score_list':score})
    

# 회원가입 화면 보여주기
@app.route('/sign.html')
def sign_page():
    title = '회원가입 페이지'
    return render_template('sign.html', title=title)

# 회원가입 API 역할을 하는 부분
@app.route('/api/sign', methods = ['POST'])
def sign_up():
    name_receive = request.form.get('give_name')
    img_receive = request.form.get('give_img')
    id_receive = request.form.get('give_userId')
    password_receive = request.form.get('give_password')
    
    # 미기입 항목 확인
    if (name_receive == '') or (img_receive == '') or (id_receive == '') or (password_receive == ''):
        return jsonify({'result': 'itemMissing'})
    
    # 중복된 ID 확인
    registered_id = db.users.find_one({'_id' : id_receive})
    if registered_id:
        return jsonify({'result': 'duplication'})

    doc = { '_id' : id_receive, 'name' : name_receive, 'img' : img_receive, 'score' : 0, 'password' : password_receive}

    db.users.insert_one(doc)
    
    
    # 회원가입이 성공하면 JWT 토큰 생성
    token = jwt.encode({'password': password_receive, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm='HS256')
    
    # 토큰을 쿠키에 저장
    response = make_response(jsonify({'result': 'success'}))
    response.set_cookie('jwt_token', token)

    return response

    # return jsonify({'result': 'success'})
    

@app.route('/login.html', methods = ['GET','POST'])
def login():
    login_id = request.form.get('give_id')
    login_password = request.form.get('give_password')
    registered_user = db.users.find_one({'_id' : login_id })
    if not registered_user:
        return jsonify({'result': 'failure'})
    if registered_user['password'] == login_password:
        return jsonify({'result' : 'success'})
    else:
        return jsonify({'result': 'failure'})
 
@app.route('/api/list', methods = ['GET'])
def addProblem():
    mateList = list(db.users.find({}))
    return jsonify({'result' : 'success', 'mateList' : mateList})
 
if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)
