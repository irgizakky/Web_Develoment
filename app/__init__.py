from flask import Flask
from app.extensions import db  

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'kunci_rahasia'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'sejarah_classroom'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

 
    db.init_app(app)


    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.main import main_bp
    
   
    from app.routes.materi import materi_bp
    app.register_blueprint(materi_bp)
    
    return app


    return app
