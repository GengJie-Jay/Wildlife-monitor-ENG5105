#====================================#
# Date: 2023.8.19
#====================================#
#!/usr/bin/env python #for linux
import os
from importlib import import_module
from flask import Flask, render_template, Response, jsonify, session, redirect, url_for, flash, request
from functools import wraps
from camera_opencv import Camera
import pyaudio
from flask_mail import Mail, Message
import time
import threading
#import wave
#import sys
#import math
from PIL import Image
import io
import sounddevice as sd
import math
import struct

#====================================#
# Cross Platform Test
#====================================#
win_linux = 1 # 0: windows 1: linux
if win_linux:
    from PWM_servo import PWM_init, PWMx_Adj, PWMy_Adj, soft_move
    from ultrasound import ultrasound_init, checkdist, dist_output
else:
    pass

#====================================#
# Website Initialization
#====================================#
# root user
users = [
    {
        'username': 'root',
        'password': 'root'
    }
]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'login' # secret key
mail = Mail(app) # instantiate the mail class

# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'jgen0006@student.monash.edu'
app.config['MAIL_PASSWORD'] = 'ueinpnxmawglpuvt'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
SOUND_THRESHOLD = 0.01
email_delays = []  # 用于存储延迟时间的列表

#====================================#
# Login Requirement
#====================================#

@app.before_request
def login_require():
    if request.path == '/live_video':
        if session.get('user', None):
            pass
        else:
            print('redirect to login')
            return redirect(url_for('login'))

