from flask import Flask
from api.rating_prediction import app_routes
from api.rating_prediction.app_routes import predict_bp

app = Flask(__name__)

@app.errorhandler(404)
def not_found(e):
    return {
        "status":404,
        "message":"Not Found"
    }, 404

app.register_blueprint(predict_bp, url_prefix='/api/rating_prediction')
