from flask_cors import CORS
import os
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify, abort, session, get_flashed_messages, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from mysql.connector import Error
import base64
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
from moviepy.editor import ImageSequenceClip, VideoFileClip, ImageClip, concatenate_videoclips
from moviepy.video.fx.fadein import fadein
from datetime import datetime
from moviepy.video.fx.rotate import rotate

mycon=mysql.connector.connect(host="localhost",user="root",password="Nidhi&Kriti1911",database="iss_proj")
mycursor=mycon.cursor()

app = Flask(__name__)
CORS(app,supports_credentials = True)

app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_COOKIE_SECURE'] = False # Only for development, set to True for production
app.secret_key = 'your_secret_key_here'
app.config['JWT_ACCESS_COOKIE_PATH'] = '/user'

jwt = JWTManager(app)
video_in_database=""
video_timestamp=""

# ussername=""

# MySQL Configuration
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Nidhi&Kriti1911",
    database="iss_proj"
)

# Function to execute MySQL queries
def execute_query(query, values=None):
    cursor = db_connection.cursor(dictionary=True)
    if values:
        cursor.execute(query, values)
    else:
        cursor.execute(query)
    db_connection.commit()
    cursor.close()

# Secret key for session management
app.secret_key = os.urandom(24)

def convertphotoToBinaryData(file_val):
    return file_val.read()

# Function to check if user is logged in
def is_logged_in():
    return 'logged_in' in session

