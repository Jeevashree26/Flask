from flask import Flask,jsonify,request
from pyngrok import ngrok
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity,JWTManager
import os
from bson import ObjectId

# ngrok.set_auth_token=("2tFRAy8dGRfQlSWANRb5XGCPzor_5fHpJceR8NUMkiMQGFeSx")
# pulic_url = ngrok.connect(3000).public_url


uri = "mongodb+srv://Jeeva:pk3IEAaUtXE2AfQK@altimedesign.igecp.mongodb.net/?retryWrites=true&w=majority&appName=altimedesign"
app = Flask(__name__)
client = pymongo.MongoClient(uri)
db = client["altimedesign"]
app.config['JWT_SECRET_KEY'] = '234edvhji987654edxzw34rfvjgfdsert'
jwt=JWTManager(app)


@app.route("/register",methods=["POST"])
def register_user():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ("first_name", "last_name", "email", "password")):
            return jsonify({"message": "Invalid input"}), 400

        if db.test1.find_one({"email": data['email']}):
            return jsonify({"message": "User already exists"}), 400
        hash_password = generate_password_hash(data['password'])
        db.test1.insert_one({
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "email": data['email'],
            "password": hash_password
        })
        return jsonify({"message": "User registered successfully"}), 201
        
    except:
        raise Exception("Error has been Occured")


@app.route('/login', methods=['post'])
def login_user():
    data = request.get_json()
    user = db.test1.find_one({"email": data['email']})
    if user and check_password_hash(user['password'],data['password']):
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({"access_token":access_token}),200
    return jsonify({"message":"Invalid Credentials"}),401


@app.route('/createTemplate',methods=['POST'])
@jwt_required()
def createTemplate():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data or not all(k in data for k in ("template_name", "subject", "body")):
        return jsonify({"message": "Invalid input"}), 400
    db.templates.insert_one({
        "user_id": user_id,
        "template_name": data['template_name'],
        "subject": data['subject'],
        "body": data['body']
    })
    return jsonify({"message":"Template Created"}),201


@app.route('/getAllTemplate',methods=['GET'])
@jwt_required()
def getAllTemplate():
    user_id = get_jwt_identity()
    templates = list(db.templates.find({"user_id":user_id}))
    for template in templates:
        template["_id"] = str(template["_id"])
    return jsonify(templates),200


@app.route('/getTemplate/<template_id>',methods=['GET'])
@jwt_required()
def getTemplate(template_id):
    user_id = get_jwt_identity()
    try:
        object_id = ObjectId(template_id)
    except:
        return jsonify({"message": "Invalid template ID format"}), 400
    
    template = db.templates.find_one({"_id":object_id,"user_id":user_id})
    if not template:
        return jsonify({"message":"Template not Found"}),404
    template["_id"] = str(template["_id"])
    return jsonify(template),200


@app.route('/updateTemplate/<template_id>',methods=['PUT'])
@jwt_required()
def updateTemplate(template_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    updatedTemplate = {
        "template_name": data.get("template_name"),
        "subject": data.get("subject"),
        "body": data.get("body")
    }
    try:
        object_id = ObjectId(template_id)
    except:
        return jsonify({"message": "Invalid template ID format"}), 400
    result = db.templates.update_one({"_id":object_id,"user_id":user_id},{"$set": updatedTemplate})
    if result.matched_count == 0:
        return jsonify({"message": "Template not found or not authorized"}),404
    return jsonify({"message":"Template Updated"}),200


@app.route('/deleteTemplate/<template_id>', methods=['DELETE'])
@jwt_required()
def deleteTemplate(template_id):
    user_id = get_jwt_identity()
    try:
        object_id = ObjectId(template_id)
    except:
        return jsonify({"message": "Invalid template ID format"}), 400
    result = db.templates.delete_one({"_id": object_id, "user_id": user_id})
    if result.deleted_count == 0:
        return jsonify({"message":"Template not fount or not authorized"}),404
    return jsonify({"message":"Template Deleted"}),200


# print("access link",pulic_url)
if __name__ == "__main__":
    app.run(port=3000, debug=True)