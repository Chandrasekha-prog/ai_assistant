import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import requests
import json
import time
import re
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class JulieAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Julie - Smart Voice Assistant")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Initialize speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize Selenium WebDriver
        self.driver = None
        self.setup_selenium()
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        self.is_listening = False
        self.setup_ui()
        
    def setup_selenium(self):
        """Initialize Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--start-maximized")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.add_to_conversation("System", "Selenium browser started successfully!")
            
        except Exception as e:
            self.add_to_conversation("System", f"Selenium initialization failed: {e}")
            self.driver = None
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Julie - Smart Voice Assistant", font=("Arial", 16, "bold"), foreground="#8B008B")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Hello! I'm Julie, ready to help you!", foreground="#4B0082")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Browser status
        browser_status = "🟢 Connected" if self.driver else "🔴 Disconnected"
        self.browser_label = ttk.Label(main_frame, text=f"Browser: {browser_status}", foreground="blue")
        self.browser_label.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        self.listen_button = ttk.Button(control_frame, text="Talk to Julie", command=self.toggle_listening)
        self.listen_button.grid(row=0, column=0, padx=(0, 5))
        
        self.browser_button = ttk.Button(control_frame, text="Restart Browser", command=self.restart_browser)
        self.browser_button.grid(row=0, column=1, padx=(0, 5))
        
        self.info_button = ttk.Button(control_frame, text="Browser Info", command=self.show_browser_info)
        self.info_button.grid(row=0, column=2)
        
        # Conversation area - FIXED: Consistent naming
        conversation_label = ttk.Label(main_frame, text="Conversation with Julie:")
        conversation_label.grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        
        self.conversation_area = scrolledtext.ScrolledText(main_frame, width=80, height=15, state=tk.DISABLED)
        self.conversation_area.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        # Command examples with Selenium
        examples_label = ttk.Label(main_frame, text="Try these commands with Julie:")
        examples_label.grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
        
        examples_text = """
