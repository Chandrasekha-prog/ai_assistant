import tkinter as tk
from tkinter import ttk, scrolledtext
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import requests
import json
from threading import Thread
import time

class VoiceAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Assistant")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Initialize speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        self.is_listening = False
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Voice Assistant", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Listen button
        self.listen_button = ttk.Button(main_frame, text="Start Listening", command=self.toggle_listening)
        self.listen_button.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Conversation area
        conversation_label = ttk.Label(main_frame, text="Conversation:")
        conversation_label.grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        self.conversation_area = scrolledtext.ScrolledText(main_frame, width=60, height=15, state=tk.DISABLED)
        self.conversation_area.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        # Command examples
        examples_label = ttk.Label(main_frame, text="Try saying:")
        examples_label.grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        
        examples_text = """
• "What time is it?" - Get current time
• "Search for artificial intelligence" - Web search
• "Open YouTube" - Open website
• "Tell me a joke" - Hear a random joke
• "What's the weather?" - Get weather information
• "Open calculator" - Open system calculator
• "Exit" - Close the assistant
        """
        
        examples_display = tk.Text(main_frame, width=60, height=8, wrap=tk.WORD)
        examples_display.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        examples_display.insert(tk.END, examples_text)
        examples_display.config(state=tk.DISABLED)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
    def toggle_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.listen_button.config(text="Stop Listening")
            self.status_label.config(text="Listening...", foreground="blue")
            self.add_to_conversation("Assistant", "I'm listening...")
            # Start listening in a separate thread
            self.listening_thread = Thread(target=self.listen_loop)
            self.listening_thread.daemon = True
            self.listening_thread.start()
        else:
            self.is_listening = False
            self.listen_button.config(text="Start Listening")
            self.status_label.config(text="Ready", foreground="green")
            self.add_to_conversation("Assistant", "Stopped listening.")
    
    def listen_loop(self):
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Recognize speech
                command = self.recognizer.recognize_google(audio).lower()
                self.add_to_conversation("You", command)
                self.process_command(command)
                
            except sr.WaitTimeoutError:
                # No speech detected, continue listening
                pass
            except sr.UnknownValueError:
                self.add_to_conversation("Assistant", "Sorry, I didn't understand that.")
                self.speak("Sorry, I didn't understand that.")
            except sr.RequestError as e:
                self.add_to_conversation("Assistant", f"Error with speech recognition: {e}")
                self.speak("There was an error with speech recognition.")
            except Exception as e:
                self.add_to_conversation("Assistant", f"Unexpected error: {e}")
    
    def process_command(self, command):
        response = "I'm not sure how to help with that."
        
        if "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The current time is {current_time}"
        
        elif "search for" in command:
            query = command.replace("search for", "").strip()
            if query:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                response = f"Searching for {query}"
            else:
                response = "What would you like me to search for?"
        
        elif "open" in command:
            site = command.replace("open", "").strip()
            if "youtube" in site:
                webbrowser.open("https://www.youtube.com")
                response = "Opening YouTube"
            elif "google" in site:
                webbrowser.open("https://www.google.com")
                response = "Opening Google"
            elif "gmail" in site:
                webbrowser.open("https://www.gmail.com")
                response = "Opening Gmail"
            elif "calculator" in site:
                if os.name == 'nt':  # Windows
                    os.system('calc')
                else:  # macOS and Linux
                    os.system('gnome-calculator' if os.name == 'posix' else 'kcalc')
                response = "Opening calculator"
            else:
                response = f"I can open YouTube, Google, Gmail, or calculator. Which one would you like?"
        
        elif "joke" in command:
            joke = self.get_joke()
            response = joke
        
        elif "weather" in command:
            # This is a simple implementation - you might want to add location detection
            response = "For weather information, please specify a location or enable location services."
        
        elif "exit" in command or "quit" in command or "stop" in command:
            response = "Goodbye!"
            self.add_to_conversation("Assistant", response)
            self.speak(response)
            self.root.after(1000, self.root.destroy)
            return
        
        else:
            response = "I can tell time, search the web, open websites, tell jokes, and more. Try saying 'what can you do?'"
        
        self.add_to_conversation("Assistant", response)
        self.speak(response)
    
    def get_joke(self):
        try:
            response = requests.get("https://official-joke-api.appspot.com/random_joke")
            if response.status_code == 200:
                joke_data = response.json()
                return f"{joke_data['setup']} ... {joke_data['punchline']}"
        except:
            pass
        
        # Fallback jokes if API fails
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!"
        ]
        import random
        return random.choice(jokes)
    
    def speak(self, text):
        def speak_thread():
            self.engine.say(text)
            self.engine.runAndWait()
        
        # Run speech in a separate thread to avoid blocking the UI
        speech_thread = Thread(target=speak_thread)
        speech_thread.daemon = True
        speech_thread.start()
    
    def add_to_conversation(self, speaker, text):
        self.conversation_area.config(state=tk.NORMAL)
        self.conversation_area.insert(tk.END, f"{speaker}: {text}\n")
        self.conversation_area.see(tk.END)
        self.conversation_area.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAssistant(root)
    root.mainloop()