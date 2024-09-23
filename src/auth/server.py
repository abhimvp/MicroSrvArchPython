import os
import jwt,datetime # jwt is used to create and verify tokens , datetime is used to set the expiration time of the token
# os is used to interact with environment variables , jwt for json web token
from flask import Flask, request # we will use flask to create our server
from flask_mysqldb import MySQL # allow us to query msql db

# create a server - A FLASK Object
server = Flask(__name__)
mysql = MySQL(server) # can connect to our mysql db

# setUp config
server.config["MYSQL_HOST"]=os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"]=os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"]=os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"]=os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"]=os.environ.get("MYSQL_PORT")
# print(server.config["MYSQL_HOST"])

# create our routes
@server.route("/login",methods=["POST"])
def login():
    """ Flow : User is going to make a request to login route using his or her credentials (username,password) & check if that 
     user exists in our database if it does we consider user is authenticated & return Json Web Token which is going to be used by that 
      User to make requests to the API & the endpoints the user will have access to is determined by the permission here (authz) if the user is
       admin or not """
    auth = request.authorization # authorization provides the credentials from a basic Authentication header , when we send a request to this login route , we're going to need to provide a basic Authorization header which will contain a username and password , this request object has an attribute that gives access to that 
    if not auth:
        return "missing credentials", 401
    
    # check db for username and password
    cur = mysql.connection.cursor() # we will use this cursor to execute sql queries
    res = cur.execute("SELECT email, password FROM users WHERE email = %s", (auth.username,))

    if res > 0:
        user_row = cur.fetchone() # resolves to a tuple
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return create_jwt(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return "invalid credentials", 401
    
def create_jwt(username, secret,authz): # authz is whether the user is admin or not
    """we create a json web token with a given user &  secret & signing algorithm"""
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz
        },
        secret,
        algorithm="HS256"
    )


# create another route to validate jwts - which will be used by our APIGW to validate jwts sent within requests from the client to both upload  videos & dowload MP3S

@server.route("/validate", methods=["POST"])
def validate():
    """we will validate the jwt sent within the request to the APIGW &
      in the production we need to check the authentication scheme (bearer - contains token , basic - user credentials ) 
      present within the authorization header"""
    encoded_jwt = request.headers["Authorization"] # we will get the jwt from the authorization header of the request

    encoded_jwt=encoded_jwt.split(" ")[1] # assuming we are getting bearer[0] token[1] 

    if not encoded_jwt:
        return "missing credentials", 401

    # we will decode the jwt using the secret
    try:
        decoded = jwt.decode(encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"])
    except:
        return "not authorized", 403

    return decoded, 200


## configure our endpoint for the auth service 
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000) # allow our auth service to listen to any IP address on our host
