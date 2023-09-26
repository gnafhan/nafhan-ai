from flask import Flask
from dotenv import load_dotenv

from api.rating_prediction import app_routes
from api.rating_prediction.app_routes import rating_bp
from lib.mongodb_collection import close_mongodb_connection, connect_to_mongodb
from middleware.api_key import check_api_key

app = Flask(__name__)
db = connect_to_mongodb()
load_dotenv()

app.before_request(check_api_key)

@app.errorhandler(404)
def not_found(e):
    return {
        "status":404,
        "message":"Not Found"
    }, 404

app.register_blueprint(rating_bp, url_prefix='/api/predict/rating')


@app.teardown_appcontext
def close_db_connection(exception=None):
    close_mongodb_connection(db)

if __name__ == '__main__':
    app.run()