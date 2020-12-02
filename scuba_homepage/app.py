from flask import Flask, render_template, jsonify, request, json

app = Flask(__name__)

from pymongo import MongoClient

import os

from PIL import Image
from PIL.ExifTags import TAGS
import datetime

from operator import itemgetter, attrgetter

# local서버용
# client = MongoClient('localhost', 27017)

# 배포용
client = MongoClient('mongodb://test:test@localhost',27017)

db = client.scuba


## HTML을 주는 부분
@app.route('/')
def home():
    # 가장 최근 사진 10장 가져오게 할거야
    path = "./static/diving"
    photo_list = os.listdir(path)

    list = {'photo_list': photo_list}

    return render_template('/index.html', title="메인", images=list)


@app.route('/introduce')
def introduce():
    path = "./static/me.jpg"
    image = {'image': path}
    return render_template('/introduce.html', title="강사 소개", image=image)


@app.route('/course')
def course():
    return render_template('/course.html', title="과정 소개")


@app.route('/askboard')
def askboard():
    return render_template('/askboard.html', title="문의 게시판")


# 게시판 글 저장해
@app.route('/askboard-form', methods=['POST'])
def write_askboard():
    writer = request.form['writer'];
    password = request.form['password'];
    content = request.form['content'];
    secret = request.form['secret'];
    title = request.form['title'];
    id = request.form['id'];
    write_date = request.form['write_date'];

    article = {
        '_id': id,
        'writer': writer,
        'password': password,
        'content': content,
        'secret': secret,
        'title': title,
        'write_date': write_date
    }

    db.articles.insert_one(article);

    return jsonify({'result': 'success', 'msg': '게시판에 작성되었습니다.'})


# 게시글 수정해
@app.route('/askboard-form/fix', methods=['POST'])
def fix_askboard():
    writer = request.form['writer']
    password = request.form['password']
    content = request.form['content']
    secret = request.form['secret'];
    title = request.form['title'];
    id = request.form['id'];

    fix = {
        'writer': writer,
        'password': password,
        'content': content,
        'title': title,
        'secret': secret,
    }

    db.articles.update_one({'_id': id}, {'$set': fix})

    return jsonify({'result': 'success', 'msg': '글이 수정되었습니다.'})


# 게시글 삭제해
@app.route('/askboard-form/delete', methods=['POST'])
def delete_askboard():
    id = request.form['id']

    delete = {
        '_id': id
    }

    db.articles.delete_one(delete)

    return jsonify({'result': 'success', 'msg': '글이 삭제되었습니다.'})


# 게시판 글 받아와
@app.route('/askboard-form', methods=['GET'])
def read_askboard():
    articles = list(db.articles.find({}))

    return jsonify({'result': 'success', 'articles': articles})


# 맨처음 12장씩 가져와
@app.route('/gallery')
def gallery():
    path = "./static/diving/"
    photo_list = os.listdir(path)
    print(len(photo_list))

    page = len(photo_list) // 12
    if (len(photo_list) % 12 > 0):
        page += 1
    photo_list = photo_list[0:12]

    photo_list = photo_date(photo_list, path)

    return render_template('/gallery.html', title="갤러리", photo_list=photo_list, page={'page': page})


# 페이지 바뀔때마다 사진 가져와
@app.route('/gallery', methods=['POST'])
def gallery_page():
    page = int(request.form['page'])
    path = "./static/diving/"
    photo_list = os.listdir(path)
    photo_list = photo_list[0 + 12 * (page - 1): 12 * page]
    photo_list = photo_date(photo_list, path)

    return jsonify({'result': 'success', 'photos': photo_list})


@app.route('/schedule')
def schedule():
    today = datetime.datetime.today()
    print(today.year, today.month)
    cond = str(today.year) + "-" + str(today.month)
    print(cond)
    schedules = list(db.schedule.find({"$or": [{"start": {"$regex": cond + "/*"}},
                                               {"end": {"$regex": cond + "/*"}}]}))
    return render_template('/schedule.html', schedules=schedules, shcetitle="다이빙 일정")

# 게시판 글 받아와
@app.route('/schedule/get-schedule', methods=['GET'])
def find_schedule():
    print("find")
    year = request.args['year']
    month = request.args['month']
    cond = str(year) + "-" + str(month)
    schedules = list(db.schedule.find({"$or": [{"start": {"$regex": cond + "/*"}},
                                               {"end": {"$regex": cond + "/*"}}]}))

    return jsonify({'result': 'success', 'schedule': schedules})


def photo_date(photo_list, path):
    # 사진의 촬열 시간 가져와

    date_list = []
    date_lists = []

    for photo in photo_list:
        i = Image.open(path + photo)
        info = i._getexif()
        i.close()
        tag = {}
        for t, value in info.items():
            decoded = TAGS.get(t, t)
            tag[decoded] = value
        time = datetime.datetime.strptime(tag['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
        date_list.append(time.strftime('%Y-%m-%d'))
        date_lists.append({'path': path + photo, 'year': time.strftime('%Y'), 'month': time.strftime('%m'), 'day': time.strftime('%d')})

    date_lists = sorted(date_lists, key=itemgetter('year', 'month', 'day'), reverse=True)
    print(type(date_lists[0]))
    return date_lists


# 삭제해
class PhotoDate:
    def __init__(self, path, year, month, day):
        self.path = path
        self.year = year
        self.month = month
        self.day = day

    def __repr__(self):
        return repr([self.path, self.year, self.month, self.day])


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
