import mysql.connector
from io import BytesIO
from PIL import Image
import numpy as np
from moviepy.editor import ImageSequenceClip

# def create_video(list):
#     # Connect to MySQL database
#         connection = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="Nidhi&Kriti1911",
#             database="iss_proj"
#         )
#         cursor = connection.cursor()

#         # List to store images
#         images = []

#         # Query to select images from the database
#         for i in list:
#             query = "SELECT photo FROM photos WHERE filename=%s"

#             # Execute the query
#             cursor.execute(query,(i,))

#             # Iterate over the results and add images to list
#             for photo in cursor.fetchall():
#                 # Read image from bytes
#                 image = Image.open(BytesIO(photo[0]))

#                 # Resize image to a common size (e.g., 640x480)
#                 image = image.resize((640, 480))

#                 # Convert image to numpy array and add to list
#                 images.append(np.array(image))

#         # Create video from images
#         clip = ImageSequenceClip(images, fps=24)  # Adjust fps as needed

#         # Write video to file
#         clip.write_videofile('static/output_video2.mp4')

#         # Read the video file and convert it to base64
#         with open('static/output_video2.mp4', 'rb') as f:
#             video_blob = f.read()
#             video_base64 = base64.b64encode(video_blob).decode('utf-8')

#         # Insert the video into the database
#         insert_query = "INSERT INTO videos (username, filename, video) VALUES (%s, %s, %s)"
#         cursor.execute(insert_query, (username, 'output_video2.mp4', video_blob))

#         # Commit the transaction
#         connection.commit()
#         connection.close()

#         print("Video created successfully.")
#         return video_base64

def create_video(list):

    # Connect to MySQL database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nidhi&Kriti1911",
        database="iss_proj"
    )
    cursor = connection.cursor()

    # List to store images
    images = []

    # Query to select images from the database
    for i in list:
        query = "SELECT photo FROM photos WHERE filename=%s"

        # Execute the query
        cursor.execute(query,(i,))

        # Iterate over the results and store images
        for photo in cursor.fetchall():
            # Read image from bytes
            image = Image.open(BytesIO(photo[0]))

            # Resize image to a specific size (e.g., 640x480)
            image = image.resize((640, 480))

            # Convert image to numpy array and append to list
            images.append(np.array(image))

    # Create video from images
    clip = ImageSequenceClip(images, fps=1)  # Adjust fps as needed

    # Write video to file
    clip.write_videofile("static/output_video5.mp4", codec='mpeg4')  # Adjust codec as needed

    # Close MySQL connection
    connection.close()

    print("Video created successfully.")

create_video(['1.png','flower.png'])