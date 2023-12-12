from flask import Flask,request,jsonify, make_response, send_file, url_for,Response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token,jwt_required, get_jwt_identity
from flask_cors import CORS,cross_origin
from datetime import timedelta,datetime
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import check_password_hash
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore
from sqlalchemy.orm import relationship

from flask import Blueprint, jsonify, request,send_from_directory, render_template
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from functools import wraps
import click
from werkzeug.utils import secure_filename
from celery.schedules import crontab
from flask_caching import Cache
import smtplib
from flask import render_template
from celery import shared_task
import sys
from datetime import datetime, timedelta,time
from flask.views import MethodView
import os
import io
import pandas as pd 
import io
from flask import make_response 
from flask import send_file
import tempfile 
from io import BytesIO
import csv
from celery import Celery
import redis
import logging
from tempfile import NamedTemporaryFile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
from werkzeug import datastructures
from werkzeug.datastructures import FileStorage
from config import Config
from flask_restful import Api, Resource, reqparse, fields, marshal_with, inputs
from flask_mail import Message
from io import BytesIO
import base64
import matplotlib.pyplot as plt

#from models import User,Role,Show,Theatre,Ticket
#from api import ShowListResource,ShowRatingResource,TheaterResource,ShowResource,SearchShowsResource,SearchTheatresResource,UploadedFileResource,ExportTheatreResource,BookShowsResource

#SignupResource,LoginResource,

celery_app = Celery(
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/2',
    broker_connection_retry_on_startup=True
)

UPLOAD_FOLDER = 'C:/padmaja/mad2/flaskvue/ticketshow/backend/static/uploads'

smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = 'padmaja121003@gmail.com'
smtp_password = 'ifdnhydooadjawzc'



app = Flask(__name__)
api = Api(app)
CORS(app, resources={r"*": {"origins": "*"}})
app.config['SECRET_KEY'] = '5e14a40fcda83b6d909ff639f40cccb4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 




smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = 'padmaja121003@gmail.com'
smtp_password = "ifdnhydooadjawzc"

mail = Mail()

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = '21f3002898@ds.study.iitm.ac.in'
app.config['MAIL_PASSWORD'] = 'd8gn4x9c'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/1'
app.config['CELERY_RESULT_BACKEND']='redis://localhost:6379/2'
app.config['CELERY_WORKER_CONCURRENCY']= 4


mail.init_app(app)
app.app_context().push()
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
                       )

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100),nullable=True)
    password = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    is_admin = db.Column(db.Boolean(), default=False)
    roles = db.relationship('Role',secondary= roles_users,backref=db.backref('users', lazy='dynamic'))
    tickets_purchased = db.relationship('Ticket', backref='purchased_by', lazy=True)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    def get_roles(self):
        return [role.name for role in self.roles]
    

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"<Role {self.name}>"
    

class Theatre(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    shows = db.relationship('Show', backref='Theatre', lazy=True,cascade='all, delete-orphan')

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    image = db.Column(db.String(255))
    rating = db.Column(db.Float, nullable=True)
    tags = db.Column(db.String(200))
    ticket_price = db.Column(db.Float)
    capacity = db.Column(db.Integer, nullable=False, default=1)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatre.id'), nullable=False)
    theatre = db.relationship('Theatre', back_populates='shows',overlaps="Theatre")
    tickets = db.relationship('Ticket', backref='event', lazy="joined", primaryjoin='Show.id == Ticket.show_id')
    ratings = db.relationship('ShowRating', backref='show', lazy='dynamic')

class ShowRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)


class Ticket(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatre.id',ondelete='CASCADE'), nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))      
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_username = get_jwt_identity()
        current_user = User.query.filter_by(username=current_user_username).first()
        print(current_user)
        if current_user.is_admin:
            return fn(*args, **kwargs)
        else:
            return jsonify({'message': 'Admin access required'}), 403
    return wrapper
    
@app.route('/')
def home():
    return 'Welcome to the homepage'




@app.cli.command("create_admin")
@click.argument("username")
@click.argument("password")
def create_admin(username, password):
    with app.app_context():
        db.create_all()

        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator role')
            db.session.add(admin_role)

        admin_user = User.query.filter_by(username=username).first()
        if not admin_user:
            admin_user = User(username=username, is_admin=True)  
            admin_user.set_password(password)  
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")    

signup_parser = reqparse.RequestParser()
signup_parser.add_argument('id', type=int, required=True, help='User ID')
signup_parser.add_argument('email', type=str, help='User email')
signup_parser.add_argument('username', type=str, required=True, help='Username')
signup_parser.add_argument('password', type=str, required=True, help='Password')

# Request parser for user login
login_parser = reqparse.RequestParser()
login_parser.add_argument('username', type=str, required=True, help='Username')
login_parser.add_argument('password', type=str, required=True, help='Password')

# Fields for user serialization
user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'active': fields.Boolean,
    'is_admin': fields.Boolean,
}