• "What time is it?" - Get current time
• "Search for python tutorials on Google" - Automated Google search
• "Find music videos on YouTube" - Automated YouTube search  
• "Look up artificial intelligence on Wikipedia" - Wikipedia search
• "Search for laptops on Amazon" - Amazon product search
• "Open YouTube and play first video" - Auto-play YouTube
• "Login to Gmail" - Gmail automation
• "Compose email" - Email automation
• "Click first result" - Click search results
• "Open calculator" - Open system calculator
• "Tell me a joke" - Hear a random joke
• "Exit" - Close the assistant
        """
        
        examples_display = tk.Text(main_frame, width=80, height=8, wrap=tk.WORD)
        examples_display.grid(row=7, column=0, columnspan=2, pady=(0, 10))
        examples_display.insert(tk.END, examples_text)
        examples_display.config(state=tk.DISABLED)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
    def restart_browser(self):
        """Restart the Selenium browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        self.setup_selenium()
        browser_status = "🟢 Connected" if self.driver else "🔴 Disconnected"
        self.browser_label.config(text=f"Browser: {browser_status}")
        
    def show_browser_info(self):
        """Show current browser information"""
        if self.driver:
            try:
                current_url = self.driver.current_url
                title = self.driver.title
                info = f"Current Page: {title}\nURL: {current_url}"
                self.add_to_conversation("Browser Info", info)
            except:
                self.add_to_conversation("Browser Info", "No active browser session")
        else:
            self.add_to_conversation("Browser Info", "Browser not initialized")
    
    def toggle_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.listen_button.config(text="Stop Listening")
            self.status_label.config(text="Julie is listening...", foreground="blue")
            self.add_to_conversation("Julie", "I'm listening, please speak your command.")
            self.speak("I'm listening, please speak your command.")
            # Start listening in a separate thread
            self.listening_thread = Thread(target=self.listen_loop)
            self.listening_thread.daemon = True
            self.listening_thread.start()
        else:
            self.is_listening = False
            self.listen_button.config(text="Talk to Julie")
            self.status_label.config(text="Julie is ready", foreground="#4B0082")
            self.add_to_conversation("Julie", "Stopped listening.")
            self.speak("Stopped listening.")
    
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
                self.add_to_conversation("Julie", "Sorry, I didn't understand that.")
                self.speak("Sorry, I didn't understand that.")
            except sr.RequestError as e:
                self.add_to_conversation("Julie", f"Error with speech recognition: {e}")
                self.speak("There was an error with speech recognition.")
            except Exception as e:
                self.add_to_conversation("Julie", f"Unexpected error: {e}")
    
    def process_command(self, command):
        response = "I'm Julie! I'm not sure how to help with that. Try asking me to search something or open a website."
        
        # Enhanced command processing with Selenium
        if "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p on %A, %B %d")
            response = f"The current time is {current_time}"
        
        # Selenium-powered search commands
        elif any(word in command for word in ["search for", "search", "find", "look up"]):
            response = self.selenium_search(command)
        
        # Selenium-powered open commands
        elif "open" in command:
            response = self.selenium_open(command)
        
        # Selenium interaction commands
        elif "click" in command or "play" in command:
            response = self.selenium_interact(command)
        
        # Email automation
        elif any(word in command for word in ["email", "compose", "gmail"]):
            response = self.selenium_email(command)
        
        elif "joke" in command:
            joke = self.get_joke()
            response = f"Here's a joke for you: {joke}"
        
        elif "weather" in command:
            response = "For weather information, please specify a location or enable location services."
        
        elif "your name" in command or "who are you" in command:
            response = "I'm Julie, your smart voice assistant! I can help you search the web, open websites, and automate tasks using Selenium."
        
        elif "exit" in command or "quit" in command or "stop" in command:
            response = "Goodbye! It was nice helping you!"
            self.add_to_conversation("Julie", response)
            self.speak(response)
            if self.driver:
                self.driver.quit()
            self.root.after(1000, self.root.destroy)
            return
        
        else:
            response = "I'm Julie! I can tell time, search the web, open websites, automate tasks with Selenium, tell jokes, and more!"
        
        self.add_to_conversation("Julie", response)
        self.speak(response)
    
    def selenium_search(self, command):
        """Perform automated search using Selenium"""
        if not self.driver:
            return "Selenium browser is not available. Please restart the browser."
        
        try:
            # Extract search platform and query
            platforms = {
                'google': ('https://www.google.com', 'textarea[name="q"], input[name="q"]'),
                'youtube': ('https://www.youtube.com', 'input[id="search"]'),
                'wikipedia': ('https://www.wikipedia.org', 'input[name="search"]'),
                'amazon': ('https://www.amazon.com', 'input[id="twotabsearchtextbox"]'),
                'github': ('https://www.github.com', 'input[name="q"]')
            }
            
            # Detect platform
            platform = None
            query = None
            
            for plat in platforms.keys():
                if plat in command:
                    platform = plat
                    break
            
            if not platform:
                platform = 'google'  # Default to Google
            
            # Extract search query
            if "search for" in command:
                query = command.split("search for")[-1].strip()
            elif "search" in command:
                query = command.split("search")[-1].strip()
            elif "find" in command:
                query = command.split("find")[-1].strip()
            elif "look up" in command:
                query = command.split("look up")[-1].strip()
            
            # Remove platform name from query
            if platform in query:
                query = query.replace(platform, "").strip()
            
            if not query:
                return f"What would you like me to search for on {platform}?"
            
            # Perform the search
            url, search_selector = platforms[platform]
            self.driver.get(url)
            time.sleep(2)
            
            # Find search box and enter query
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, search_selector))
            )
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)
            
            return f"✅ Successfully searched for '{query}' on {platform.title()}!"
            
        except Exception as e:
            return f"Search failed: {str(e)}"
    
    def selenium_open(self, command):
        """Open websites with Selenium automation"""
        if not self.driver:
            return "Selenium browser is not available."
        
        websites = {
            'youtube': 'https://www.youtube.com',
            'google': 'https://www.google.com',
            'gmail': 'https://mail.google.com',
            'github': 'https://www.github.com',
            'wikipedia': 'https://www.wikipedia.org',
            'amazon': 'https://www.amazon.com',
            'linkedin': 'https://www.linkedin.com',
            'facebook': 'https://www.facebook.com',
            'twitter': 'https://www.twitter.com'
        }
        
        for site, url in websites.items():
            if site in command:
                try:
                    self.driver.get(url)
                    time.sleep(3)
                    return f"✅ Opened {site.title()} with Selenium!"
                except Exception as e:
                    return f"Failed to open {site}: {str(e)}"
        
        # Check for calculator
        if "calculator" in command:
            if os.name == 'nt':  # Windows
                os.system('calc')
                return "Opening calculator"
            else:  # macOS and Linux
                os.system('gnome-calculator' if os.name == 'posix' else 'kcalc')
                return "Opening calculator"
        
        return "I can open YouTube, Google, Gmail, GitHub, Wikipedia, Amazon, LinkedIn, Facebook, Twitter, or calculator."
    
    def selenium_interact(self, command):
        """Interact with web elements using Selenium"""
        if not self.driver:
            return "Selenium browser is not available."
        
        try:
            # Click first search result
            if "first" in command and any(word in command for word in ["click", "play", "open"]):
                # Try different selectors for first result
                selectors = [
                    'h3',  # Google results
                    '#video-title',  # YouTube results
                    'a[href*="/wiki/"]',  # Wikipedia results
                    '.s-result-item h2 a'  # Amazon results
                ]
                
                for selector in selectors:
                    try:
                        first_result = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        first_result.click()
                        time.sleep(3)
                        return "✅ Clicked the first result!"
                    except:
                        continue
                
                return "Could not find a result to click."
            
            # Play YouTube video
            elif "play" in command and "youtube" in command:
                try:
                    play_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '.ytp-play-button'))
                    )
                    play_button.click()
                    return "✅ Playing YouTube video!"
                except:
                    return "Could not find play button on YouTube."
            
            return "Specify what to interact with (e.g., 'click first result', 'play video')"
            
        except Exception as e:
            return f"Interaction failed: {str(e)}"
    
    def selenium_email(self, command):
        """Handle email-related automation"""
        if not self.driver:
            return "Selenium browser is not available."
        
        try:
            if "compose" in command or "write" in command:
                self.driver.get("https://mail.google.com")
                time.sleep(3)
                
                # Try to click compose button
                try:
                    compose_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"][gh="cm"]'))
                    )
                    compose_btn.click()
                    time.sleep(2)
                    return "✅ Opened Gmail compose window!"
                except:
                    return "Could not find compose button. You might need to login first."
            
            elif "login" in command:
                self.driver.get("https://mail.google.com")
                time.sleep(3)
                return "✅ Navigated to Gmail login page. Please enter your credentials."
            
            else:
                self.driver.get("https://mail.google.com")
                time.sleep(3)
                return "✅ Opened Gmail!"
                
        except Exception as e:
            return f"Email automation failed: {str(e)}"
    
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
            "What do you call a fake noodle? An impasta!",
            "Why did the computer go to the doctor? It had a virus!"
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
        """Add message to conversation area - FIXED: Consistent method name"""
        self.conversation_area.config(state=tk.NORMAL)
        
        # Color code different speakers
        if speaker == "Julie":
            tag = "julie"
            self.conversation_area.tag_config(tag, foreground="#8B008B", font=("Arial", 10, "bold"))
        elif speaker == "System":
            tag = "system"
            self.conversation_area.tag_config(tag, foreground="green", font=("Arial", 9, "bold"))
        elif speaker == "Browser Info":
            tag = "browser"
            self.conversation_area.tag_config(tag, foreground="purple", font=("Arial", 9))
        else:
            tag = "user"
            self.conversation_area.tag_config(tag, foreground="darkgreen")
        
        self.conversation_area.insert(tk.END, f"{speaker}: ", tag)
        self.conversation_area.insert(tk.END, f"{text}\n")
        self.conversation_area.see(tk.END)
        self.conversation_area.config(state=tk.DISABLED)
    
    def __del__(self):
        """Cleanup when application closes"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = JulieAssistant(root)
        
        def on_closing():
            if app.driver:
                app.driver.quit()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting Julie: {e}")
        input("Press Enter to exit...")