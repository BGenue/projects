from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

from pymongo import MongoClient

import os

# local서버용
client = MongoClient('localhost', 27017)

# 배포용
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


@app.route('/photo-list')
def photo_list():
    path = "./static/diving"
    photo_list = os.listdir(path)

    list = {'photo_list': photo_list}
    return list;


@app.route('/schedule')
def schedule():
    return render_template('schedule.html', title="다이빙 일정")


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


# 게시판 글 받아와
@app.route('/community-form', methods=['GET'])
def read_community():
    communities = list(db.community.find({}, {'_id': False}))

    return jsonify({'result': 'success', 'communities': communities})


# 게시판 글 지워
@app.route('/community-form/del', methods=['POST'])
def delete_community():
    delete_id = request.form['id']
    delete = {
        'community_id': delete_id
    }
    db.community.delete_one(delete)

    return jsonify({'result': 'success', 'msg': '글이 삭제되었습니다.'})


# 게시판 글 수정
@app.route('/community-form/fix', methods=['POST'])
def fix_community():
    fix_name = request.form['name']
    fix_password = request.form['password']
    fix_text = request.form['text']
    fix_secrete = request.form['secrete'];
    fix_title = request.form['title'];
    fix_id = request.form['id'];

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


# 일정 저장해
@app.route('/schedule/save-schedule', methods=['POST'])
def save_schedule():
    start_year = request.form['start_year']
    start_month = request.form['start_month']
    start_date = request.form['start_date']
    end_year = request.form['end_year']
    end_month = request.form['end_month']
    end_date = request.form['end_date']
    title = request.form['title']

    doc = {
        'start_year': start_year,
        'start_month': start_month,
        'start_date': start_date,
        'end_year': end_year,
        'end_month': end_month,
        'end_date': end_date,
        'title': title
    }

    db.schedule.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '일정이 추가되었습니다'})


# 일정 가져와
@app.route('/schedule/get-schedule', methods=['GET'])
def read_schedule():
    print("일정 가져와")
    year = request.args['year']
    month = request.args['month']
    bound = 14
    print(year, month)
    next_year = str(int(year) + 1)
    next_month = str(int(month) + 1)
    prev_year = str(int(year) - 1)
    prev_month = str(int(month) - 1)

    if next_month == "13":
        next_month = "1"
    if prev_month == "0":
        prev_month = "12"

    print(year, month, next_year, next_month, prev_year, prev_month)

    schedule = list(db.schedule.find({"$or": [{"$and": [{"start_year": year}, {"start_month": month}]},
                                              {"$and": [{"end_year": year}, {"end_month": month}]}]}, {'_id': False}))
    # # 쿼리
    # if month == 1:
    #     schedule = list(db.schedule.find({"$and": [{"start_year": prev_year}, {"end_year": year}, {"start_month": prev_month}, {"end_month": month}]}, {'_id': False}))
    # elif month == 12:
    #     schedule = list(db.schedule.find({"$and": [{"start_year": year}, {"end_year": next_year}, {"start_month": month}, {"end_month": next_month}]}, {'_id': False}))
    # else:
    #     schedule = list(db.schedule.find({"$or": [{"$and": [{"start_year": year}, {"end_year": year}, {"start_month": month}, {"end_month": month}]},
    #                                               {"$and": [{"start_year": year}, {"end_year": year}, {"start_month": month}, {"end_month": next_month}]},
    #                                               {"$and": [{"start_year": year}, {"end_year": year}, {"start_month": prev_month}, {"end_month": month}]},
    #                                               {"$and": [{"start_year": year}, {"end_year": year}, {"start_month": next_month}, {"end_month": next_month}]},
    #                                               {"$and": [{"start_year": year}, {"end_year": year}, {"start_month": prev_month}, {"end_month": prev_month}]}]}, {'_id': False}));
    # schedule = list(db.schedule.find({"$expr": {"$cond": {
    #                                                         "if": {"$eq": [month, 1]},
    #                                                         "then": {"$and": [{"start_year": prev_year}, {"end_year": year}, {"start_month": prev_month}, {"end_month": month}]},
    #                                                         "else": {
    #                                                             "if": {"$eq": [month, 12]},
    #                                                             "then": {"$and": [{"start_year": year}, {"end_year": next_year}, {"start_month": month}, {"end_month": next_month}]}
    #                                                         }}}}, {'_id': False}))

    # {"$and": [
    #     {"$or": [
    #         {"$expr": {"$cond": {
    #             "if": month == 1,
    #             "then": {"$and": [{"start_year": prev_year}, {"end_year": year}, {"start_month": prev_month}, {"end_month": month}]},
    #             "else": {
    #                 "if": month == 12,
    #                 "then": {"$and": [{"start_year": year}, {"end_year": next_year}, {"start_month": month}, {"end_month": next_month}]}
    #             }}}}
    #     ]
    #     }
    # ]}


    # {"$and": [{"start_year": year}, {"end_year": year}, {"start_month": month}, {"end_month": month}]},  # 현재 달 내의 일정을 가져와
    # "$and": [{"start_year": year}, {"end_year": year}, {"start_month": month}, {"end_month": month}]
    # {"$and": [{"start_year": year}, {"start_month": str(int(month) + 1)}, {"start_date": {"$lte": 14}}]}  # 현재달 앞뒤 남는칸에 보여질 녀석들을 가져와
    for i in schedule:
        print(i)
    return jsonify({'result': 'success', 'schedule': schedule})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
