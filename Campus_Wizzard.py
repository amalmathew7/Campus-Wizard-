import osimport customtkinter as tkfrom customtkinter import *import ollamaimport speech_recognition as srimport pyttsx3from gtts import gTTSfrom googletrans import Translatorfrom PIL import Image# Initialize componentsengine = pyttsx3.init()rec = sr.Recognizer()translator = Translator()# Available LanguagesLANGUAGES = {"English": "en", "Malayalam": "ml"}selected_language = StringVar(value="English")  # Default: English# Load Imagesimg = Image.open("mic.png")img2 = Image.open("cw.png")# Function to translate queries/responsesdef translate_text(text, src, dest):    return translator.translate(text, src=src, dest=dest).text# Function to process speech inputdef askk():    goask()    tb2.delete('1.0', END)    tb2.insert("0.0", "Listening...")    root.update()        lang_code = LANGUAGES[selected_language.get()]  # Get Selected Language Code    with sr.Microphone() as mic:        try:            audio = rec.listen(mic, timeout=5)  # 5-second timeout            ask = rec.recognize_google(audio, language=f"{lang_code}-IN")        except sr.UnknownValueError:            tb2.delete('1.0', END)            tb2.insert("0.0", "Could not understand, please try again.")            return        except sr.RequestError:            tb2.delete('1.0', END)            tb2.insert("0.0", "Speech service unavailable.")            return        except Exception as e:            tb2.delete('1.0', END)            tb2.insert("0.0", f"Error: {str(e)}")            return    tb2.delete('1.0', END)    tb2.insert("0.0", ask)    root.update()    # If Malayalam is selected, translate to English before sending to AI    if lang_code == "ml":        ask = translate_text(ask, "ml", "en")    waitt()    tb1.delete('1.0', END)    tb1.insert("0.0", "Generating...")    root.update()    # Send query to Llama3 Model    stream = ollama.chat(        model="cw7125-llama3",        messages=[{'role': 'user', 'content': ask}],        stream=True,    )    # Collect response    response = ''.join(chunk['message']['content'] for chunk in stream)    # Translate response back to Malayalam if needed    if lang_code == "ml":        response = translate_text(response, "en", "ml")    # Update UI    tb1.delete('1.0', END)    tb1.insert("0.0", response)    root.update()    # Speak Response    if switch.get() == 1:        speak_text(response, lang_code)    cmbck()    root.update()# Function to speak text using gTTSdef speak_text(text, lang_code):    tts = gTTS(text, lang=lang_code)    tts.save("response.mp3")    os.system("start response.mp3" if os.name == "nt" else "mpg321 response.mp3")# UI Setuproot = tk.CTk()root.geometry("800x600")root.title("CampusWiZZard AI Receptionist")frame = tk.CTkFrame(master=root)frame.pack(padx=60, pady=20, fill="both", expand=True)ext1 = tk.CTkButton(master=frame, height=20, width=40, text="", image=CTkImage(img2), hover_color="green", command=root.quit)ext1.pack()label = tk.CTkLabel(master=frame, text="CampusWiZZard 1.0", font=("Impact", 38), text_color="#33ACFF")label.pack(pady=10)label1 = tk.CTkLabel(master=frame, text="How can I help you today?", font=("Arial", 18))label1.pack(pady=10)tb1 = tk.CTkTextbox(master=frame, height=200, width=1000, font=("Arial", 14), fg_color="white", text_color="black", border_color="#33ACFF", border_width=4)tb1.pack(pady=2, padx=20)label2 = tk.CTkLabel(master=frame, text="Message CampusWiZZard", font=("Arial", 18))label2.pack(pady=10)tb2 = tk.CTkTextbox(master=frame, height=50, width=1000, font=("Arial", 14), fg_color="white", text_color="black", border_color="#33ACFF", border_width=4)tb2.pack(pady=5, padx=20)# Language Selection Dropdownlabel3 = tk.CTkLabel(master=frame, text="Select Language:", font=("Arial", 14))label3.pack(pady=5)language_dropdown = tk.CTkComboBox(master=frame, values=list(LANGUAGES.keys()), variable=selected_language)language_dropdown.pack(pady=5)mic = tk.CTkButton(master=frame, height=100, width=200, text="ASK", font=("Arial", 17), hover_color="green", image=CTkImage(img), command=askk, corner_radius=360)mic.pack(pady=10)switch = tk.CTkSwitch(master=frame, text="Talk Back")switch.pack(pady=10)ext = tk.CTkButton(master=frame, height=50, width=100, text="EXIT", font=("Arial", 12), hover_color="red", command=root.quit)ext.pack(padx=100)root.mainloop()