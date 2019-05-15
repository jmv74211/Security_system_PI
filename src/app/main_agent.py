from flask import Flask, request, jsonify
from photo import Photo
from video import Video
import os, signal
import subprocess

#https://stackoverflow.com/questions/308999/what-does-functools-wraps-do
from functools import wraps
from login import authenticate_user

"""
    MAIN AGENT: Receive requests and interact with the rest of system elements .
"""


##############################################################################################

app = Flask(__name__)

# Motion agent path
motion_agent_path = "/home/jmv74211/git/Security_system_PI/src/app/motion_agent.py"

# Files path where save the generated files.
files_path = "/home/jmv74211/Escritorio/photo_files"

# Port where run this agent
running_port = 10000

# Alert flag, True if there is any to process, False otherwise
motion_agent_alert = False

# Path file that  has been captured in the alert
file_path_alert = ""

# Streaming server py path
streaming_server_path = "/home/jmv74211/git/Security_system_PI/src/app/pistream/streaming_server.py"


##############################################################################################

"""
    Decorator function to authenticate the access
"""
def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json()

        if data is not None and 'username' in data and 'password' in data:
            if authenticate_user(data['username'],data['password']):
                 return f(authentication_sucessfully=True, *args, **kwargs)
            else:
                return jsonify({'message' : 'Autentication is invalid!'}), 401
        else: 
           return jsonify({'message' : 'Autentication info is missing!'}), 401 
                
    return decorated

##############################################################################################       

"""
    Function to photo capture. Requires authentication.
"""

@app.route("/take_photo",methods=['POST'])
@authentication_required
def take_photo(authentication_sucessfully):
    camera_photo = Photo(file_path = files_path)
    camera_photo.set_configuration(resolution="best")
    camera_photo.take_photo()
    return jsonify({'status':'Photo has been taken'})

############################################################################################## 

"""
    Function to video capture. Requires authentication.
"""

@app.route("/record_video",methods=['POST'])
@authentication_required
def record_video(authentication_sucessfully):
    camera_video= Video(file_path = files_path)
    camera_video.set_configuration(resolution="best")
    data = request.get_json()
    
    # If recordtime is specified in the data request
    if data is not None and 'recordtime' in data and data['recordtime'] > 0:
        record_time = data['recordtime']
        if(record_time > 60000):
            record_time = 60000
        camera_video.record_video(record_time)
    # If is not specified, the default recordtime is 10 seconds.
    else:
        camera_video.record_video()
     
    # Convert video from .h264 to mp4 (readable video format in telegram)
    convert_video_to_mp4()
     
    return jsonify({'status':'Recorded!'})

##############################################################################################

"""
    Function to check the motion agent status. True if is running, False otherwise
"""

def check_status_motion_agent():
    #process = os.popen('ps -ax | grep "motion_agent" | grep -v grep | cut -d " " -f1')
    process = os.popen('pgrep -a python | grep "motion_agent" | cut -d " " -f1')
    pid_process=process.read()
    process.close()
    
    if(pid_process == ""):
        return False
    else:
        return True

############################################################################################## 

"""
    Function to activate the motion agent.
"""

@app.route("/activate_motion_agent",methods=['POST'])
@authentication_required
def activate_motion_agent(authentication_sucessfully):
    if not check_status_motion_agent():
        
        motion_agent_mode = "photo"
        data = request.get_json()
        if data is not None and 'motion_agent_mode' in data:
            if data['motion_agent_mode'] == "video":
                motion_agent_mode = "video"
                
        # Make a subprocess and redirect stdout
        subprocess.Popen(['python3', motion_agent_path, motion_agent_mode],stdout=subprocess.PIPE)
        #subprocess.Popen(['python3', motion_agent_path, motion_agent_mode])
        
        #if check_status_motion_agent():
        print("The motion agent in " + motion_agent_mode + " mode has been activated")
        return jsonify({'status':'The motion agent in ' + motion_agent_mode + ' mode has been activated sucessfully'})
        #else:
         #   return jsonify({'status':'ERROR: The motion agent could not been activated'})
    else:
        return jsonify({'status':'The motion agent was already activated!'})
         
##############################################################################################       

"""
    Function to deactivate the motion agent.
"""

@app.route("/deactivate_motion_agent",methods=['POST'])
@authentication_required
def deactivate_motion_agent(authentication_sucessfully):
    if check_status_motion_agent():
        process = os.popen('pgrep -a python | grep "motion_agent" | cut -d " " -f 1')
        pid_process = int(process.read())
        os.kill(pid_process, signal.SIGKILL)
        process.close()
        #if not check_status_motion_agent:
        print("The motion has been deactivated")
        return jsonify({'status':'The motion agent has been deactivated sucessfully'})
        #else:
         #   return jsonify({'status':'ERROR: The motion agent could not been deactivated'})
        
    else:
        return jsonify({'status':'The agent was already deactivated!'})
    
##############################################################################################    

"""
    Function to get the latest photo path.
"""