#====================================#
# Login Page (default page)
#====================================#
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username", None)
        password = request.form.get('password', None)

        for user in users:
            if user['username'] == username and user['password'] == password:
                session['user'] = username
                print("Find user!!")
                return redirect(url_for('live_video'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')


#====================================#
# Register Page
#====================================#
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username", None)
        password = request.form.get('password', None)

        for user in users:
            if user['username'] == username:
                return render_template('register.html', message="用户%s已经存在" % (username))
        else:
            users.append(dict(username=username, password=password))
            return redirect(url_for('login'))
    return render_template('register.html')

#====================================#
# Logout
#====================================#
@app.route('/logout')
def logout():
    session.pop('user')
    print("logout success")
    return redirect(url_for('login'))


#====================================#
# Live Streaming Video Page
#====================================#
@app.route('/live_video')
def live_video():
    """Video streaming home page."""
    return render_template('live_video.html')

def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'
@app.route('/get_distance')
def get_distance():
    distance = checkdist()
    #print(distance)# Assuming this function returns a distance in cm or any unit you want.
    return jsonify({"distance": distance})


def send_warning_email(image_path):
    with app.app_context():
        try:
            print('Sending Email')
            msg = Message(
                'Warning: Object Detected Close',
                sender='jgen0006@student.monash.edu',
                recipients=['jgen0006@student.monash.edu']
            )
            msg.body = 'An object was detected closer than 1m!'
            msg.html = """
            <p>An object was detected closer than 1m!</p>
            <p>Click <a href="http://172.20.10.5:5000/live_video">here</a> to view first link.</p>
            <p>Click <a href="http://172.20.10.5:8421/#/">here</a> to view second link.</p>
            """
            with app.open_resource(image_path) as fp:
                msg.attach(image_path, "image/jpeg", fp.read())  # 将图片附加到邮件中
            mail.send(msg)
        except Exception as e:

            print(f"Error sending email: {str(e)}")

def dist_output():
    while True:
        distance = checkdist()
        if distance < 1:  # 1代表1米，假设距离返回的单位是m
            # 捕获当前帧并保存为图片
            frame = Camera().get_frame()
            image = Image.open(io.BytesIO(frame))
            image_path = "captured_image.jpg"
            image.save(image_path)
            
            # 发送警告邮件
            send_warning_email(image_path)
        time.sleep(5)
'''
def dist_output():
    global email_delays

    while True:
        distance = checkdist()
        if distance < 1:  # 100代表1米，假设距离返回的单位是cm
            start_time = time.time()
            frame = Camera().get_frame()
            image = Image.open(io.BytesIO(frame))
            image_path = "captured_image.jpg"
            image.save(image_path)# 记录当前时间
            send_warning_email(image_path)
            end_time = time.time()  # 再次记录时间
            delay = end_time - start_time
            email_delays.append(delay)  # 将延迟时间添加到列表中

            # 如果列表长度达到20，保存数据并清空列表
            if len(email_delays) >= 20:
                with open("email_delays.txt", "w") as f:
                    for delay in email_delays:
                        f.write(str(delay) + "\n")
                email_delays.clear()  # 清空列表，准备下一轮数据

        time.sleep(5)

'''
@app.route('/audio_feed')
def audio_feed():
    def sound():
        wav_header = genHeader(RATE, BIT_PER_SAMPLE, CHANNELS)

        stream = audio_source.open(format = FORMAT, 
                                   channels = CHANNELS,
                                   rate = RATE, 
                                   input = True, 
                                   input_device_index = 1,
                                   frames_per_buffer = CHUNK)
        
        print("recording...")
        first_run = True
        while True:
           if first_run:
               data = wav_header + stream.read(CHUNK)
               first_run = False
           else:
               data = stream.read(CHUNK, exception_on_overflow=False)
           
           # Check sound intensity and send email if it's above a threshold.
           intensity = sound_intensity(data)
           #print(intensity)
           if intensity > SOUND_THRESHOLD:
               frame = Camera().get_frame()
               image = Image.open(io.BytesIO(frame))
               image_path = "captured_image.jpg"
               image.save(image_path)
            
               # 发送警告邮件
               send_warning_email(image_path)
               
           
           yield(data)
        time.sleep(5)
    
    return Response(sound())
def sound_intensity(data):
      """Calculate the RMS of the audio chunk."""
      count = len(data)/2
      format = "%dh"%(count)
      shorts = struct.unpack(format, data)
      sum_squares = 0.0
      for sample in shorts:
        n = sample * (1.0/32768) # Convert to range [-1, 1]
        sum_squares += n*n
      return math.sqrt(sum_squares / count)
      # Return some response to indicate that the route is working
      #return "Monitoring sound for triggers...", 200
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

#====================================#
# Live Streaming Audio Page
#====================================#
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
BIT_PER_SAMPLE = 16

audio_source = pyaudio.PyAudio()

# generate wave header
def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o

#@app.route('/audio_feed')

#====================================#
# Servo Motor Controller
#====================================#
current_angle_x = 0  # X servo motor default angle
current_angle_y = 0  # Y servo motor default angle

@app.route('/up_func')
def up_func():
    global current_angle_y
    target_angle = max(current_angle_y - 10, -90)
    for angle in soft_move("decrease", current_angle_y, target_angle):
        if win_linux:
            PWMy_Adj(angle)
        else:
            pass
    current_angle_y = target_angle
    return f"Moved Up to {current_angle_y} degrees"

@app.route('/down_func')
def down_func():
    global current_angle_y
    target_angle = min(current_angle_y + 10, 90)
    for angle in soft_move("increase", current_angle_y, target_angle):
        if win_linux:
            PWMy_Adj(angle)
        else:
            pass
    current_angle_y = target_angle
    return f"Moved Up to {current_angle_y} degrees"

@app.route('/left_func')
def left_func():
    global current_angle_x
    target_angle = min(current_angle_x + 10, 90)
    for angle in soft_move("increase", current_angle_x, target_angle):
        if win_linux:
            PWMx_Adj(angle)
        else:
            pass
    current_angle_x = target_angle
    return f"Moved Right to {current_angle_x} degrees"

@app.route('/right_func')
def right_func():
    global current_angle_x
    target_angle = max(current_angle_x - 10, -90)
    for angle in soft_move("decrease", current_angle_x, target_angle):
        if win_linux:
            PWMx_Adj(angle)
        else:
            pass
    current_angle_x = target_angle
    return f"Moved Left to {current_angle_x} degrees"
 
#====================================#
# Email
#====================================#
@app.route('/Email')

def Email():
    try:
        print('Sending Email')
        msg = Message(
            'Hello',
            sender='jgen0006@student.monash.edu',
            recipients=['jgen0006@student.monash.edu']
        )
        msg.body = 'Hello Flask message sent from Flask-Mail'
        mail.send(msg)
     

        return 'Sent'
    except Exception as e:
        return f'Error sending email: {str(e)}'

    except Exception as e:
        print(f'Error sending email: {str(e)}')




#====================================#
if __name__ == '__main__':
    if win_linux:
        PWM_init()
        ultrasound_init()
        dist_out = threading.Thread(target=dist_output)
        dist_out.start()
    else:
        pass
    app.run(host='0.0.0.0', threaded=True)