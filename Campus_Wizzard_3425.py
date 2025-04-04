import os
import customtkinter as tk
from customtkinter import *
import ollama
import speech_recognition as sr
import pyttsx3
from PIL import Image
from gtts import gTTS
from deep_translator import GoogleTranslator

# Load Images
img = Image.open("mic.png")
img2 = Image.open("cw.png")

# Initialize TTS and Speech Recognition
engine = pyttsx3.init()
rec = sr.Recognizer()

# Default Language Selection
selected_language = "en"


# Function to Translate Text
def translate_text(text, target_lang):
    return GoogleTranslator(source="auto", target=target_lang).translate(text)


# Function to Process Speech Input
def askk():
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


# Exit function
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