@app.route('/')
def final():
    return render_template('final.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

# Route for user registration
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert user into database
        execute_query("INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username, hashed_password))

        # Redirect to login page
        return redirect(url_for('login'))

    return render_template('signup.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Fetch form data
        username = request.form['username']
        session['username'] = username
        print("session data: ",session)
        password = request.form['password']

        # Get user by email
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        
        if(user['username']=="admin"):
                response = make_response(redirect(url_for('admin_page')))

        if user and check_password_hash(user['password'], password):
            # Generate JWT token
    
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            print(session)
            
            if(user['username']=="admin"):
                response = make_response(redirect(url_for('admin_page')))
            else: 
                access_token = create_access_token(identity=username, expires_delta=timedelta(days=7))   
                response = make_response(redirect(url_for('photos', username=username)))
                response.set_cookie('access_token_cookie', value=access_token, max_age=3600, httponly=True)
            return response
        flash("Invalid","error")    
            
            
    return render_template('login.html')

@app.route('/admin')
def admin_page():
    if 'logged_in' in session and session['logged_in'] and session['username'] == "admin":
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT username, name, email FROM users")
        users = cursor.fetchall()
        cursor.close()
        return render_template('admin.html', users=users)
    else:
        return redirect(url_for('login'))

@app.route('/photos/<username>',  methods=['GET', 'POST'])
@jwt_required()
def photos(username):
    current_user = get_jwt_identity()
    print("Current user:", current_user)
    if current_user != username:
        print("Error: Current user does not match requested user.")
        abort(403)  # Return a forbidden error (HTTP status code 403)
    return render_template('photos.html',username=username)
    
@app.route('/recieve', methods=['POST'])
def receive_array():
    print("Receiving files...")
    print(session)
    username = session["username"]
    if 'uploaded_files[]' in request.files:
        files = request.files.getlist('uploaded_files[]')
        for file in files:
            print("File received:", file.filename)
            file_data=convertphotoToBinaryData(file)
            execute_query("INSERT INTO photos (username, filename, photo) VALUES (%s, %s, %s)", (username, file.filename, file_data))
            print("inserted")
        return 'Files received successfully!'
    else:
        print("Gandu kya kiya")
        return 'No files received in the request.'

@app.route('/videos/<username>', methods=['GET', 'POST'])
@jwt_required()
def re_direct(username):
    current_user = get_jwt_identity()
    print("Current user:", current_user)
    print("Username: ",username)
    if current_user != username:
        print("Error: Current user does not match requested user.")
        abort(403)  # Return a forbidden error (HTTP status code 403)
        
    try:
        # Fetch photos from the database for the given username
        cursor = db_connection.cursor()
        user_id = session["user_id"]
        print("Username inside try: ",user_id)
        cursor.execute("SELECT filename, photo FROM photos WHERE username = %s", (username,))
        photos = cursor.fetchall()
        if(photos):
            print("YES mc")
        cursor.close()
        
        modified_photos = []
        for photo in photos:
            filename = photo[0]
            photo_data = photo[1]
            
            if isinstance(photo_data, bytes):
                photo_base64 = base64.b64encode(photo_data).decode('utf-8')
                modified_photo = {
                    'filename': filename,
                    'photo': photo_base64
                }
                modified_photos.append(modified_photo)
                
        

# Assign the modified photos list to the template
        return render_template('videos.html', username=username, photos=modified_photos)

    except Exception as e:
        return f"An error occurred: {str(e)}"

        

@app.route('/videos')
@jwt_required()
def video():
    access_token_cookie = request.cookies.get('access_token_cookie')
    if access_token_cookie:
        try:
            decoded = decode_token(access_token_cookie)
            username = decoded.get('sub')
            return redirect(url_for('re_direct', username=username))
        except Exception as e:
            print("Error decoding token:", e)

    else:
        # Handle the case when the access token is missing
        return jsonify({'error': 'Access token missing'}), 401

@app.route('/search')
def search_images():
    query = request.args.get('query')
    username = session.get('username')

    if query:
        # Query the database for filenames matching the search query
        cursor = db_connection.cursor()
        cursor.execute("SELECT filename FROM photos WHERE username = %s AND filename LIKE %s", (username, query + '%'))
        matched_images = [image[0] for image in cursor.fetchall()]
        cursor.close()

        # Return the matched images to the frontend
        return jsonify(success=True, images=matched_images)
    else:
        # Handle empty search query
        return jsonify(success=True, images=[])

  
    
    
@app.route('/save_selected_photos', methods=['POST'])
def save_selected_photos():
    print('******')
    data = request.json
    selected_filenames = data.get('filenames', [])
    print("Selected filenames:", selected_filenames)
    username=session["username"]

    def create_video(list):
    # Connect to MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Nidhi&Kriti1911",
            database="iss_proj"
        )
        cursor = connection.cursor()

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        video_filename = f'output_video_{timestamp}.mp4'

        # List to store images
        images = []

        # Query to select images from the database
        for i in list:
            query = "SELECT photo FROM photos WHERE filename=%s"

            # Execute the query
            cursor.execute(query,(i,))

            # Iterate over the results and add images to list
            for photo in cursor.fetchall():
                # Read image from bytes
                image = Image.open(BytesIO(photo[0]))

                # Resize image to a common size (e.g., 640x480)
                image = image.resize((1000, 850))

                # Convert image to numpy array and add to list
                images.append(np.array(image))

        # Create video from images
        clip = ImageSequenceClip(images, fps=1)  # Adjust fps as needed

        # Write video to file
        clip.write_videofile(f'static/{video_filename}')

        # Read the video file and convert it to base64
        with open(f'static/{video_filename}', 'rb') as f:
            video_blob = f.read()
            video_base64 = base64.b64encode(video_blob).decode('utf-8')

        # Insert the video into the database
        insert_query = "INSERT INTO videos (username, filename, video) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (username, video_filename, video_blob))

        # Commit the transaction
        connection.commit()
        connection.close()
        video_url = url_for('static', filename=video_filename)
        
        print("Video created successfully.")

        session['video_filename'] = video_filename
        session['video_timestamp'] = timestamp
        return video_url
    video_url = create_video(selected_filenames)
    
    print("Video URL:", video_url)
    return jsonify({'video_url': video_url})

# print("video in database",video_in_database)

@app.route('/add_transition', methods=['GET'])
def add_transition():
    # connection = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="Nidhi&Kriti1911",
    #     database="iss_proj"
    # )
    # cursor = connection.cursor()
    username=session["username"]
    video_in_database=session['video_filename']
    video_timestamp = session['video_timestamp']

    print("video in database",video_in_database)
    print("video timestamp",video_timestamp)

    # Query to select video from the database
    query = "SELECT video FROM videos WHERE filename = %s"

    # Execute the query
    mycursor.execute(query, (video_in_database,))

    # Fetch the video as a single blob
    video_blob = mycursor.fetchone()[0]

    # Write the video blob to a temporary file
    with open("temp_video.mp4", "wb") as file:
        file.write(video_blob)

    # Close MySQL connection
    # connection.close()

    # Read the temporary video file as a VideoFileClip
    video_clip = VideoFileClip("temp_video.mp4")

    # Break down the video into frames
    frames = [frame for frame in video_clip.iter_frames()]

    # Convert frames to ImageClips with transitions
    clips_with_transitions = []
    for frame in frames:
        # Convert frame to ImageClip with transition and add to list
        clip = ImageClip(np.array(frame), duration=1).fx(fadein, duration=1)  # Adjust duration as needed

        clips_with_transitions.append(clip)

    # Concatenate the clips with transitions
    final_clip = concatenate_videoclips(clips_with_transitions, method="compose")

    # Set fps for the final_clip (assuming 24 fps for example)
    final_clip.fps = 24  # You can adjust the fps as needed

    # Write video with transitions to file
    final_clip.write_videofile(f"static/output_video_with_fade_{video_timestamp}.mp4")  # Adjust codec as needed

    with open(f"static/output_video_with_fade_{video_timestamp}.mp4","rb") as ofile:
        video_blob = ofile.read()
        query2 = "INSERT INTO videos (username, filename, video) VALUES (%s, %s, %s)"
        mycursor.execute(query2, (username, f"static/output_video_with_fade_{video_timestamp}.mp4", video_blob))

    video_in_database = f"output_video_with_fade_{video_timestamp}.mp4"

    print("Video with transitions created successfully.")
    return jsonify({'video_url': url_for('static', filename=f"output_video_with_fade_{video_timestamp}.mp4")})


@app.route('/add_transition_rotate', methods=['GET'])
def add_transition_rotate():
    # Connect to MySQL database
    # connection = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="Nidhi&Kriti1911",
    #     database="iss_proj"
    # )
    # cursor = connection.cursor()

    username=session["username"]
    video_in_database=session['video_filename']
    video_timestamp = session['video_timestamp']

    # Query to select video from the database
    query = "SELECT video FROM videos WHERE filename = %s"

    # Execute the query
    mycursor.execute(query, (video_in_database,))

    # Fetch the video as a single blob
    video_blob = mycursor.fetchone()[0]

    # Write the video blob to a temporary file
    with open("temp_video.mp4", "wb") as file:
        file.write(video_blob)

    # Close MySQL connection
    # connection.close()

    # Read the temporary video file as a VideoFileClip
    video_clip = VideoFileClip("temp_video.mp4")

    # Break down the video into frames
    frames = [frame for frame in video_clip.iter_frames()]

    # Calculate duration for each frame
    frame_duration = video_clip.duration / len(frames)

    # Convert frames to ImageClips with transitions
    clips_with_transitions = []
    for i, frame in enumerate(frames):
        # Convert frame to ImageClip
        frame_clip = ImageClip(frame, duration=frame_duration)
        # Rotate frame into view over the duration of the clip
        clip = rotate(frame_clip, lambda t: 360 * t / frame_duration, unit='deg')  # Rotate frame from 0 to 360 degrees over the duration of the frame
        clips_with_transitions.append(clip)

    # Concatenate the clips with transitions
    final_clip = concatenate_videoclips(clips_with_transitions, method="compose")

    # Set fps for the final_clip (assuming 24 fps for example)
    final_clip.fps = 24  # You can adjust the fps as needed

    # Write video with transitions to file
    final_clip.write_videofile(f"static/output_video_with_rotation_transition{video_timestamp}.mp4")  # Adjust codec as needed
    
    with open(f"static/output_video_with_rotation_transition{video_timestamp}.mp4","rb") as ofile:
        video_blob = ofile.read()
        query2 = "INSERT INTO videos (username, filename, video) VALUES (%s, %s, %s)"
        mycursor.execute(query2, (username, f"static/output_video_with_rotation_transition{video_timestamp}.mp4", video_blob))

    video_in_database = f"output_video_with_rotation_transition{video_timestamp}.mp4"

    print("Video with rotation transition created successfully.")
    return jsonify({'video_url': url_for('static', filename=f"output_video_with_rotation_transition{video_timestamp}.mp4")})

# Example usage
# create_video_with_transitions('output_video_20240317111222.mp4')  # Replace 'output_video_20240317111222.mp4' with the actual video filename from your database

if __name__ == '__main__':
    app.run(debug=True)