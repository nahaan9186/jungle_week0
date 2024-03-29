from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request, make_response, session
from flask.json.provider import JSONProvider

import json
import sys

import jwt
import datetime

import random


app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.lookFace

# 세션에 사용될 시크릿 키 설정
app.secret_key = 'user_secret_key'

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

@app.route('/sign.html')
def sign_page():
    title = '회원가입 페이지'
    return render_template('sign.html', title=title)

@app.route('/ranking.html')
def rank_page():
    title = '랭킹 페이지'
    return render_template('ranking.html', title = title)

@app.route('/api/sign', methods = ['GET','POST'])
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
    

@app.route('/api/login', methods = ['GET','POST'])
def login():
    login_id = request.form.get('give_id')
    login_password = request.form.get('give_password')
    registered_user = db.users.find_one({'_id' : login_id })
    if not registered_user:
        return jsonify({'result': 'failure'})
    if registered_user['password'] == login_password:
        # 로그인에 성공하면 세션에 사용자 정보 저장
        session['user'] = registered_user
        # print('session : ', session)
        return jsonify({'result' : 'success'})
    else:
        return jsonify({'result': 'failure'})
    
@app.route('/logout')
def logout():
    # 세션에서 사용자 정보 삭제
    session.pop('user', None)
    print('로그아웃!')
    return jsonify({'result': 'success'})
 
@app.route('/api/list', methods = ['GET'])
def addProblem():
    mateList = list(db.users.find({}))
    return jsonify({'result' : 'success', 'mateList' : mateList})

@app.route('/api/rank', methods = ['POST'])
def addScore():
    receive_score = request.form.get('give_score')
    # 세션에서 현재 로그인한 사용자 정보 가져오기
    current_user = session.get('user')

    # 사용자 정보가 세션에 있는지 확인하고, 있으면 해당 사용자의 score를 업데이트
    if current_user:
        db.users.update_one({'_id': current_user['_id']}, {'$set': {'score': receive_score}})
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure', 'message': '유저 정보를 찾을 수 없습니다.'})

    
@app.route('/api/ranking', methods=['GET'])
def show_score():
    # 사용자 정보를 가져와서 점수순으로 정렬
    users = list(db.users.find().sort([('score', -1)]))
    # 필요한 정보만 추출하여 리스트에 저장
    score_list = []
    for user in users:
        if 'score' in user:
            score_list.append({'name': user['name'], 'score': user['score']})
        else:
            # score 필드가 없는 경우에 대한 처리
            score_list.append({'name': user['name'], 'score': 0})  # 또는 다른 기본값 설정
    return jsonify({'result': 'success', 'score_list': score_list})  
 
if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)
