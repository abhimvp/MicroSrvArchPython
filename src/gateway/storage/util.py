import pika , json

def upload(f,fs,channel,access):
    """
    what this upload function needs to do is 
    1. Upload the file to mongoDB database using gridfs
    2. once the file is uploaded successfully, we need to send a message to our RabbitMQ queue
    3. so that downstream service when they pull that message from the queue can process the upload by pulling it from mongoDB
    4. This queue is allowing us to create an asynchronous communication flow between our gateway service and the service that processes our videos
    5. This asynchronicity is going to allow us to avoid the need for our gateway service to wait for our internal service to process the video before being able to return a response to the client
    """
    try: # try to put our file into the mongoDB
        fileID = fs.put(f) # store the file in mongoDB returns a fileID
    except Exception as err: # if not successful , catch the error
        return "internal server error",500
    
    # If the file is successfully uploaded we need to create a message to put on to the queue

    message = {
        "video_file_id":str(fileID),
        "mp3_fid":None,
        "username":access["username"],
    }

    # try and put this message on to the queue
    try:
        channel.basic_publish(
            exchange='', # default exchange 
            routing_key='video', # this is going to be name of our queue
            body=json.dumps(message),      # dumps convert python object to json string
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ), # this is imp because we make sure that our messages are persisted in our queue in the event of a pod crash or restart of our pod

            )
    except:
        fs.delete(fileID) # delete the file from mongoDB - if there's no message on the queue for the file , but the file still exists in the DB , that file is never going to get processed
        return "internal server error",500 
    
    