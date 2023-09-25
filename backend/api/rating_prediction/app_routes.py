from flask import Blueprint

predict_bp = Blueprint('predict_bp', __name__)

@predict_bp.route('/')
def predict():
    return 'Hello, World!'