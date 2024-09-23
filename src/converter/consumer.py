import pika # to pull the messsages from queue
import os,sys,time
import pymongo
import gridfs # take the files from mongoDb & also upload the mp3 files to mongoDb
from convert import to_mp3 # module within that package

def main():
    client = pymongo.MongoClient('host.minikube.internal',27017) #gives access to host systems env 
    db_videos = client.videos
    db_mp3s= client.mp3s
    #gridfs is a module within pymongo
    fs_videos = gridfs.GridFS(db_videos) 
    fs_mp3s = gridfs.GridFS(db_mp3s)
    #connect to rabbitmq
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()


    def callback(ch , method , properties , body): # ch is channel
        err = to_mp3.start(body,fs_videos,fs_mp3s,ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag) # ack = acknowledge

    channel.basic_qos(prefetch_count=1)
        
    # create a configuration to consume from video queue
    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"),
        on_message_callback= callback # gets executed whenever a message is pulled off the queue - callback function
        
    )
    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming() # start consuming messages


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
