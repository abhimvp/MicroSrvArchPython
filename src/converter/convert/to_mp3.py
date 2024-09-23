import pika , json , tempfile , os
import bson.objectid as ObjectId
import moviepy.editor as mp # convert the videos to mp3

def start(message , fs_videos, fs_mp3, channel):
    message = json.loads(message) # load our message - essentialy make it into python obj

    # we want to write our content to empty temp file
    tf = tempfile.NamedTemporaryFile()
    # video contents
    out = fs_videos.get(ObjectId(message['video_file_id']))
    # add video contents to temp file
    tf.write(out.read())
    # create audio from temp video file
    audio_clip = mp.VideoFileClip(tf.name).audio
    tf.close() # close temp file

    # write audio to the file
    tf_path = tempfile.gettempdir() + f"/{message['video_file_id']}.mp3"
    audio_clip.write_audiofile(tf_path)

    # save the file to mongo
    f = open(tf_path, 'rb')
    data = f.read()
    fid = fs_mp3.put(data)
    f.close()
    os.remove(tf_path)

    message["mp3_fid"] = str(fid)

    # put the message on to mp3 queue
    try:
        channel.basic_publish(
            exchange='' ,
            routing_key=os.environ.get("MP3_QUEUE") ,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
            )
    except Exception as err:
        fs_mp3.delete(fid)
        return 'failed to publish message'

