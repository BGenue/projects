from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

from pymongo import MongoClient

#local서버용
client = MongoClient('localhost', 27017)

#배포용
#client = MongoClient('mongodb://test:test@localhost',27017)
db = client.scubapage


## HTML을 주는 부분
@app.route('/')
def home():
    return render_template('main.html', title="메인")

@app.route('/introduce')
def introduce():
    return render_template('introduce.html', title="강사 소개")

@app.route('/course')
def course():
    return render_template('course.html', title="교육 과정")

@app.route('/board')
def board():
    return render_template('board.html', title="질의 게시판")

@app.route('/photo')
def photo():
    return render_template('photo.html', title="다이비 사진")

@app.route('/plan')
def plan():
    return render_template('plan.html', title="다이빙 일정")


## API 역할을 하는 부분
# 게시판 글 저장해
@app.route('/community-form', methods=['POST'])
def write_community():
    community_name = request.form['name']
    community_password = request.form['password']
    community_text = request.form['text']
    community_secrete = request.form['secrete'];
    community_title = request.form['title'];
    community_id = request.form['id'];
    print(community_text)
    doc = {
        'community_name': community_name,
        'community_password': community_password,
        'community_text': community_text,
        'community_title': community_title,
        'community_secrete': community_secrete,
        'community_id': community_id
    }

    db.community.insert_one(doc)

    return jsonify({'result': 'success', 'msg': '게시판에 작성되었습니다.'})

#게시판 글 받아와
@app.route('/community-form', methods=['GET'])
def read_community():
    communities = list(db.community.find({}, {'_id': False}))

    return jsonify({'result': 'success', 'communities': communities})

#게시판 글 지워
@app.route('/community-form/del', methods=['POST'])
def delete_community():
    delete_id = request.form['id']
    delete = {
        'community_id': delete_id
    }
    db.community.delete_one(delete)

    return jsonify({'result': 'success', 'msg': '글이 삭제되었습니다.'})

#게시판 글 수정
@app.route('/community-form/fix', methods=['POST'])
def fix_community():
    fix_name = request.form['name']
    fix_password = request.form['password']
    fix_text = request.form['text']
    fix_secrete = request.form['secrete'];
    fix_title = request.form['title'];
    fix_id = request.form['id'];
    print(fix_name, fix_password, fix_text, fix_secrete, fix_title, fix_id)
    fix = {
        'community_name': fix_name,
        'community_password': fix_password,
        'community_text': fix_text,
        'community_title': fix_title,
        'community_secrete': fix_secrete,
        'community_id': fix_id,
    }

    db.community.update_one({'community_id': fix_id}, {'$set': fix})

    return jsonify({'result': 'success', 'msg': '글이 수정되었습니다.'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
