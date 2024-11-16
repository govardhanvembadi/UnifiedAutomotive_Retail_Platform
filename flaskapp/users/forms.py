from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DateField, IntegerField, DecimalField
# from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from flask_login import current_user
from flaskapp.db_models import User, Service, Inventory
from datetime import datetime
class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[
        ('Admin', 'Admin'),
        ('Sales', 'Sales'),
        ('Service', 'Service'),
        ('Customer', 'Customer')
    ], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('That email is already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[
        ('Admin', 'Admin'),
        ('Sales', 'Sales'),
        ('Service', 'Service'),
        ('Customer', 'Customer')
    ], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
        
    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('That email is already registered. Please choose a different one.')



class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is None:
            raise ValidationError('There is no account with that email. You must register first.')
        

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
    

class SaleForm(FlaskForm):
    vehicle_id = IntegerField('Vehicle ID', validators=[DataRequired(), NumberRange(min=1)])
    customer_id = IntegerField('Customer ID', validators=[DataRequired(), NumberRange(min=1)])
    sale_date = StringField('Sale Date', default=datetime.utcnow().strftime('%Y-%m-%d'))  # Date as string in 'YYYY-MM-DD'
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)], default=1)
    total_amount = StringField('Total Amount', render_kw={'readonly': True})  # This will be auto-calculated
    payment_method = SelectField('Payment Method', choices=[('Cash', 'Cash'), ('Credit Card', 'Credit Card'), ('Loan', 'Loan')], validators=[DataRequired()])
    submit = SubmitField('Add Sale')

    def get_vehicle_details(self, vehicle_id):
        vehicle = Inventory.query.get(vehicle_id)
        if vehicle:
            return vehicle.model, vehicle.make, vehicle.price
        return None, None, 0  # Return defaults if no vehicle found

    def get_customer_name(self, customer_id):
        customer = User.query.get(customer_id)
        if customer:
            return customer.username
        return None  # Return None if no customer found




class InventoryForm(FlaskForm):
    make = StringField('Make', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    stock_count = IntegerField('Stock Count', default=1)
    price = DecimalField('Price', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Available', 'Available'), ('Sold', 'Sold')], default='Available')