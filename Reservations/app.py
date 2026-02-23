from flask import Flask
from flask_restful import Api

from models import db
from views import ReservationView

app = None


def create_flask_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask_tutorial.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    app_context = app.app_context()
    app_context.push()

    add_urls(app)

    return app


def add_urls(app):
    api = Api(app)

    api.add_resource(ReservationView, "/reservation/create")


app = create_flask_app()

# Initialize database
db.init_app(app)
db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8081", debug=True)
