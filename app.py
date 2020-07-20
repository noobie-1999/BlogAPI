from flask import Flask, jsonify, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time
from collections import OrderedDict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)
db.create_all()

class BlogPosts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(20), nullable=False, default="N/A")
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return "Post ID: "+str(self.post_id)

class Authors(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return "User ID: "+str(self.user_id)+"\tName: "+self.name

@app.route("/getpostcount")
def get_number_of_posts():
    try:
        post_count = db.session.query(BlogPosts.author, db.func.count(BlogPosts.post_id)).order_by(db.func.count(BlogPosts.post_id).desc()).group_by(BlogPosts.author).all()
        json_dict = {}
        for author in post_count:
            json_dict[author[0]] = author[1]
        print(json_dict)
        return jsonify(json_dict)
    except:
        return jsonify({"status":"failure"})

@app.route('/getpostsbyauthor/<string:author>')
def get_posts_by_author(author):
    posts = db.session.query(BlogPosts).filter_by(author=author).all()
    dict1 = OrderedDict()
    for post in posts:
        dict_post = {}
        dict_post['post_id'] = post.post_id
        dict_post['title']=post.title
        dict_post['content'] = post.content
        dict_post['author'] = post.author
        dict_post['date_posted'] = post.date_posted
        print(dict_post)
        dict1[post.post_id] = dict_post
    print(dict1)
    return jsonify(dict1)

@app.route("/createpost", methods=['POST'])
def create_post():
    try:
        data = request.get_json()
        new_post = BlogPosts(post_id=data["post_id"], author=data["author"], title=data["title"], content=data["content"])
        db.session.add(new_post)
        db.session.commit()
        return jsonify({"Status":"Success"})
    except:
        return jsonify({"Status":"Failure"})

@app.route('/deletepost/<int:post_id>')
def delete_post(post_id):
    try:
        db.session.delete(BlogPosts.query.get(post_id))
        db.session.commit()
        print("Post with ID "+str(post_id)+" is deleted. You will be redirected.")
        return redirect(url_for('get_posts'))

    except:
        print("Post with ID "+str(post_id)+" does not exisits. Please try again with a different Post ID")
        return redirect(url_for('get_posts'))

@app.route('/getposts')
def get_posts():
    try:
        posts = db.session.query(BlogPosts).order_by(BlogPosts.date_posted).all()
        dict1 = OrderedDict()
        for post in posts:
            dict_post = {}
            dict_post['post_id'] = post.post_id
            dict_post['title']=post.title
            dict_post['content'] = post.content
            dict_post['author'] = post.author
            dict_post['date_posted'] = post.date_posted
            print(dict_post)
            dict1[post.post_id] = dict_post
        print(dict1)
        return jsonify(dict1)

    except:
        return jsonify({"status":"failure"})

@app.route("/")
def hello_base_url():
    return "Hello World"

@app.route("/second_route")
def second_route():
    return "This is the second route"

if(__name__=='__main__'):
    app.run(debug=True)