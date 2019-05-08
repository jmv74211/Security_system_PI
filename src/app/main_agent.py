from flask import Flask, request, jsonify
from photo import Photo
from video import Video
import os, signal

#https://stackoverflow.com/questions/308999/what-does-functools-wraps-do
from functools import wraps
from login import authenticate_user

"""
    MAIN AGENT: Receive requests and interact with the rest of system elements .
"""


##############################################################################################

app = Flask(__name__)
motion_agent_path = "/home/jmv74211/Escritorio/motion_agent.py"
files_path = "/home/jmv74211/Escritorio/"
running_port = 10000

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
    camera_video.record_video()
    return jsonify({'status':'Recorded!'})

##############################################################################################

"""
    Function to check the motion agent status. True if is running, False otherwise
"""

def check_status_motion_agent():
    process = os.popen('ps -ax | grep "motion_agent" | grep -v grep | cut -d " " -f1')
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
        os.system('nohup python3 ' + motion_agent_path + ' &')
        #if check_status_motion_agent():
        print("The motion has been activated")
        return jsonify({'status':'The motion has been activated sucessfully'})
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
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=running_port, debug=True)
    