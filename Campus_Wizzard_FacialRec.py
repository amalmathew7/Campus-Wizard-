import os
import cv2
import numpy as np
import customtkinter as tk
from customtkinter import *
import ollama
import speech_recognition as sr
import pyttsx3
from PIL import Image
from gtts import gTTS
from deep_translator import GoogleTranslator
import face_recognition

# Ensure base directory exists
BASE_DIR = "user_data"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Initialize TTS and Speech Recognition
engine = pyttsx3.init()
rec = sr.Recognizer()
selected_language = "en"

# Load Images
img = Image.open("mic.png")
img2 = Image.open("cw.png")


# Function to Translate Text
def translate_text(text, target_lang):
    return GoogleTranslator(source="auto", target=target_lang).translate(text)


# Face Recognition and Registration
def recognize_or_register():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Error capturing image.")
        return None

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if len(face_locations) == 0:
        print("No face detected.")
        return None

    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    if len(face_encodings) == 0:
        print("Face encoding failed.")
        return None

    known_faces = []
    known_users = []

    # Scan user_data folders for existing users
    for user_folder in os.listdir(BASE_DIR):
        user_face_path = os.path.join(BASE_DIR, user_folder, "face.jpg")
        if os.path.exists(user_face_path):
            user_face = face_recognition.load_image_file(user_face_path)
            encoding = face_recognition.face_encodings(user_face)
            if len(encoding) > 0:
                known_faces.append(encoding[0])
                known_users.append(user_folder)

    user_encoding = face_encodings[0]
    matches = face_recognition.compare_faces(known_faces, user_encoding)

    if True in matches:
        matched_index = matches.index(True)
        recognized_user = known_users[matched_index]
        print(f"User recognized: {recognized_user}")
        return recognized_user
    else:
        new_user_id = f"user_{len(known_users) + 1}"
        user_folder_path = os.path.join(BASE_DIR, new_user_id)
        os.makedirs(user_folder_path)  # Create a folder for the new user

        cv2.imwrite(os.path.join(user_folder_path, "face.jpg"), frame)
        print(f"New user registered as: {new_user_id}")
        return new_user_id


# Function to Process Speech Input
def askk():
    user_id = recognize_or_register()
    if user_id is None:
        return

    print("Campus Wizard - AI Receptionist")
    goask()
    print("Tell your query: ")

    tb2.delete('1.0', END)
    tb2.insert("0.0", "Listening...")
    root.update()

    with sr.Microphone() as mic:
        audio = rec.listen(mic)
        ask = rec.recognize_google(audio, language=selected_language)

    ask = ask.lower()
    tb2.delete('1.0', END)
    tb2.insert("0.0", ask)
    root.update()
    print("Heard: ", ask)

    result = ['']
    root.update()
    waitt()

    tb1.delete('1.0', END)
    tb1.insert("0.0", "Generating...")
    root.update()

    stream = ollama.chat(
        model="cw7125-llama3",
        messages=[{'role': 'user', 'content': ask}],
        stream=True,
    )

    print("Result: ")
    delimiter = ''
    for chunk in stream:
        result.append(chunk['message']['content'])
        print(chunk['message']['content'], end="")

        response_text = delimiter.join(result)
        translated_text = translate_text(response_text,
                                         selected_language) if selected_language != "en" else response_text

        tb1.delete('1.0', END)
        root.update()
        tb1.insert("0.0", translated_text)
        root.update()

    tb1.delete('1.0', END)
    tb1.insert("0.0", translated_text)
    root.update()

    if switch.get() == 1:
        speak(translated_text)

    # Save query and response in the user's folder
    user_folder_path = os.path.join(BASE_DIR, user_id)
    query_log_path = os.path.join(user_folder_path, "queries.txt")

    try:
        with open(query_log_path, "a", encoding="utf-8") as file:
            file.write(f"Q: {ask}\nA: {translated_text}\n\n")
        print(f"Query saved for {user_id} in {query_log_path}")
    except Exception as e:
        print(f"Error saving query: {e}")

    cmbck()
    root.update()


# Function to Speak the Response
def speak(text):
    tts = gTTS(text=text, lang=selected_language)
    tts.save("response.mp3")
    os.system("start response.mp3")  # For Windows


# Function to Handle UI Feedback
def goask():
    mic.configure(fg_color="green", text="LISTENING")
    tb2.configure(border_color="green")


def cmbck():
    mic.configure(fg_color="#33ACFF", text="ASK", text_color="white", hover_color="green")
    tb2.configure(border_color="#33ACFF")
    tb1.configure(border_color="#33ACFF")


def waitt():
    mic.configure(fg_color="yellow", text="WAIT", hover_color="red", text_color="black")
    tb1.configure(border_color="yellow")


# Function to Set Language from Dropdown
def set_language(choice):
    global selected_language
    selected_language = language_options[choice]
    print(f"Language changed to: {selected_language}")


# Function to Exit
def getout():
    exit(0)


# GUI Setup
tk.set_appearance_mode("dark")
root = tk.CTk()
root.geometry("800x600")
root.title("Campus Wizard")

frame = tk.CTkFrame(master=root)
frame.pack(padx=60, pady=20, fill="both", expand=True)

# Exit Button (Image)
ext1 = tk.CTkButton(master=frame, height=20, width=40, text="", font=("Arial", 12),
                    image=CTkImage(img2), hover_color="green", command=getout)
ext1.pack()

# Title
label = tk.CTkLabel(master=frame, text="CampusWiZZard 1.0", font=("Impact", 38), text_color="#33ACFF")
label.pack(pady=10)

label1 = tk.CTkLabel(master=frame, text="How can I help you today?", font=("Arial", 18))
label1.pack(pady=10)

# Response Box
tb1 = tk.CTkTextbox(master=frame, height=200, width=1000, font=("Arial", 14), corner_radius=20,
                    fg_color="white", text_color="black", border_color="#33ACFF", border_width=4, border_spacing=0)
tb1.pack(pady=2, padx=20)

label2 = tk.CTkLabel(master=frame, text="Message CampusWizzard", font=("Arial", 18))
label2.pack(pady=10)

# User Input Box
tb2 = tk.CTkTextbox(master=frame, height=50, width=1000, font=("Arial", 14), corner_radius=35,
                    fg_color="white", text_color="black", border_color="#33ACFF", border_width=4)
tb2.pack(pady=5, padx=20)

# Mic Button
mic = tk.CTkButton(master=frame, height=100, width=200, text="ASK", font=("Arial", 17), hover_color="green",
                   image=CTkImage(img), command=askk, corner_radius=360)
mic.pack(pady=10)

# Talk Back Switch
switch = tk.CTkSwitch(master=frame, text="Talk Back")
switch.pack(pady=10)

# Language Selection Dropdown
language_options = {"English": "en", "Malayalam": "ml"}
language_dropdown = tk.CTkOptionMenu(frame, values=list(language_options.keys()),
                                     command=lambda choice: set_language(choice))
language_dropdown.pack(pady=10)

# Exit Button
ext = tk.CTkButton(master=frame, height=50, width=100, text="EXIT", font=("Arial", 12), hover_color="red",
                   command=getout)
ext.pack(padx=100)

root.mainloop()
