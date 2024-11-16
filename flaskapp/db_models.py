from datetime import datetime, timedelta
import jwt
from flaskapp import db, login_manager
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import event
from sqlalchemy.orm import validates

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'Admin', 'Sales', 'Service', 'Customer'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    
    def get_reset_token(self, expires_sec=1800):
        payload = {
            'user_id': self.user_id,
            'exp': datetime.now() + timedelta(seconds=expires_sec)
        }
        # Encode the token and return it directly
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token
    
    @staticmethod
    def verify_reset_token(token):
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
        return User.query.get(user_id)
    # You can override the get_id() method, but it's not necessary if you use UserMixin
    def get_id(self):
        return str(self.user_id)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now())
    content = db.Column(db.Text, nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Inventory(db.Model):
    __tablename__ = 'inventory'

    vehicle_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    stock_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(50), nullable=False)  # 'available' or 'sold'
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Automatically gets 'sales' and 'service_records' attributes via backref in Sales and Service models

    def __repr__(self):
        return f"Inventory('{self.vehicle_id}', '{self.make}', '{self.model}', '{self.year}', {self.stock_count})"


class Sales(db.Model):
    __tablename__ = 'sales'
    
    sale_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('inventory.vehicle_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # Foreign key to User
    sale_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    quantity = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # 'Cash', 'Credit'

    def __repr__(self):
        return f"Sales('{self.sale_id}', '{self.vehicle_id}', '{self.customer_id}', '{self.sale_date}')"


class Service(db.Model):
    __tablename__ = 'service'
    
    service_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('inventory.vehicle_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)  # 'oil change', 'tire replacement', etc.
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'scheduled', 'completed'
    service_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"Service('{self.service_id}', '{self.vehicle_id}', '{self.customer_id}', '{self.service_type}')"



@event.listens_for(Sales, 'after_insert')
def update_vehicle_stock_count(mapper, connection, target):
    vehicle = Inventory.query.get(target.vehicle_id)  # Get the vehicle associated with the sale
    if vehicle:
        vehicle.stock_count -= target.quantity  # Subtract the quantity sold from the stock_count
        # db.session.commit()  # Commit the changes to the database
