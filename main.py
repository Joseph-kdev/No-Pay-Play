from flask import Flask
from blueprint.home.home import home
from blueprint.home.home import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///games.db"

#change the stuff b4 committing
db.init_app(app)
app.register_blueprint(home, url_prefix="/")

with app.app_context():
    db.create_all()
    
if __name__ == "__main__":
    app.run()