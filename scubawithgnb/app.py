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
    return render_template('index.html')


## API 역할을 하는 부분
# 게시판 글 저장해
@app.route('/community-form', methods=['POST'])
def write_community():
    community_name = request.form['name']
    community_password = request.form['password']
    community_text = request.form['text']
    community_noshow = request.form['noshow'];
    community_title = request.form['title'];
    print(community_text)
    doc = {
        'community_name': community_name,
        'community_password': community_password,
        'community_text': community_text,
        'community_title': community_title,
        'community_noshow': community_noshow
    }

    db.community.insert_one(doc)

    return jsonify({'result': 'success', 'msg': '게시판에 작성되었습니다.'})

#게시판 글 받아와
@app.route('/community-form', methods=['GET'])
def read_community():
    communities = list(db.community.find({}, {'_id': False}))

    return jsonify({'result': 'success', 'communities': communities})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
