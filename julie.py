import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyttsx3
import datetime
import webbrowser
import os
import requests
import subprocess
import sys
from threading import Thread
import time

class JulieAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Julie - Smart Voice Assistant")
        self.root.geometry("800x650")
        self.root.resizable(True, True)
        
        # Initialize speech engine with Julie's voice
        self.engine = None
        self.setup_voice()
        
        self.is_listening = False
        self.setup_ui()
        
    def setup_voice(self):
        """Initialize and configure Julie's voice"""
        try:
            self.engine = pyttsx3.init()
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            
            # Try to find a female voice for Julie
            female_voice_found = False
            for voice in voices:
                if any(female_indicator in voice.name.lower() for female_indicator in 
                      ['female', 'woman', 'girl', 'zira', 'karen', 'veena', 'tessa']):
                    self.engine.setProperty('voice', voice.id)
                    female_voice_found = True
                    print(f"Julie's voice set to: {voice.name}")
                    break
            
            if not female_voice_found and voices:
                self.engine.setProperty('voice', voices[0].id)
            
            # Configure Julie's speech properties
            self.engine.setProperty('rate', 160)
            self.engine.setProperty('volume', 0.8)
            
        except Exception as e:
            print(f"Voice initialization failed: {e}")
            self.engine = None
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title with Julie's name
        title_label = ttk.Label(main_frame, text="Julie - Your Smart Voice Assistant", 
                               font=("Arial", 18, "bold"), foreground="#8B008B")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Hello! I'm Julie, ready to help you!", 
                                     foreground="#4B0082")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Command input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=2, pady=(0, 15), sticky=(tk.W, tk.E))
        
        ttk.Label(input_frame, text="Type your command:").grid(row=0, column=0, sticky=tk.W)
        
        self.command_var = tk.StringVar()
        self.command_entry = ttk.Entry(input_frame, textvariable=self.command_var, width=60)
        self.command_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.command_entry.bind('<Return>', lambda e: self.process_text_command())
        
        ttk.Button(input_frame, text="Execute", command=self.process_text_command).grid(row=1, column=1)
        
        # Quick commands frame
        quick_frame = ttk.LabelFrame(main_frame, text="Quick Actions", padding="10")
        quick_frame.grid(row=3, column=0, columnspan=2, pady=(0, 15), sticky=(tk.W, tk.E))
        
        quick_commands = [
            ("🔍 Search Google", "search python programming on google"),
            ("🎥 YouTube Search", "search music videos on youtube"),
            ("📚 Wikipedia", "search artificial intelligence on wikipedia"),
            ("🛒 Amazon", "search laptops on amazon"),
            ("💼 LinkedIn", "search jobs on linkedin"),
            ("🐙 GitHub", "search python projects on github"),
            ("📰 News", "search technology news on google news"),
            ("🎵 Spotify", "play songs on spotify"),
            ("📧 Gmail", "open gmail and compose email"),
            ("🧮 Calculator", "open calculator")
        ]
        
        for i, (text, cmd) in enumerate(quick_commands):
            btn = ttk.Button(quick_frame, text=text, 
                           command=lambda c=cmd: self.quick_command(c))
            btn.grid(row=i//5, column=i%5, padx=2, pady=2, sticky=tk.W+tk.E)
        
        # Conversation area
        conversation_frame = ttk.LabelFrame(main_frame, text="Conversation with Julie", padding="10")
        conversation_frame.grid(row=4, column=0, columnspan=2, pady=(0, 15), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.conversation_area = scrolledtext.ScrolledText(conversation_frame, width=80, height=15, 
                                                          font=("Arial", 10))
        self.conversation_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        input_frame.columnconfigure(0, weight=1)
        quick_frame.columnconfigure(tuple(range(5)), weight=1)
        conversation_frame.columnconfigure(0, weight=1)
        conversation_frame.rowconfigure(0, weight=1)
        
    def quick_command(self, command):
        """Handle quick command buttons"""
        self.command_var.set(command)
        self.process_text_command()
    
    def process_text_command(self):
        command = self.command_var.get().strip()
        if not command:
            return
            
        self.add_to_conversation("You", command)
        self.command_var.set("")
        self.status_label.config(text="Julie is processing your command...", foreground="blue")
        
        # Process in thread to avoid UI freezing
        thread = Thread(target=self._process_command_thread, args=(command,))
        thread.daemon = True
        thread.start()
    
    def _process_command_thread(self, command):
        response = self.process_command(command)
        self.root.after(0, self._update_ui_after_command, response)
    
    def _update_ui_after_command(self, response):
        self.add_to_conversation("Julie", response)
        self.status_label.config(text="Ready for next command", foreground="#4B0082")
        self.speak(response)
    
    def process_command(self, command):
        """Process commands with intelligent website and app navigation"""
        command_lower = command.lower()
        response = "I'll help you with that!"
        
        try:
            # SEARCH COMMANDS
            if any(word in command_lower for word in ["search", "find", "look for"]):
                response = self.handle_search_command(command_lower)
            
            # OPEN/LAUNCH COMMANDS
            elif any(word in command_lower for word in ["open", "launch", "start"]):
                response = self.handle_open_command(command_lower)
            
            # PLAY MUSIC/VIDEO
            elif any(word in command_lower for word in ["play", "listen to", "watch"]):
                response = self.handle_play_command(command_lower)
            
            # SPECIFIC WEBSITE ACTIONS
            elif any(word in command_lower for word in ["email", "compose", "write mail"]):
                response = self.handle_email_command(command_lower)
            
            # CALCULATOR
            elif "calculator" in command_lower:
                response = self.open_calculator()
            
            # TIME
            elif "time" in command_lower:
                current_time = datetime.datetime.now().strftime("%I:%M %p on %A, %B %d")
                response = f"The current time is {current_time}"
            
            # HELP
            elif "help" in command_lower or "what can you do" in command_lower:
                response = self.get_help_message()
            
            else:
                response = "I'm not sure what you want me to do. Try saying 'search for something on Google' or 'open YouTube'"
                
        except Exception as e:
            response = f"Sorry, I encountered an error: {str(e)}"
        
        return response
    
    def handle_search_command(self, command):
        """Handle search commands for different platforms"""
        # Define search platforms and their URLs
        search_platforms = {
            "google": "https://www.google.com/search?q={}",
            "youtube": "https://www.youtube.com/results?search_query={}",
            "wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search={}",
            "amazon": "https://www.amazon.com/s?k={}",
            "github": "https://github.com/search?q={}",
            "linkedin": "https://www.linkedin.com/search/results/all/?keywords={}",
            "twitter": "https://twitter.com/search?q={}",
            "reddit": "https://www.reddit.com/search/?q={}",
            "bing": "https://www.bing.com/search?q={}",
            "duckduckgo": "https://duckduckgo.com/?q={}",
            "news": "https://news.google.com/search?q={}",
            "google news": "https://news.google.com/search?q={}",
            "spotify": "https://open.spotify.com/search/{}"
        }
        
        # Extract search query and platform
        query = self.extract_search_query(command)
        platform = self.detect_search_platform(command)
        
        if not query:
            return "What would you like me to search for? Please specify your search terms."
        
        if platform in search_platforms:
            search_url = search_platforms[platform].format(query.replace(' ', '+'))
            webbrowser.open(search_url)
            return f"Searching for '{query}' on {platform.title()}"
        else:
            # Default to Google search
            search_url = search_platforms["google"].format(query.replace(' ', '+'))
            webbrowser.open(search_url)
            return f"Searching for '{query}' on Google"
    
    def extract_search_query(self, command):
        """Extract the search query from command"""
        # Remove search-related phrases
        search_phrases = ["search", "search for", "find", "look for", "on google", "on youtube", 
                         "on wikipedia", "on amazon", "on github", "on linkedin", "on twitter",
                         "on reddit", "on bing", "on duckduckgo", "on news", "on spotify"]
        
        query = command
        for phrase in search_phrases:
            query = query.replace(phrase, "")
        
        return query.strip()
    
    def detect_search_platform(self, command):
        """Detect which platform to search on"""
        platforms = {
            "google": any(word in command for word in ["google", "web", "internet"]),
            "youtube": any(word in command for word in ["youtube", "video"]),
            "wikipedia": any(word in command for word in ["wikipedia", "wiki"]),
            "amazon": any(word in command for word in ["amazon", "shop", "buy"]),
            "github": any(word in command for word in ["github", "code", "programming"]),
            "linkedin": any(word in command for word in ["linkedin", "job", "career"]),
            "twitter": any(word in command for word in ["twitter", "tweet"]),
            "reddit": any(word in command for word in ["reddit"]),
            "bing": any(word in command for word in ["bing"]),
            "duckduckgo": any(word in command for word in ["duckduckgo"]),
            "news": any(word in command for word in ["news", "headlines"]),
            "spotify": any(word in command for word in ["spotify", "music", "song"])
        }
        
        for platform, condition in platforms.items():
            if condition:
                return platform
        
        return "google"  # Default platform
    
    def handle_open_command(self, command):
        """Handle commands to open websites or applications"""
        websites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "gmail": "https://mail.google.com",
            "github": "https://www.github.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.twitter.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "wikipedia": "https://www.wikipedia.org",
            "amazon": "https://www.amazon.com",
            "netflix": "https://www.netflix.com",
            "whatsapp": "https://web.whatsapp.com",
            "reddit": "https://www.reddit.com",
            "stackoverflow": "https://stackoverflow.com",
            "spotify": "https://open.spotify.com"
        }
        
        apps = {
            "calculator": self.open_calculator,
            "notepad": self.open_notepad,
            "paint": self.open_paint,
            "file explorer": self.open_file_explorer,
            "browser": self.open_browser
        }
        
        # Check for websites
        for site_name, url in websites.items():
            if site_name in command:
                webbrowser.open(url)
                return f"Opening {site_name.title()} for you!"
        
        # Check for applications
        for app_name, app_function in apps.items():
            if app_name in command:
                return app_function()
        
        return "I can open websites like YouTube, Google, Gmail, etc. or apps like calculator, notepad. What would you like me to open?"
    
    def handle_play_command(self, command):
        """Handle play commands for music and videos"""
        if "youtube" in command or "video" in command:
            query = command.replace("play", "").replace("on youtube", "").replace("video", "").strip()
            if query:
                webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
                return f"Playing '{query}' on YouTube"
            else:
                webbrowser.open("https://www.youtube.com")
                return "Opening YouTube for you!"
        
        elif "spotify" in command or "music" in command or "song" in command:
            query = command.replace("play", "").replace("on spotify", "").replace("music", "").replace("song", "").strip()
            if query:
                webbrowser.open(f"https://open.spotify.com/search/{query.replace(' ', '%20')}")
                return f"Searching for '{query}' on Spotify"
            else:
                webbrowser.open("https://open.spotify.com")
                return "Opening Spotify for you!"
        
        else:
            # Default to YouTube for play commands
            query = command.replace("play", "").strip()
            if query:
                webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
                return f"Playing '{query}' on YouTube"
            else:
                webbrowser.open("https://www.youtube.com")
                return "Opening YouTube for you!"
    
    def handle_email_command(self, command):
        """Handle email-related commands"""
        if "compose" in command or "write" in command or "new email" in command:
            webbrowser.open("https://mail.google.com/mail/?view=cm&fs=1&tf=1")
            return "Opening Gmail compose window for you to write a new email!"
        else:
            webbrowser.open("https://mail.google.com")
            return "Opening your Gmail inbox!"
    
    def open_calculator(self):
        """Open calculator application"""
        try:
            if os.name == 'nt':  # Windows
                os.system('calc')
                return "Opening Windows Calculator"
            elif os.name == 'posix':  # Linux
                if self.is_command_available('gnome-calculator'):
                    os.system('gnome-calculator')
                    return "Opening GNOME Calculator"
                elif self.is_command_available('kcalc'):
                    os.system('kcalc')
                    return "Opening KCalc"
                else:
                    webbrowser.open("https://www.google.com/search?q=calculator")
                    return "Opening online calculator in your browser"
            else:  # macOS
                os.system('open -a Calculator')
                return "Opening Calculator"
        except:
            webbrowser.open("https://www.google.com/search?q=calculator")
            return "Opening online calculator in your browser"
    
    def open_notepad(self):
        """Open text editor"""
        try:
            if os.name == 'nt':  # Windows
                os.system('notepad')
                return "Opening Notepad"
            elif os.name == 'posix':  # Linux
                if self.is_command_available('gedit'):
                    os.system('gedit')
                    return "Opening Gedit"
                elif self.is_command_available('kate'):
                    os.system('kate')
                    return "Opening Kate"
                else:
                    os.system('nano')
                    return "Opening Nano text editor"
            else:  # macOS
                os.system('open -a TextEdit')
                return "Opening TextEdit"
        except:
            return "Could not open text editor"
    
    def open_paint(self):
        """Open paint application"""
        try:
            if os.name == 'nt':  # Windows
                os.system('mspaint')
                return "Opening Paint"
            else:
                return "Paint is only available on Windows. Try another application."
        except:
            return "Could not open Paint"
    
    def open_file_explorer(self):
        """Open file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.system('explorer')
            elif os.name == 'posix':  # Linux
                os.system('nautilus' if self.is_command_available('nautilus') else 'dolphin' if self.is_command_available('dolphin') else 'thunar')
            else:  # macOS
                os.system('open .')
            return "Opening file explorer"
        except:
            return "Could not open file explorer"
    
    def open_browser(self):
        """Open web browser"""
        webbrowser.open("https://www.google.com")
        return "Opening your web browser"
    
    def is_command_available(self, command):
        """Check if a command is available on the system"""
        try:
            if os.name == 'nt':
                result = subprocess.run(['where', command], capture_output=True, text=True)
            else:
                result = subprocess.run(['which', command], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def get_help_message(self):
        """Return help message with all capabilities"""
        return """I can help you with many tasks! Here's what I can do:

🔍 SEARCH COMMANDS:
• "Search python on Google" - Web search
• "Find music videos on YouTube" - Video search
• "Look up AI on Wikipedia" - Encyclopedia search
• "Search laptops on Amazon" - Shopping search
• "Find jobs on LinkedIn" - Professional search

🎯 OPENING APPS & WEBSITES:
• "Open YouTube" - Video platform
• "Open Gmail" - Email service
• "Open calculator" - System calculator
• "Open notepad" - Text editor

🎵 MEDIA COMMANDS:
• "Play songs on Spotify" - Music streaming
• "Play comedy videos on YouTube" - Video streaming

📧 EMAIL COMMANDS:
• "Compose email" - New email window
• "Open Gmail" - Email inbox

Try these examples or create your own commands!"""
    
    def speak(self, text):
        """Make Julie speak the text"""
        if not self.engine:
            return
        
        def speak_thread():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Julie's voice error: {e}")
        
        speech_thread = Thread(target=speak_thread)
        speech_thread.daemon = True
        speech_thread.start()
    
    def add_to_conversation(self, speaker, text):
        """Add message to conversation area"""
        self.conversation_area.config(state=tk.NORMAL)
        
        if speaker == "Julie":
            tag = "julie"
            self.conversation_area.tag_config(tag, foreground="#8B008B", font=("Arial", 10, "bold"))
        else:
            tag = "user"
            self.conversation_area.tag_config(tag, foreground="#2E8B57")
        
        self.conversation_area.insert(tk.END, f"{speaker}: ", tag)
        self.conversation_area.insert(tk.END, f"{text}\n\n")
        self.conversation_area.see(tk.END)
        self.conversation_area.config(state=tk.DISABLED)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        style = ttk.Style()
        style.theme_use('clam')
        app = JulieAssistant(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting Julie: {e}")
        input("Press Enter to exit...")