@app.route("/give_last_photo_path",methods=['GET'])
@authentication_required
def give_last_photo_path(authentication_sucessfully):
    process = os.popen('ls -pt ' + files_path  +' | grep -v / | grep ".jpg" | head -n 1')
    photo_name= process.read().rstrip('\n') # Reads the output and delete the \n character
    photo_path = files_path + "/" + photo_name
    print("It has been sended the last photo path")
    
    return jsonify({'response':photo_path})
    
##############################################################################################

"""
    Function to get the latest video path.
"""

@app.route("/give_last_video_path",methods=['GET'])
@authentication_required
def give_last_video_path(authentication_sucessfully):
    process = os.popen('ls -pt ' + files_path  +' | grep -v / | grep ".mp4" | head -n 1')
    video_name= process.read().rstrip('\n') # Reads the output and delete the \n character
    video_path = files_path + "/" +video_name
    print("It has been sended the last video path")
    
    return jsonify({'response':video_path})

##############################################################################################

"""
    Convert .h264 format into .mp4(format that a telegram client can read) .Need install gpac
"""
def convert_video_to_mp4():
    process1 = os.popen('ls -pt ' + files_path  +' | grep -v / | grep ".h264" | head -n 1')
    video_name= process1.read().rstrip('\n') # Reads the output and deletes the \n character
    video_name_converted = video_name[:-4] # Deletes h264
    video_name_converted += "mp4" # Adds new format
    
    video_name_old_path = files_path + "/" + video_name
    video_name_converted_path = files_path + "/" + video_name_converted
    
    # Make a subprocess. Father process waits until it finishes
    subprocess.call(['MP4Box','-add',video_name_old_path,video_name_converted_path])

    # Call delete video function
    delete_last_video_captured()
    print("Video has been converted to mp4")
 
##############################################################################################  
 
"""
    Delete last video that has been capturated. This is usually callled after a convert_video
    due to it duplicates the file.
""" 
def delete_last_video_captured():
    
    # Get the last video name captured
    process = os.popen('ls -pt ' + files_path  +' | grep -v / | grep ".h264"')
    video_name= process.read().rstrip('\n')
    path = files_path + "/" +video_name
    
    # Make a subprocess for removing. Father process waits until it finishes
    subprocess.call(['rm', path])
        

############################################################################################## 

"""
    Function to receive a motion agent photo alert
"""

@app.route("/generate_motion_agent_alert",methods=['POST'])
@authentication_required
def receive_file_motion_agent(authentication_sucessfully):
    global motion_agent_alert
    global file_path_alert
    
    data = request.get_json()
    
    print("Recibe alerta!")
    
    if data is not None and 'file_path' in data:
        file_path_alert = data['file_path']
        motion_agent_alert = 1
        return jsonify({'status':'The alert has been received'})
    else:
        return jsonify({'status':'Error, file path data is missing'}),400
        
##############################################################################################
    
"""
    Function check motion agent and send the response to requester
"""

@app.route("/check_motion_agent_alert",methods=['GET'])
@authentication_required
def check_motion_agent_alert(authentication_sucessfully):
    global motion_agent_alert
        
    if motion_agent_alert == 1:
        global file_path_alert
        motion_agent_alert = 0
        return jsonify({'alert': True, 'file_path': file_path_alert})
    else:
        return jsonify({'alert': False})
        
##############################################################################################

"""
    Function to check the motion agent status. True if is running, False otherwise
"""

def check_status_streaming_mode():
    process = os.popen('pgrep -a python | grep "streaming_server" | cut -d " " -f 1')
    pid_process=process.read()
    process.close()
    
    if(pid_process == ""):
        return False
    else:
        return True


##############################################################################################

"""
    Function to activate the streaming mode
"""

@app.route("/activate_streaming_mode",methods=['POST'])
@authentication_required
def activate_streaming_mode(authentication_sucessfully):
    if not check_status_streaming_mode():
                        
        # Make a subprocess and redirect stdout
        subprocess.Popen(['python3', streaming_server_path],stdout=subprocess.PIPE)
    
        print("The streaming mode " + streaming_server_path + " mode has been activated")
        
        return jsonify({'status':'The streaming mode has been activated sucessfully'})
    else:
        return jsonify({'status':'The streaming mode was already activated!'})
         
############################################################################################## 
    
"""
    Function to deactivate the streaming mode.
"""

@app.route("/deactivate_streaming_mode",methods=['POST'])
@authentication_required
def deactivate_streaming_mode(authentication_sucessfully):
    if check_status_streaming_mode():
        process = os.popen('pgrep -a python | grep "streaming_server" | cut -d " " -f 1')
        pid_process = int(process.read())
        os.kill(pid_process, signal.SIGKILL)
        process.close()
        print("The streaming mode has been deactivated")
        
        return jsonify({'status':'The streaming mode has been deactivated sucessfully'})

        
    else:
        return jsonify({'status':'The streaming mode was already deactivated!'})
    
##############################################################################################  

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=running_port, debug=True)
    