# Fields for login response
login_response_fields = {
    'token': fields.String,
    'is_admin': fields.Boolean,
}

  
class SignupResource(Resource):
    def post(self): 
        args = signup_parser.parse_args() 
        email = args['email']
        username = args['username'] 
        password = args['password'] 

        if not username or not password or not email:
             return {'message': 'Missing fields!'}, 400

        user = User.query.filter_by(username=username).first()
        if user:
             return {'message': 'Username already exists!'}, 409

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=username, additional_claims={'is_admin': user.is_admin})
        return {'token': access_token, 'is_admin': user.is_admin}, 201

    '''@staticmethod
    def as_view(cls):
        return MethodView.as_view(cls)'''

class LoginResource(Resource):
    def post(self):
        args = login_parser.parse_args()
        username = args['username']
        password = args['password']

        if not username or not password:
            return {'message': 'Invalid credentials!'}, 401

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            # Generate a token with the user's id and role
            access_token = create_access_token(identity=username, additional_claims={'is_admin': user.is_admin})
            return {'token': access_token, 'is_admin': user.is_admin}, 200
        else:
            return {'message': 'Wrong username or password!'}, 401

    '''@staticmethod
    def as_view(cls):
        return MethodView.as_view(cls)'''

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}   

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
      



show_parser = reqparse.RequestParser()
show_parser.add_argument('name', type=str, required=True, help='The name of the show')
show_parser.add_argument('start_time', type=inputs.datetime_from_iso8601, required=True, help='The start time of the show in ISO 8601 format')
show_parser.add_argument('end_time', type=inputs.datetime_from_iso8601, required=True, help='The end time of the show in ISO 8601 format')
show_parser.add_argument('tags', type=str, help='Tags for the show')
show_parser.add_argument('ticket_price', type=float, required=True, help='The ticket price of the show')
show_parser.add_argument('theatre_id', type=int, required=True, help='The ID of the theatre for the show')
show_parser.add_argument('image', type=datastructures.FileStorage, location='files', help='The image file for the show')


show_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'start_time': fields.DateTime(dt_format='iso8601'),
    'end_time': fields.DateTime(dt_format='iso8601'),
    'tags': fields.String,
    'ticket_price': fields.Float,
    'image': fields.String,
    'theatre_id': fields.Integer,
    'capacity': fields.Integer,
}

