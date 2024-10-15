import os
import gridfs , json
import pika 
# gridfs allows us to store larger files in mongoDB , 
# pika is used to interface without queue , we're going to use a rabbitMQ service to store our messages 
from flask import Flask
from flask_pymongo import PyMongo # type: ignore
from auth import validate
from auth_svc import access
from storage import util
from flask import send_file

server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.interal:27017/videos" # mongodb endpoint to interface with mongodb - videos database
# host.minikube.internal gives access to our localhost from within oor kubNtes cluster 
mongo = PyMongo(server) # PyMongo is going to wrap our flask server , which will allows us to interface with mongoDB
fs = gridfs.GridFS(mongo.db) # gridfs is going to allow us to store larger files in mongoDB
# configure our rabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

@server.route('/login', methods=['POST'])
def login():
    """ this route communicate with our auth service to log the user in & assign a token to that user  """
    token,err = access.login(request) # returns a tuple from auth_svc package - access.py - login 
    if not err:
        return token
    else:
        return err
    
@server.route('/upload', methods=['POST'])
def upload():
    """ this route will handle the upload of files to our storage service """
    access,err = validate.token(request.headers.get('Authorization')) # validate module token function
    access = json.loads(access)

    if access["admin"]: # if user have access 
        if len(request.files) > 1 or len(request.files) < 1 :# we need to make sure a file need to be uploaded
            return "Only one file can be uploaded at a time",400
        
        # we should iterate through the key values in the request.files dictionary
        for _,f in request.files.items(): # _ is key , f is file
            err = util.upload(f,fs,channel,access)

            if err:
                return err       
            
        return "File uploaded successfully", 200
    else:
        return "Unauthorized access", 401
    
# download the mp3 created from video
@server.route('/download', methods=['GET'])
def download():
    pass

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=8080)