import os

class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245' #os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db' #os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'govardhan21241a0560@grietcollege.com' #os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = 'rgge fggc ggmj usou' #os.environ.get('EMAIL_PASS')  
