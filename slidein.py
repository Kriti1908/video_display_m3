import mysql.connector
from io import BytesIO
from PIL import Image, ImageOps
import numpy as np
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
from moviepy.video.fx.fadein import fadein
import mysql.connector
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
from moviepy.video.fx.rotate import rotate

def create_video_with_transitions(video_filename):
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nidhi&Kriti1911",
        database="iss_proj"
    )
    cursor = connection.cursor()

    # Query to select video from the database
    query = "SELECT video FROM videos WHERE filename = %s"

    # Execute the query
    cursor.execute(query, (video_filename,))

    # Fetch the video as a single blob
    video_blob = cursor.fetchone()[0]

    # Write the video blob to a temporary file
    with open("temp_video.mp4", "wb") as file:
        file.write(video_blob)

    # Close MySQL connection
    connection.close()

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
    final_clip.write_videofile("output_video_with_rotation_transition.mp4", codec='mpeg4')  # Adjust codec as needed

    print("Video with rotation transition created successfully.")

# Example usage
create_video_with_transitions('output_video_20240317111222.mp4')  # Replace 'output_video_20240317111222.mp4' with the actual video filename from your database