class ShowResource(Resource):

    '''def __init__(self):
        super(ShowResource, self).__init__()'''

    print('reached inside')
    @marshal_with(show_fields)
    @jwt_required()
    def get(self):
        print('reached inside get')
        shows = Show.query.all()
        show_list = []

        for show in shows:
            # Calculate the average rating for the show
            theatre = Theatre.query.get(show.theatre_id)
            theatre_name = theatre.name if theatre else None
            rating = show.rating if show.rating is not None else 0.0
            print(show.image)

            show_data = {
                'id': show.id,
                'name': show.name,
                'start_time': show.start_time,
                'end_time': show.end_time,
                'rating': rating,
                'tags': show.tags,
                'ticket_price': show.ticket_price,
                'image': f'http://127.0.0.1:5000/uploads/{show.image}',
                'theatre_id': show.theatre_id,
                'capacity': show.capacity,
            }
            show_list.append(show_data)
        print(show_list)
        return show_list

    @marshal_with(show_fields)
    @jwt_required()
    def post(self):
        if request.is_json:
        # Handling JSON request
            print('json data')
            data = request.get_json()
            name = data.get('name')
            start_time_str = data.get('start_time')
            end_time_str = data.get('end_time')
            tags = data.get('tags')
            ticket_price = data.get('ticket_price')
            image_filename = data.get('image')
            theatre_id = data.get('theatre_id')

            if not name or not theatre_id:
                return jsonify({'message': 'Name and theatre_id are required'}), 400

            theatre = Theatre.query.get(theatre_id)
            if not theatre:
                return jsonify({'message': 'Theatre not found'}), 404

            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)

        # Calculate the capacity based on the numeric value of the theatre
            capacity = int(theatre.capacity)

            new_show = Show(
            name=name, start_time=start_time, end_time=end_time, tags=tags, ticket_price=ticket_price,
            image=image_filename, theatre_id=theatre_id, capacity=capacity  # Set capacity here
            )

            db.session.add(new_show)
            db.session.commit()
            return jsonify({'message': 'Show created successfully'}), 201
        else:
        # Handling form data request
            print('data form')
            data = request.form
            name = data.get('name')
            start_time_str = data.get('start_time')
            end_time_str = data.get('end_time')
            tags = data.get('tags')
            ticket_price = data.get('ticket_price')
            image_data = request.files.get('image')
            theatre_id = data.get('theatre_id')

            if not name or not theatre_id:
               return jsonify({'message': 'Name and theatre_id are required'}), 400

            theatre = Theatre.query.get(theatre_id)
            if not theatre:
               return jsonify({'message': 'Theatre not found'}), 404

            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)

        # Calculate the capacity based on the numeric value of the theatre
            capacity = int(theatre.capacity)

            try:
                if image_data:
                    filename = secure_filename(image_data.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image_data.save(image_path)
                    image_filename = os.path.basename(image_path)
                else:
                    image_filename = None
            except Exception as e:
                return jsonify({'message': 'Error saving image'}), 500

            new_show = Show(
            name=name, start_time=start_time, end_time=end_time, tags=tags, ticket_price=ticket_price,
            image=image_filename, theatre_id=theatre_id, capacity=capacity  # Set capacity here
             )

            db.session.add(new_show)
            db.session.commit()
            return jsonify({'message': 'Show created successfully'}), 201
        return jsonify({'message': 'Unsupported request method'}), 405

    
    '''@staticmethod
    def as_view(cls):
        return Resource.as_view(cls)''' 

class UpdateShowResource(Resource):
    @marshal_with(show_fields)
    @jwt_required()
    def put(self, show_id):
        args = show_parser.parse_args()
        show = Show.query.get(show_id)

        if show is None:
            return {'message': 'Show not found'}, 404

        # Update the show attributes based on the parsed arguments
        if args['name']:
            show.name = args['name']
        if args['start_time']:
            show.start_time = args['start_time']
        if args['end_time']:
            show.end_time = args['end_time']
        if args['tags']:
            show.tags = args['tags']
        if args['ticket_price']:
            show.ticket_price = args['ticket_price']
        if args['image']:
            show.image = args['image']
        if args['theatre_id']:
            show.theatre_id = args['theatre_id']

        db.session.commit()
        return show
    
    @jwt_required()
    def delete(self, show_id):
        show = Show.query.get(show_id)

        if show:
            db.session.delete(show)
            db.session.commit()
            return {'message': 'Show deleted'}
        else:
            return {'message': 'Show not found'}, 404

    '''@staticmethod
    def as_view(cls):
        return Resource.as_view(cls)    '''    

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='The name of the theater')
parser.add_argument('place', type=str, required=True, help='The location of the theater')
parser.add_argument('capacity', type=int, required=True, help='The seating capacity of the theater')

theatre_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'place': fields.String,
    'capacity': fields.Integer,
}

class TheaterResource(Resource):
    print('reached inside theatreapi')
    @marshal_with(theatre_fields)
    @jwt_required()
    def get(self):
        print('reached inside theatre get')
        #if theater_id is None:
            # This handles the GET request for all theaters
        theatres = Theatre.query.all()
        theatre_list = []
        for theatre in theatres:
            theatre_data = {
                'id': theatre.id,
                'name': theatre.name,
                'place': theatre.place,
                'capacity': theatre.capacity
                }
            theatre_list.append(theatre_data)
        return theatre_list
        '''else:
            # This handles the GET request for a specific theater by ID
            theater = Theatre.query.get(theater_id)
            if theater:
                return theater
            else:
                return {'message': 'Theater not found'}, 404'''
    @jwt_required()
    @marshal_with(theatre_fields)
    def post(self, theatre_id=None):
        print('reached inside theatre post')
        if theatre_id is None:
            # This handles the POST request to create a new theater
            args = parser.parse_args()
            new_theatre = Theatre(
                name=args['name'],
                place=args['place'],
                capacity=args['capacity']
            )
            db.session.add(new_theatre)
            db.session.commit()
            return new_theatre, 201    
    '''@staticmethod
    def as_view(cls):
        return Resource.as_view(cls)'''

