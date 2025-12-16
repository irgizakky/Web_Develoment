from flask import Flask
from flask_mysqldb import MySQL


db = MySQL()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'rahasia123'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'sejarah_classroom'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    
    db.init_app(app)

    
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app
