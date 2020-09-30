#import Flask to create instance of web application
#request to get request data
#jsonify to turns the JSON output into a Response object with the application/json mimetype
#SQAlchemy from flask_sqlalchemy to accessing database
#Marshmallow from flask_marshmallow to serialized object
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import os

#Create an instances of our web application and set path of our SQLite uri.
app = Flask(__name__, template_folder="templates")
app.secret_key = "SecretKey20202020202020"
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data_test.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#---- ---- ---- ----
#Binding SQLAlchemy and Marshmallow into our flask application.
db = SQLAlchemy(app)
ma = Marshmallow(app)
#---- ---- ---- ----
#After importing SQLAlchemy and bind it to our flask app, we can declare our models. Here we declare model called eData and defined its field with it's properties.
class eData(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=False)
    email = db.Column(db.String(250), unique=False)
    timestamp = db.Column(
        db.DateTime, default=datetime.now(), onupdate=datetime.now()
    )

    def __init__(self, username, email):
#		self.id = id
        self.username = username
        self.email = email
        #self.timestamp = timestamp
#---- ---- ---- ----
#This part defined structure of response of our endpoint. We want that all of our endpoint will have JSON response. Here we define that our JSON response will have two keys(username, and email). Also we defined user_schema as instance of UserSchema, and user_schemas as instances of list of UserSchema.
class eDataSchema(ma.Schema):
    class Meta:
        # Fields to expose
	# fields = ('username', 'email')
        #fields = ('id', 'username', 'email')
        fields = ('id', 'username', 'email', 'timestamp')

data_schema = eDataSchema()
datas_schema = eDataSchema(many=True)
#---- ---- ---- ----
#---- ---- ---- ----
# endpoint to show all records
@app.route("/data", methods=["GET"])
def get_data():
    all_data = eData.query.all()
    result = datas_schema.dump(all_data)
    return datas_schema.jsonify(all_data)
#---- ---- ---- ----
# endpoint to get user detail by id
@app.route("/data/<id>", methods=["GET"])
def data_detail_id(id):
    data = eData.query.get(id)
    return data_schema.jsonify(data)
#---- ---- ---- ----
# endpoint to get user detail by username
@app.route("/data/username/<username>", methods=["GET"])
def data_detail_username(username):
    #data = eData.query.get(id)
    data = eData.query.filter(eData.username == username).one_or_none()
    return data_schema.jsonify(data)
#---- ---- ---- ----
#endpoint to create new record
##set the route to "/data" and set HTTP methods to POST
@app.route("/data", methods=["POST"])
def add_data():
	#id = request.json[' id']
    username = request.json['username']
    email = request.json['email']
    
    new_data = eData(username, email)
    if db.session.query(eData).filter_by(username=username).count() > 0:
        return jsonify('This data exist on database!')

    db.session.add(new_data)
    db.session.commit()
    return jsonify('Data added Successfully!')
#---- ---- ---- ----
# endpoint to update a record
@app.route("/data/<id>", methods=["PUT"])
def data_update(id):
    data = eData.query.get(id)
	#id = request.json['id']
    username = request.json['username']
    email = request.json['email']

    data.username = username
    data.email = email


    db.session.commit()
    return data_schema.jsonify(data)
#---- ---- ---- ----
# endpoint to delete a record
@app.route("/data/<id>", methods=["DELETE"])
def data_delete(id):
    data = eData.query.get(id)
    db.session.delete(data)
    db.session.commit()

    return jsonify('Data was deleted!')
    #return data_schema.jsonify(user)
#---- ---- ---- ----
'''
#Make req with header: Content-Type : application/json
#read all data
curl 'http://127.0.0.1:5000/data'
#get user detail by id
curl 'http://127.0.0.1:5000/data/1'
#get user detail by username
curl 'http://127.0.0.1:5000/data/username/admin'
#create new record
curl 'http://127.0.0.1:5000/data' -H "Content-Type: application/json" -X POST -d '{ "email": "user1@localhost.local", "username": "user1" }'
#update a record by id
curl 'http://127.0.0.1:5000/data/1' -H "Content-Type: application/json" -X PUT -d '{ "email": "admin@localhost.local", "id": 1, "username": "admin1" }'
#delete a record by id
curl 'http://127.0.0.1:5000/data/7' -X DELETE
'''
@app.errorhandler(404)
def page_not_found(e):
	return '<h1>404 PAGE NOT FOUND!<br><a href="/">Click here go to Home</a></h1>'
	#return render_template('404.html')

@app.errorhandler(500)
def internal_server_error(e):
	return '<h1>500 Internal Server Error!</h1>'
	#return render_template('500.html')

@app.route('/')
def index():
	#result = eData.query.all()
	users_desc = eData.query.order_by(eData.username.desc())
	return render_template('index.html',result=users_desc)
#	return '<h1>Hello World!</h1>'

#table view
@app.route('/table')
def table():
	results = eData.query.all()
	return render_template('table.html',results=results)

#pagination
@app.route("/pages/<int:page_num>")  
def pages(page_num):
    all_data = eData.query.paginate(per_page=2, page=page_num, error_out=True)
    #all_data = eData.query.all()
    return render_template("pages.html",all_data = all_data) 


@app.route('/form')
def form():
	 return render_template('add.html')

#add new record
@app.route('/add', methods =['POST'])
def add():
	username = request.form['username']
	email = request.form['email']
#
	add_data = eData(username=username,email=email)
	db.session.add(add_data)
	db.session.commit()

	return redirect(url_for('index'))
	#return '<h1>ADD TEST</h1><br><h1>Username: {}<br>Email: {}</h1>'.format(username,email)

#edit a record
@app.route('/edit/<id>', methods = ['GET', 'POST'])
def edit(id):
	edit_data = eData.query.get(id)
	return render_template("edit.html",result = edit_data)


#update a record
@app.route('/update', methods = ['GET', 'POST'])
def update():

    if request.method == 'POST':
        update_data = eData.query.get(request.form.get('id'))
        update_data.username = request.form['username']
        update_data.email = request.form['email']

        db.session.commit()
        flash("Data Updated Successfully")
	
        return redirect('/')
        #return redirect(url_for('Index'))

#delete a record
@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    del_data = eData.query.get(id)
    db.session.delete(del_data)
    db.session.commit()
    flash("Data Deleted Successfully")

    return redirect('/')

#search page
@app.route('/search', methods=['GET', 'POST'])
def search():
	return render_template('search.html')


#search result
@app.route('/results', methods =['POST'])
def search_results():
	search = request.form['search']
	search_text = search
	qry1 = eData.query.filter(eData.username.like('%'+ search_text +'%')).all()
	qry2 = eData.query.filter(eData.email.like('%'+ search_text +'%')).all()
	qry3 = eData.query.filter(eData.id.like('%'+ search_text +'%')).all()
	result = qry1 or qry2 or qry3
	return render_template('search.html', result=result)


