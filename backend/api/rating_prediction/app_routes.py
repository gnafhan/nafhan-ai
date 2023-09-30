from flask import Blueprint, request, jsonify
from lib.mongodb_collection import close_mongodb_connection, connect_to_mongodb
from bson import json_util, ObjectId
import pickle
import numpy as np
import json

rating_bp = Blueprint('predict_bp', __name__)

db = connect_to_mongodb()
@rating_bp.route('/', methods = ['GET'], defaults={'id': None})
@rating_bp.route('/<string:id>', methods = ['GET'])
def get_predicts(id):
    if id:
        try:
            collection = db["predictions"]
            predicts = collection.find({"_id": ObjectId(id)})
            close_mongodb_connection(db)

        except Exception as e :
            close_mongodb_connection(db)
            return f"Terjadi kesalahan saat mengambil data : {e}", 500
    else:
        if db:
            try:
                collection = db["predictions"]
                predicts = collection.find({})
                close_mongodb_connection(db)

            except Exception as e :
                close_mongodb_connection(db)
                return f"Terjadi kesalahan saat mengambil data : {e}", 500

    return jsonify({
        "status":{
            "code": 200,
            "message": "Success",
        },
        "data": json.loads(json_util.dumps(list(predicts)))}), 200

@rating_bp.route('/', methods=['POST'])
def rating_predict():
    # Get the data from the POST request.
    data = request.get_json()
    text = data.get('text')

    # Load the model
    model = pickle.load(open('api/rating_prediction/models/model.pkl','rb'))
    multi_model = pickle.load(open('api/rating_prediction/models/multi_model.pkl','rb'))
    
    sentiment = model.predict([text])
    sentiment_proba = model.predict_proba([text])
    emotion = multi_model.predict([text])
    emotion_proba = multi_model.predict_proba([text])

    emotion_list ={
        0: 'anger',
        1: 'fear',
        2: 'happy',
        3: 'love',
        4: 'sadness',
    }
    
    emotion_dict = {emotion_list[i]: emotion_proba[0][i] for i in range(len(emotion_list))}

    # Make prediction using model loaded from disk as per the data.
    result = {
        "input": f"{text}",
        "sentiment": "positive" if sentiment[0] == 1 else "negative",
        "sentiment_score": round(sentiment_proba[0][sentiment[0]]*100),
        "emotion": emotion_list[emotion[0]],
        "emotion_score": round(emotion_proba[0][emotion[0]]*100),
        "emotion_probability": emotion_dict
    }

    if db:
        try:
            collection = db["predictions"]
            inserted = collection.insert_one(json.loads(json_util.dumps(result)))
            result["_id"] = str(inserted.inserted_id)
            close_mongodb_connection(db)

        except Exception as e :
            close_mongodb_connection(db)
            return f"Terjadi kesalahan saat mengambil data : {e}", 500
        
    return jsonify({
        "status":{
            "code": 201,
            "message": "Success",
        },
        "data":result}), 201