class TheaterUpdateResource(Resource):
    @jwt_required()
    @marshal_with(theatre_fields)
    def put(self, theatre_id):
        args = parser.parse_args()
        theatre = Theatre.query.get(theatre_id)

        if theatre is None:
            return {'message': 'Theatre not found'}, 404
        theatre.name = args['name']
        theatre.place = args['place']
        theatre.capacity = args['capacity']
        db.session.commit()
        return theatre

    @marshal_with(theatre_fields)
    @jwt_required()
    def delete(self, theatre_id):
        theatre = Theatre.query.get(theatre_id)

        if theatre:
            db.session.delete(theatre)
            db.session.commit()
            return {'message': 'Theatre deleted'}
        else:
            return {'message': 'Theatre not found'}, 404

    '''@staticmethod
    def as_view(cls):
        return Resource.as_view(cls)    '''    

class UploadFileResource(Resource):
    @jwt_required()
    def post(self):
        print("Received file")
        if 'image' not in request.files:
            return jsonify({'message': 'No image part in the request'}), 400

        image_file = request.files['image']

        if image_file.filename == '':
            return jsonify({'message': 'No selected file'}), 400

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            relative_image_path = filename
            print("File saved as:", image_path)

            return jsonify({'url': relative_image_path}), 201
        else:
            print("Invalid file format")
            return jsonify({'message': 'Invalid file format'}), 400
    '''@staticmethod
    def as_view(cls):
        return Resource.as_view(cls)   '''     

class UploadedFileResource(Resource):
    def get(self, filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    '''@staticmethod
    def as_view(cls):
        return Resource.as_view(cls)'''    


rating_parser = reqparse.RequestParser()
rating_parser.add_argument('rating', type=int, required=True)

class BookShowsResource(Resource):
    @jwt_required()
    def post(self, show_id):
        data = request.get_json()
        number_of_tickets = data.get('number_of_tickets')
        user_rating = data.get('rating')
        current_user_username = get_jwt_identity()
        current_user = User.query.filter_by(username=current_user_username).first()
        if number_of_tickets == 0:
            return jsonify({'message': 'Invalid number of tickets'}), 400

        show = Show.query.get(show_id)
        if not show:
            return jsonify({'message': 'Show not found'}), 404

        if show.capacity < int(number_of_tickets):
            return jsonify({'message': 'Not enough available tickets'}), 400

        # Update the show's rating here based on user_rating
        if user_rating:
            print(user_rating)
            user_rating = int(user_rating)
            if user_rating < 1 or user_rating > 5:
                return jsonify({'message': 'Invalid rating value. It should be between 1 and 5.'}), 400
            
            # Check if the user has already rated this show
            existing_rating = ShowRating.query.filter_by(user_id=current_user.id, show_id=show.id).first()
            if existing_rating:
                print("Updating existing rating with value:", user_rating)
    # Update the existing rating
                existing_rating.rating = user_rating
            else:
                print("Creating a new rating with value:", user_rating)
    # Create a new rating
                new_rating = ShowRating(user_id=current_user.id, show_id=show.id, rating=user_rating)
                db.session.add(new_rating)

            # Calculate the new average rating for the show
            ratings = ShowRating.query.filter_by(show_id=show.id).all()
            total_ratings = sum([rating.rating for rating in ratings])
            average_rating = total_ratings / len(ratings) if ratings else 0
            show.rating = average_rating  # Update the show's average rating

        for _ in range(int(number_of_tickets)):
            ticket = Ticket(
                theatre_id=show.theatre_id,
                price=show.ticket_price,
                quantity=1,
                user_id=current_user.id,
                show_id=show.id,
            )
            db.session.add(ticket)

        show.capacity -= int(number_of_tickets)
        db.session.commit()

        return jsonify({'message': f'Successfully booked {number_of_tickets} tickets for {show.name}'})




# Define a parser for search queries
search_parser = reqparse.RequestParser()
search_parser.add_argument('name', type=str)
search_parser.add_argument('place', type=str)
search_parser.add_argument('tags', type=str)
search_parser.add_argument('rating', type=float)

# Define fields for serialization
class SearchTheatresResource(Resource):
    @jwt_required()
    def get(self):
        try:
            search_query = request.args.get('name')
            place_query = request.args.get('place')

            if search_query:
                theatres = Theatre.query.filter(Theatre.name.ilike(f'%{search_query}%')).all()
                result = [{'id': theatre.id, 'name': theatre.name, 'place': theatre.place} for theatre in theatres]
            elif place_query:
                theatres = Theatre.query.filter(Theatre.place.ilike(f'%{place_query}%')).all()
                result = [{'id': theatre.id, 'name': theatre.name, 'place': theatre.place} for theatre in theatres]
            else:
                result = []

            response = jsonify(result)
            return response
        except Exception as e:
            error_message = {'error': 'Internal Server Error', 'message': str(e)}
            return jsonify(error_message), 500




    '''@staticmethod
    def as_view(cls):
        return MethodView.as_view(cls)'''

class SearchShowsResource(Resource):
    @jwt_required()
    def get(self):
        try:
            print('reached inside search shows get')
            tags_query = request.args.get('tags')
            rating_query = request.args.get('rating')
            print('got args')

            if tags_query:
                shows = Show.query.filter(Show.tags.ilike(f'%{tags_query}%')).all()
                result = [{'id': show.id, 'name': show.name, 'tags': show.tags} for show in shows]
                print(result)
                response = jsonify(result)
                print(response)
            elif rating_query is not None:

                try:
                   rating_query = float(rating_query)
                except ValueError:
                   return jsonify({'message': 'Invalid rating value. It should be a number.'}), 400

                tolerance = 0.1  
                shows = Show.query.filter(
                Show.rating >= rating_query - tolerance,
                Show.rating <= rating_query + tolerance
                ).all()
                result = [{'id': show.id, 'name': show.name, 'rating': show.rating} for show in shows]
                print(result)
                response = jsonify(result)

            else:
                print('json data was returned')
                response = jsonify([])

            return response
        except Exception as e:
            error_message = {'error': 'Internal Server Error', 'message': str(e)}
            return jsonify(error_message)

    '''@staticmethod
    def as_view(cls):
        return MethodView.as_view(cls)'''

class ExportTheatreResource(Resource):
    @jwt_required()
    def get(self, theatre_id):
        try:
            print(f"Triggering export_theatre_csv Celery task for theatre ID: {theatre_id}")
            result = export_theatre_csv.apply_async(args=[theatre_id])
            print(f"Export_theatre_csv Celery task triggered, task ID: {result.id}")

            task_id = result.id

            print(f"Waiting for the task to complete, task ID: {task_id}")
            result_task = export_theatre_csv.AsyncResult(task_id)
            csv_data = result_task.get()

            if csv_data:
                print("CSV data available, writing to file and sending response")
                print(csv_data)
                file_path = 'theatre_report.csv'
                csv_file = io.StringIO(csv_data)

                df = pd.read_csv(csv_file)
                print(df)
                df.to_csv(file_path)

                response = send_file(file_path, as_attachment=True, mimetype='text/csv')
                return response

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

        return jsonify([]), 200      
    '''@staticmethod
    def as_view(cls):
        return MethodView.as_view(cls)     '''         

class UserProfileResource(Resource):
    @jwt_required()
    def get(self):
        current_user_username = get_jwt_identity()
        current_user = User.query.filter_by(username=current_user_username).first()

        if not current_user:
            return {'message': 'User not found'}, 404

        # Fetch booked tickets for the current user
        booked_tickets = Ticket.query.filter_by(user_id=current_user.id).all()

        # Create a dictionary to store unique shows and their details
        booked_shows = {}

        # Collect show details for the booked tickets
        for ticket in booked_tickets:
            show = Show.query.get(ticket.show_id)
            if show:
                show_id = show.id
                if show_id not in booked_shows:
                    booked_shows[show_id] = {
                        'show_name': show.name,
                        'show_start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'show_end_time': show.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'ticket_count': 1  # Initialize ticket count to 1
                        # Add other show details here
                    }
                else:
                    # If the show already exists in the dictionary, increment the ticket count
                    booked_shows[show_id]['ticket_count'] += 1
        print(booked_shows)
        return {
            'user': {
                'username': current_user.username,
                'email': current_user.email,
                # Add other user details here
            },
            'booked_shows': list(booked_shows.values())  # Convert dictionary to list
        }


api.add_resource(SignupResource, '/signup',methods=['POST'])        
api.add_resource(LoginResource, '/login',methods=['POST'])
api.add_resource(TheaterResource, '/theatres',methods=['POST','GET'])
api.add_resource(TheaterUpdateResource, '/theatres/<int:theatre_id>',methods=['PUT','DELETE'])
api.add_resource(ShowResource, '/shows',methods=['POST','GET','DELETE'])
api.add_resource(UpdateShowResource, '/shows/<int:show_id>',methods=['PUT','DELETE'])
#api.add_resource(ShowRatingResource, '/shows/<int:show_id>/rate')
api.add_resource(UploadFileResource, '/uploads',methods=['POST'])
api.add_resource(UploadedFileResource, '/uploads/<filename>',methods=['GET'])
api.add_resource(BookShowsResource, '/bookshows/<int:show_id>/book')
api.add_resource(SearchTheatresResource, '/search/theatres',methods=['GET'])
api.add_resource(SearchShowsResource, '/search/shows',methods=['GET'])
api.add_resource(UserProfileResource, '/userprofile')
api.add_resource(ExportTheatreResource, '/export_theatre/<int:theatre_id>')


routes = Blueprint('routes', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

@celery_app.task
def send_email_reminder():
    print('Task received')
    with app.app_context():
        users = User.query.all()
        print('Users queried')

        for user in users:
            subject = "Daily Reminder: Visit/Book Something!"
            message = f"Hello {user.username},\n\nDon't forget to visit or book something on our Ticket Show platform today!\n\nBest regards,\nThe Ticket Show Team"
            print('Going into try block')
            try:
                # Set up your SMTP connection
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                print('Connected to SMTP server')

                # Create a MIME message
                msg = MIMEMultipart()
                msg["From"] = 'padmaja121003@gmail.com'
                msg["To"] = user.email
                msg["Subject"] = subject

                # Attach the message to the email
                msg.attach(MIMEText(message, 'plain'))

                # Send the email
                server.sendmail(smtp_username, user.email, msg.as_string())
                server.quit()

                print(f"Reminder email sent to {user.email}")
                logging.info(f"Reminder email sent to {user.email}")
            except Exception as e:
                logging.error(f"Error sending reminder email to {user.email}: {e}")
                print(f"Error sending reminder email to {user.email}: {e}")



  
@celery_app.task
def generate_monthly_report():
    # Calculate the date range for the previous month
    today = datetime.now()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)

    # Query the database to gather information for the report

    users = User.query.all()

    for user in users:
        user_tickets = db.session.query(User, Ticket, Show). \
            join(Ticket, Ticket.user_id == User.id). \
            join(Show, Show.id == Ticket.show_id). \
            filter(Show.start_time.between(first_day_of_current_month, today)).all()

        user_ratings = db.session.query(User.username, Show.name, ShowRating.rating). \
            join(ShowRating, User.id == ShowRating.user_id). \
            join(Show, Show.id == ShowRating.show_id). \
            filter(Show.start_time.between(first_day_of_current_month, today)).all()    


        report_html = """
        <!DOCTYPE html>
        <html>
        <head>
           <title>Monthly Entertainment Report</title>
        </head>
        <body>
           <h2>Bookings Made:</h2>
           <ul>
            {0}
           </ul>

           <h2>Show Ratings:</h2>
           <ul>
              {1}
           </ul>
        </body>
        </html>
        """.format(
           "".join(f"<li>{user.username} purchased tickets for {ticket.event.name} on {ticket.event.start_time.strftime('%Y-%m-%d %H:%M')}</li>" for user, ticket, show in user_tickets),
           "".join(f"<li>{username} rated {show_name}: {rating}/5</li>" for username, show_name, rating in user_ratings),
        )

    # Send the report as an email
        send_report_as_email(user, report_html)

def send_report_as_email(user, report_html):
    try:
        # Set up your SMTP connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        print('Connected to SMTP server')

        # Create a MIME message
        msg = MIMEMultipart()
        msg["From"] = smtp_username
        msg["To"] = user.email
        msg["Subject"] = 'Monthly Entertainment Report'

        # Attach the HTML report to the email
        msg.attach(MIMEText(report_html, 'html'))

        # Send the email
        server.sendmail(smtp_username, user.email, msg.as_string())
        server.quit()

        print(f'Report email sent successfully to {user.username}')
    except Exception as e:
        print(f'Error sending report email to {user.username}: {str(e)}')

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    print('Scheduled monthly report task')
    
    # Schedule the send_email_reminder task to run every 10 seconds
    sender.add_periodic_task(
        2000.0,  # Interval in seconds
        send_email_reminder.s(),
        name='send_email_reminder_to_all_users'
    )

    # Schedule the generate_monthly_report task to run on the first day of each month
    sender.add_periodic_task(
        60.0,
        generate_monthly_report.s(),
        name='generate_monthly_report'
    )        

'''@celery_app.task
def send_daily_reminder():
    with app.app_context():
        users = User.query.all()
        for user in users:
            send_email_reminder.delay(user.id)  # Use .delay() to invoke the Celery task



@shared_task
def send_email(report, email):
    message = Message()
    message.set_content(report)
    message["Subject"] = "Your Monthly Entertainment Report"
    message["From"] = "21f3002898@ds.study.iitm.ac.in"  
    message["To"] = email

    try:
        
        server = smtplib.SMTP("smtp.gmail.com", 587)  
        server.starttls()
        server.login("21f3002898@ds.study.iitm.ac.in", "d8gn4x9c")  

        server.send_message(message)
        server.quit()
        print(f"Report sent to {email}")

    except Exception as e:
        print(f"Error sending report to {email}: {e}")

@shared_task
def send_monthly_report():
    print("Sending monthly reports...")
    with app().app_context():
         users = User.query.all()
         for user in users:
             report = render_template("monthly_report.html", user=user)
             send_email.delay(report, user.email)
           
celery_app.conf.beat_schedule = {
    'send-daily-reminder': {
        'task': 'run.send_daily_reminder',  # Replace with your module name
        'schedule': crontab(hour=0, minute=30),  # Set the desired schedule (e.g., daily at 07:20 AM)
    },
}'''

@celery_app.task(name='export_theatre_csv')
def export_theatre_csv(theatre_id):
    try:
        print(f"Exporting theatre CSV for theatre ID: {theatre_id}")
        with app.app_context():
            theatre = Theatre.query.get(theatre_id)
            shows = Show.query.filter_by(theatre_id=theatre_id).all()
        if not theatre:
            raise Exception(f"Theatre with ID {theatre_id} not found")

        csv_data = [
            ['Theatre Name', theatre.name],
            ['Number of Shows', len(shows)],
			['Number of Bookings', sum(1 for show in shows for ticket in show.tickets if ticket.user_id is not None)],
            ['Average Rating', sum(show.rating for show in shows) / len(shows)],
            
        ]

        csv_file = io.StringIO()
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerows(csv_data)
        csv_data = csv_file.getvalue()
        print("CSV data created")

        return csv_data
        
    except Exception as e:
        print(f"Error exporting theatre CSV: {e}")
        raise e


@app.route('/popularity_graph_image', methods=['GET'])
def popularity_graph_image():
    # Query the database to get show names and ratings
    shows = Show.query.all()
    show_names = [show.name for show in shows]
    ratings = [show.rating for show in shows]

    # Create a figure with a specified size
    plt.figure(figsize=(9, 4))

    # Create a bar plot with customized colors
    bars = plt.bar(show_names, ratings, color='green')

    # Add labels and a title
    plt.xlabel('Shows', fontsize=14)
    plt.ylabel('Ratings', fontsize=14)
    plt.title('Show Popularity Based on Ratings', fontsize=16)

    # Add data labels above each bar
    for bar, rating in zip(bars, ratings):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 0.5, str(rating), ha='center', fontsize=9)

    # Rotate x-axis labels for better visibility
    plt.xticks(rotation=45, ha='right', fontsize=12)

    # Adjust spacing for the x-axis labels
    plt.subplots_adjust(bottom=0.2)

    # Save the plot as a PNG image
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)

    # Encode the image as base64
    img_base64 = base64.b64encode(img_buffer.read()).decode()

    # Generate a data URI for the image
    data_uri = 'data:image/png;base64,' + img_base64

    # Close the Matplotlib plot to release resources
    plt.close()

    return jsonify(data_uri)

if __name__=="__main__":
	app.run(debug=True)
	