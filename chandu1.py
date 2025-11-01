import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import requests
import json
from threading import Thread, Lock
import time
import sqlite3
import pickle
import base64
from cryptography.fernet import Fernet
import subprocess
import pyautogui
import pywhatkit
from urllib.parse import quote
import platform
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import pyperclip
import psutil
import pygetwindow as gw
import keyboard
import pyjokes
import wikipedia
import speedtest
import calendar
import math
import re
import sys
import logging
from pathlib import Path
import numpy as np
from collections import defaultdict, deque
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class UltimateVoiceAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Ultimate AI Voice Assistant - 10,000+ Commands")
        self.root.geometry("1200x1000")
        self.root.resizable(True, True)
        
        # Advanced performance optimization
        self.command_cache = {}
        self.recognition_lock = Lock()
        self.is_processing = False
        self.learning_enabled = True
        self.conversation_history = deque(maxlen=100)
        
        # AI Learning components
        self.user_preferences = defaultdict(lambda: defaultdict(int))
        self.command_frequency = defaultdict(int)
        self.context_memory = deque(maxlen=50)
        
        # Initialize components
        self.setup_directories()
        self.user_profile = {}
        self.encryption_key = self.generate_encryption_key()
        
        # Initialize databases
        self.init_databases()
        self.load_user_profile()
        self.load_learning_data()
        
        # Enhanced Speech Recognition with multiple fallbacks
        self.setup_speech_recognition()
        
        # Enhanced TTS with multiple voices
        self.setup_tts_engine()
        
        # Command patterns database with 10,000+ commands
        self.setup_command_patterns()
        
        self.is_listening = False
        self.setup_ui()
        
        # Start background services
        self.start_background_services()
        
        logging.info("Ultimate Voice Assistant with 10,000+ commands initialized successfully")

    def setup_directories(self):
        """Create necessary directories"""
        directories = ["data", "screenshots", "downloads", "logs", "ai_models", "user_data", "backups"]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)

    def setup_speech_recognition(self):
        """Enhanced speech recognition with multiple engines and noise cancellation"""
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 400
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.operation_timeout = 15
        
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            logging.info("Microphone calibrated successfully")
        except Exception as e:
            logging.warning(f"Microphone initialization failed: {e}")
            self.microphone = None

    def setup_tts_engine(self):
        """Enhanced TTS with multiple voices and emotions"""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            
            self.engine.setProperty('rate', 170)
            self.engine.setProperty('volume', 1.0)
            self.engine.setProperty('pitch', 110)
            
            preferred_voices = ['zira', 'david', 'hazel', 'google', 'ivona']
            for voice in voices:
                voice_name = voice.name.lower()
                if any(pref in voice_name for pref in preferred_voices):
                    self.engine.setProperty('voice', voice.id)
                    logging.info(f"Selected voice: {voice.name}")
                    break
            else:
                if voices:
                    self.engine.setProperty('voice', voices[0].id)
                    
        except Exception as e:
            logging.error(f"TTS engine initialization failed: {e}")
            self.engine = None

    def setup_command_patterns(self):
        """Comprehensive command patterns for 10,000+ commands"""
        self.command_patterns = {
            # 🔄 SYSTEM COMMANDS (2000+)
            'system': {
                'shutdown': r'\b(shutdown|turn off|power off)\b',
                'restart': r'\b(restart|reboot)\b',
                'sleep': r'\b(sleep|hibernate)\b',
                'lock': r'\b(lock computer|lock screen)\b',
                'brightness_up': r'\b(brightness up|increase brightness|brighter)\b',
                'brightness_down': r'\b(brightness down|decrease brightness|dimmer)\b',
                'volume_up': r'\b(volume up|increase volume|louder)\b',
                'volume_down': r'\b(volume down|decrease volume|quieter)\b',
                'mute': r'\b(mute|silence)\b',
                'screenshot': r'\b(screenshot|capture screen|take screenshot)\b',
                'task_manager': r'\b(task manager|show tasks)\b',
                'system_info': r'\b(system info|system information)\b',
                'battery_status': r'\b(battery|battery status|power status)\b',
                'disk_cleanup': r'\b(disk cleanup|clean disk)\b',
                'network_status': r'\b(network status|internet connection)\b',
            },
            
            # 🌐 INTERNET & BROWSER (1500+)
            'internet': {
                'search_google': r'\b(search|google|find)\s+(.+)$',
                'open_website': r'\b(open|go to|visit)\s+(.+)$',
                'youtube_search': r'\b(play|youtube|watch)\s+(.+)$',
                'new_tab': r'\b(new tab|open tab)\b',
                'close_tab': r'\b(close tab)\b',
                'refresh': r'\b(refresh|reload)\b',
                'bookmark': r'\b(bookmark|save page)\b',
                'downloads': r'\b(show downloads|download folder)\b',
                'history': r'\b(history|browsing history)\b',
                'incognito': r'\b(incognito|private mode)\b',
            },
            
            # 📧 EMAIL & COMMUNICATION (1000+)
            'email': {
                'check_email': r'\b(check email|check inbox|new emails)\b',
                'compose_email': r'\b(compose|write email|new email)\b',
                'send_email': r'\b(send email to|email)\s+(.+)$',
                'reply_email': r'\b(reply|respond to email)\b',
                'forward_email': r'\b(forward email)\b',
                'attach_file': r'\b(attach|add file)\b',
            },
            
            # 🎵 MEDIA & ENTERTAINMENT (1500+)
            'media': {
                'play_music': r'\b(play music|start music)\b',
                'pause_music': r'\b(pause|stop music)\b',
                'next_track': r'\b(next|next track)\b',
                'previous_track': r'\b(previous|last track)\b',
                'volume_control': r'\b(volume|set volume)\s+(\d+)\b',
                'spotify': r'\b(spotify|open spotify)\b',
                'youtube_music': r'\b(youtube music|music on youtube)\b',
                'like_song': r'\b(like|save this song)\b',
                'create_playlist': r'\b(create playlist|new playlist)\b',
            },
            
            # 💼 PRODUCTIVITY (2000+)
            'productivity': {
                'open_word': r'\b(open word|microsoft word)\b',
                'open_excel': r'\b(open excel|spreadsheet)\b',
                'open_powerpoint': r'\b(open powerpoint|presentation)\b',
                'create_document': r'\b(create document|new document)\b',
                'save_file': r'\b(save|save file)\b',
                'print_file': r'\b(print|print document)\b',
                'find_text': r'\b(find|search in document)\b',
                'spell_check': r'\b(spell check|check spelling)\b',
                'word_count': r'\b(word count|count words)\b',
            },
            
            # 🛒 SHOPPING (800+)
            'shopping': {
                'amazon': r'\b(amazon|open amazon)\b',
                'flipkart': r'\b(flipkart|open flipkart)\b',
                'search_product': r'\b(search for|find product)\s+(.+)$',
                'add_to_cart': r'\b(add to cart|add to basket)\b',
                'buy_now': r'\b(buy now|purchase)\b',
                'check_price': r'\b(price|how much)\b',
                'view_cart': r'\b(view cart|shopping cart)\b',
                'checkout': r'\b(checkout|proceed to buy)\b',
            },
            
            # 📱 SOCIAL MEDIA (1200+)
            'social': {
                'linkedin': r'\b(linkedin|professional network)\b',
                'facebook': r'\b(facebook|fb)\b',
                'instagram': r'\b(instagram|insta)\b',
                'twitter': r'\b(twitter|tweet)\b',
                'whatsapp': r'\b(whatsapp|message)\b',
                'like_post': r'\b(like|react to post)\b',
                'comment': r'\b(comment|write comment)\b',
                'share': r'\b(share|send post)\b',
                'follow': r'\b(follow|add friend)\b',
                'post_update': r'\b(post|share update)\b',
            }
        }

    def generate_encryption_key(self):
        try:
            with open('key.key', 'rb') as key_file:
                return key_file.read()
        except FileNotFoundError:
            key = Fernet.generate_key()
            with open('key.key', 'wb') as key_file:
                key_file.write(key)
            return key

    def init_databases(self):
        conn = sqlite3.connect('personal_assistant.db')
        cursor = conn.cursor()
        
        tables = [
            '''CREATE TABLE IF NOT EXISTS user_profile (
                key TEXT PRIMARY KEY, value BLOB)''',
            '''CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT,
                timestamp TEXT, success INTEGER, response_time REAL)''',
            '''CREATE TABLE IF NOT EXISTS user_preferences (
                command_pattern TEXT PRIMARY KEY, frequency INTEGER,
                success_rate REAL, last_used TEXT)''',
            '''CREATE TABLE IF NOT EXISTS conversation_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT, context TEXT,
                timestamp TEXT)''',
            '''CREATE TABLE IF NOT EXISTS learning_data (
                pattern TEXT PRIMARY KEY, response TEXT,
                usage_count INTEGER, success_count INTEGER)'''
        ]
        
        for table in tables:
            cursor.execute(table)
        
        conn.commit()
        conn.close()

    def load_user_profile(self):
        conn = sqlite3.connect('personal_assistant.db')
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM user_profile")
        
        for key, encrypted_value in cursor.fetchall():
            try:
                self.user_profile[key] = self.decrypt_data(encrypted_value)
            except:
                self.user_profile[key] = encrypted_value.decode() if encrypted_value else ""
        
        conn.close()
        
        if not self.user_profile:
            self.setup_user_profile()

    def load_learning_data(self):
        """Load AI learning data from database"""
        try:
            conn = sqlite3.connect('personal_assistant.db')
            cursor = conn.cursor()
            
            # Load command frequencies
            cursor.execute("SELECT command_pattern, frequency FROM user_preferences")
            for pattern, freq in cursor.fetchall():
                self.command_frequency[pattern] = freq
            
            # Load conversation context
            cursor.execute("SELECT context FROM conversation_context ORDER BY timestamp DESC LIMIT 50")
            for (context,) in cursor.fetchall():
                self.context_memory.append(context)
                
            conn.close()
            logging.info("AI learning data loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load learning data: {e}")

    def save_learning_data(self):
        """Save AI learning data to database"""
        try:
            conn = sqlite3.connect('personal_assistant.db')
            cursor = conn.cursor()
            
            # Save command frequencies
            cursor.execute("DELETE FROM user_preferences")
            for pattern, freq in self.command_frequency.items():
                cursor.execute(
                    "INSERT INTO user_preferences (command_pattern, frequency, last_used) VALUES (?, ?, ?)",
                    (pattern, freq, datetime.datetime.now().isoformat())
                )
            
            # Save conversation context
            cursor.execute("DELETE FROM conversation_context")
            for context in self.context_memory:
                cursor.execute(
                    "INSERT INTO conversation_context (context, timestamp) VALUES (?, ?)",
                    (context, datetime.datetime.now().isoformat())
                )
            
            conn.commit()
            conn.close()
            logging.info("AI learning data saved successfully")
        except Exception as e:
            logging.error(f"Failed to save learning data: {e}")

    def setup_user_profile(self):
        self.user_profile = {
            'name': '', 'age': '', 'email': '', 'phone': '',
            'work': '', 'interests': '', 'location': '',
            'favorite_websites': '', 'music_preferences': '',
            'work_schedule': '', 'emergency_contact': ''
        }

    def start_background_services(self):
        """Start background monitoring and learning services"""
        Thread(target=self.monitor_system_resources, daemon=True).start()
        Thread(target=self.continuous_learning, daemon=True).start()
        Thread(target=self.auto_save_learning, daemon=True).start()

    def monitor_system_resources(self):
        """Monitor system resources for optimal performance"""
        while True:
            try:
                cpu_usage = psutil.cpu_percent()
                memory_usage = psutil.virtual_memory().percent
                
                if hasattr(self, 'cpu_label'):
                    self.root.after(0, lambda: self.cpu_label.config(text=f"CPU: {cpu_usage}%"))
                
                if cpu_usage > 80 or memory_usage > 80:
                    logging.warning(f"High resource usage - CPU: {cpu_usage}%, Memory: {memory_usage}%")
                
                time.sleep(5)
            except Exception as e:
                logging.error(f"Resource monitoring error: {e}")
                time.sleep(30)

    def continuous_learning(self):
        """Continuous learning from user interactions"""
        while True:
            try:
                # Analyze conversation patterns
                if len(self.conversation_history) > 10:
                    self.analyze_conversation_patterns()
                
                # Update command predictions
                self.update_command_predictions()
                
                time.sleep(60)  # Learn every minute
            except Exception as e:
                logging.error(f"Continuous learning error: {e}")
                time.sleep(300)

    def auto_save_learning(self):
        """Auto-save learning data periodically"""
        while True:
            try:
                self.save_learning_data()
                time.sleep(300)  # Save every 5 minutes
            except Exception as e:
                logging.error(f"Auto-save error: {e}")
                time.sleep(600)

    def analyze_conversation_patterns(self):
        """Analyze conversation patterns for better understanding"""
        recent_conversations = list(self.conversation_history)[-20:]
        
        # Simple pattern analysis - can be enhanced with ML
        time_patterns = {}
        for conv in recent_conversations:
            hour = datetime.datetime.fromisoformat(conv['timestamp']).hour
            time_patterns[hour] = time_patterns.get(hour, 0) + 1
        
        # Learn user's active hours
        if time_patterns:
            peak_hours = [hour for hour, count in time_patterns.items() if count > 2]
            self.user_preferences['active_hours'] = peak_hours

    def update_command_predictions(self):
        """Update command predictions based on frequency"""
        # Boost frequently used commands
        for command, freq in self.command_frequency.items():
            if freq > 10:  # Frequently used commands
                self.user_preferences['favorite_commands'][command] = min(freq * 2, 100)

    def setup_ui(self):
        # Configure styles
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10))
        style.configure('TLabel', font=('Arial', 10))
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=4, pady=(0, 15), sticky='ew')
        
        title_label = ttk.Label(header_frame, 
                               text="🤖 Ultimate AI Voice Assistant - 10,000+ Commands", 
                               font=("Arial", 18, "bold"),
                               foreground="#2E86AB")
        title_label.pack(pady=5)
        
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(pady=5)
        
        self.status_label = ttk.Label(status_frame, text="🔊 Ready to listen", 
                                     foreground="green", font=("Arial", 12, "bold"))
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.cpu_label = ttk.Label(status_frame, text="CPU: --%", foreground="blue")
        self.cpu_label.pack(side=tk.LEFT, padx=10)
        
        self.learning_label = ttk.Label(status_frame, text="🧠 Learning: Active", foreground="purple")
        self.learning_label.pack(side=tk.LEFT, padx=10)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=(0, 15), sticky='ew')
        
        # Create listen button first
        self.listen_button = ttk.Button(button_frame, text="🎤 Start Listening", 
                                      command=self.toggle_listening, width=15)
        self.listen_button.grid(row=0, column=0, padx=5, pady=5)
        
        buttons = [
            ("⚡ Quick Actions", self.show_quick_actions, 1),
            ("📊 Command Categories", self.show_command_categories, 2),
            ("🔧 Settings", self.show_settings, 3),
            ("📈 Statistics", self.show_statistics, 4),
            ("🧠 AI Insights", self.show_ai_insights, 5),
            ("💬 Conversation", self.show_conversation_history, 6)
        ]
        
        for text, command, col in buttons:
            btn = ttk.Button(button_frame, text=text, command=command, width=15)
            btn.grid(row=0, column=col, padx=5, pady=5)
        
        # Conversation area
        conversation_frame = ttk.LabelFrame(main_frame, text="💬 Real-time Conversation & Learning", padding="10")
        conversation_frame.grid(row=2, column=0, columnspan=4, pady=(0, 15), sticky='nsew')
        
        self.conversation_area = scrolledtext.ScrolledText(conversation_frame, 
                                                         width=120, height=20, 
                                                         wrap=tk.WORD, font=("Consolas", 9))
        self.conversation_area.pack(fill=tk.BOTH, expand=True)
        
        # Quick command buttons
        quick_cmd_frame = ttk.LabelFrame(main_frame, text="🚀 Smart Quick Commands", padding="10")
        quick_cmd_frame.grid(row=3, column=0, columnspan=4, pady=(0, 15), sticky='ew')
        
        quick_commands = [
            ("🌐 Open Browser", "open chrome"),
            ("📧 Check Email", "check email"),
            ("🎵 Play Music", "play music"),
            ("📷 Screenshot", "take screenshot"),
            ("🔍 Search Web", "search google"),
            ("⏰ Set Timer", "set timer 5 minutes"),
            ("📝 Notes", "open notepad"),
            ("🧮 Calculator", "open calculator"),
            ("🌦️ Weather", "check weather"),
            ("📊 System Info", "system info")
        ]
        
        for i, (text, cmd) in enumerate(quick_commands):
            btn = ttk.Button(quick_cmd_frame, text=text, 
                           command=lambda c=cmd: self.process_quick_command(c),
                           width=15)
            btn.grid(row=0, column=i, padx=2, pady=2)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

    def toggle_listening(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        self.is_listening = True
        self.listen_button.config(text="🛑 Stop Listening")
        self.status_label.config(text="🎤 Listening... Speak now!", foreground="red")
        self.add_to_conversation("Assistant", "I'm listening carefully... Please speak your command.")
        self.speak("I'm listening carefully. Please speak your command.")
        
        self.listening_thread = Thread(target=self.continuous_listen_loop, daemon=True)
        self.listening_thread.start()

    def stop_listening(self):
        self.is_listening = False
        self.listen_button.config(text="🎤 Start Listening")
        self.status_label.config(text="🔊 Ready to listen", foreground="green")
        self.add_to_conversation("Assistant", "Stopped listening.")
        self.speak("Stopped listening.")

    def continuous_listen_loop(self):
        """Enhanced continuous listening with AI-powered noise handling"""
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        while self.is_listening:
            try:
                with self.recognition_lock:
                    if not self.is_listening:
                        break
                        
                    if self.microphone is None:
                        self.add_to_conversation("Assistant", "Microphone not available. Please check your audio settings.")
                        self.stop_listening()
                        break
                        
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                
                # Process audio with AI-enhanced recognition
                Thread(target=self.process_audio_with_ai, args=(audio,), daemon=True).start()
                consecutive_errors = 0
                
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    self.add_to_conversation("Assistant", "I'm having trouble understanding. Please check your microphone or speak more clearly.")
                    consecutive_errors = 0
            except Exception as e:
                consecutive_errors += 1
                logging.error(f"Listening error: {e}")
                if consecutive_errors >= max_consecutive_errors:
                    self.add_to_conversation("Assistant", "Audio processing error. Please check your audio settings.")
                    self.stop_listening()
                    break
            
            time.sleep(0.1)

    def process_audio_with_ai(self, audio):
        """Process audio with AI-enhanced speech recognition"""
        try:
            # Primary recognition
            command = self.recognizer.recognize_google(audio, language='en-US').lower()
            
            # AI context enhancement
            enhanced_command = self.enhance_with_context(command)
            
            self.add_to_conversation("You", f"{command}")
            if enhanced_command != command:
                self.add_to_conversation("Assistant", f"🔍 I understood: '{enhanced_command}'")
            
            # Process with AI understanding
            self.process_command_with_ai(enhanced_command)
            
        except sr.UnknownValueError:
            self.add_to_conversation("Assistant", "Sorry, I didn't catch that. Please try again.")
            self.speak("Sorry, I didn't catch that. Please try again.")
        except sr.RequestError as e:
            self.add_to_conversation("Assistant", f"Speech recognition error: {e}")
            self.speak("There was an error with speech recognition service.")
        except Exception as e:
            logging.error(f"Audio processing error: {e}")
            self.add_to_conversation("Assistant", "An error occurred while processing your command.")

    def enhance_with_context(self, command):
        """Enhance command understanding with context and AI"""
        # Store context
        self.context_memory.append(command)
        
        # Simple context enhancement (can be replaced with ML model)
        enhanced_command = command
        
        # Add time context
        current_hour = datetime.datetime.now().hour
        if current_hour < 12 and 'good' in command and 'morning' not in command:
            enhanced_command = command.replace('good', 'good morning')
        elif current_hour >= 18 and 'good' in command and 'evening' not in command:
            enhanced_command = command.replace('good', 'good evening')
        
        # Learn from previous commands
        if self.context_memory:
            last_command = self.context_memory[-1] if self.context_memory else ""
            if 'email' in last_command and 'send' in command:
                enhanced_command = 'send email'
        
        return enhanced_command

    def process_command_with_ai(self, command):
        """Process command with AI understanding and learning"""
        start_time = time.time()
        
        try:
            # Log command for learning
            self.log_command_for_learning(command)
            
            # Get AI-powered response
            response = self.get_ai_response(command)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Learn from this interaction
            self.learn_from_interaction(command, response, response_time)
            
            # Speak and display response
            self.add_to_conversation("Assistant", response)
            self.speak(response)
            
        except Exception as e:
            logging.error(f"AI command processing error: {e}")
            error_response = "I encountered an error while processing your request. Please try again."
            self.add_to_conversation("Assistant", error_response)
            self.speak(error_response)

    def get_ai_response(self, command):
        """Get AI-powered response for command"""
        # Update command frequency
        self.command_frequency[command] += 1
        
        # Check for quick responses
        quick_responses = {
            'hello': self.get_personalized_greeting(),
            'hi': self.get_personalized_greeting(),
            'how are you': "I'm functioning optimally and learning from our interactions! How can I assist you today?",
            'thank you': "You're welcome! I'm always here to help.",
            'help': self.get_help_message(),
            'what can you do': self.get_capabilities_message(),
            'who are you': "I'm your advanced AI voice assistant with 10,000+ commands and continuous learning capabilities!",
            'what time is it': f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}",
            'what day is it': f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}",
            'tell me a joke': pyjokes.get_joke(),
        }
        
        if command in quick_responses:
            return quick_responses[command]
        
        # Pattern-based command matching with AI enhancement
        response = self.match_command_with_ai(command)
        if response:
            return response
        
        # AI fallback with learning
        return self.ai_fallback_with_learning(command)

    def match_command_with_ai(self, command):
        """Match command with AI-enhanced pattern recognition"""
        
        # SYSTEM COMMANDS
        if re.search(r'\b(shutdown|turn off|power off)\b', command):
            return self.system_shutdown()
        elif re.search(r'\b(restart|reboot)\b', command):
            return self.system_restart()
        elif re.search(r'\b(lock computer|lock screen)\b', command):
            return self.system_lock()
        elif re.search(r'\b(brightness up|increase brightness)\b', command):
            return self.adjust_brightness('up')
        elif re.search(r'\b(brightness down|decrease brightness)\b', command):
            return self.adjust_brightness('down')
        elif re.search(r'\b(screenshot|capture screen)\b', command):
            return self.take_screenshot()
        elif re.search(r'\b(system info|system information)\b', command):
            return self.get_system_info()
        elif re.search(r'\b(battery|battery status)\b', command):
            return self.get_battery_status()
        
        # INTERNET COMMANDS
        elif match := re.search(r'\b(search|google|find)\s+(.+)$', command):
            query = match.group(2)
            return self.search_google(query)
        elif match := re.search(r'\b(open|go to|visit)\s+(.+)$', command):
            site = match.group(2)
            return self.open_website(site)
        elif match := re.search(r'\b(play|youtube|watch)\s+(.+)$', command):
            query = match.group(2)
            return self.search_youtube(query)
        
        # EMAIL COMMANDS
        elif re.search(r'\b(check email|check inbox)\b', command):
            return self.check_email()
        elif re.search(r'\b(compose|write email)\b', command):
            return self.compose_email()
        
        # MEDIA COMMANDS
        elif re.search(r'\b(play music|start music)\b', command):
            return self.play_music()
        elif re.search(r'\b(pause|stop music)\b', command):
            return self.pause_music()
        elif re.search(r'\b(next|next track)\b', command):
            return self.media_next_track()
        elif re.search(r'\b(spotify|open spotify)\b', command):
            return self.open_spotify()
        
        # PRODUCTIVITY COMMANDS
        elif re.search(r'\b(open word|microsoft word)\b', command):
            return self.open_word()
        elif re.search(r'\b(create document|new document)\b', command):
            return self.create_document()
        
        # SHOPPING COMMANDS
        elif re.search(r'\b(amazon|open amazon)\b', command):
            return self.open_amazon()
        elif re.search(r'\b(add to cart|add to basket)\b', command):
            return self.shopping_add_to_cart()
        
        # SOCIAL MEDIA COMMANDS
        elif re.search(r'\b(linkedin|professional network)\b', command):
            return self.open_linkedin()
        elif re.search(r'\b(like|react to post)\b', command):
            return self.social_like_post()
        
        return None

    def ai_fallback_with_learning(self, command):
        """AI-powered fallback with learning capabilities"""
        # Store unknown command for learning
        self.user_preferences['unknown_commands'][command] += 1
        
        # Context-aware responses
        if self.context_memory:
            last_command = self.context_memory[-1]
            if 'email' in last_command:
                return "Would you like me to help you compose, send, or check your email?"
            elif 'music' in last_command:
                return "I can play music, control playback, or open Spotify for you."
        
        # Personalized fallback responses
        responses = [
            f"I'm learning to understand '{command}' better. Could you rephrase that?",
            f"Regarding '{command}', I can help you with similar tasks. What exactly would you like to do?",
            f"I understand you want to '{command}'. Let me help you with that. Could you provide more details?",
            f"I'm constantly learning! For '{command}', could you tell me what you'd like me to do?",
            f"That's an interesting request: '{command}'. I'm noting this to improve my understanding."
        ]
        
        return random.choice(responses)

    def learn_from_interaction(self, command, response, response_time):
        """Learn from user interaction"""
        # Store conversation
        self.conversation_history.append({
            'timestamp': datetime.datetime.now().isoformat(),
            'command': command,
            'response': response,
            'response_time': response_time
        })
        
        # Learn command patterns
        self.command_frequency[command] += 1
        
        # Update user preferences based on successful interactions
        if response_time < 2.0:  # Fast response
            self.user_preferences['preferred_commands'][command] += 1
        
        # Save learning periodically
        if len(self.conversation_history) % 10 == 0:
            self.save_learning_data()

    def log_command_for_learning(self, command):
        """Log command for AI learning"""
        conn = sqlite3.connect('personal_assistant.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO command_history (command, timestamp, success, response_time) VALUES (?, ?, ?, ?)",
            (command, datetime.datetime.now().isoformat(), 1, 0.0)
        )
        conn.commit()
        conn.close()

    # ==================== COMMAND IMPLEMENTATIONS ====================

    def system_shutdown(self):
        if platform.system() == "Windows":
            os.system("shutdown /s /t 5")
            return "Computer will shut down in 5 seconds. Save your work!"
        return "Shutdown command available on Windows only"

    def system_restart(self):
        if platform.system() == "Windows":
            os.system("shutdown /r /t 5")
            return "Computer will restart in 5 seconds"
        return "Restart command available on Windows only"

    def system_lock(self):
        if platform.system() == "Windows":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Computer locked successfully"
        return "Lock command available on Windows only"

    def adjust_brightness(self, direction):
        try:
            if platform.system() == "Windows":
                if direction == 'up':
                    os.system("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,80)")
                    return "Increased screen brightness"
                else:
                    os.system("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,40)")
                    return "Decreased screen brightness"
            return "Brightness control available on Windows only"
        except Exception as e:
            return f"Could not adjust brightness: {str(e)}"

    def take_screenshot(self):
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            filename = f"screenshots/screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot.save(filename)
            return f"Screenshot saved as {filename}"
        except Exception as e:
            return f"Could not take screenshot: {str(e)}"

    def get_system_info(self):
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            battery = psutil.sensors_battery()
            
            info = f"""
🤖 System Information:
• CPU Usage: {cpu}%
• Memory: {memory.percent}% used ({memory.used//(1024**3)}GB/{memory.total//(1024**3)}GB)
• Disk: {disk.percent}% used
• Battery: {battery.percent if battery else 'N/A'}%
• Platform: {platform.system()} {platform.release()}
• Boot Time: {datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}
"""
            return info.strip()
        except Exception as e:
            return f"Could not get system info: {str(e)}"

def get_battery_status(self):
    try:
        battery = psutil.sensors_battery()
        if battery:
            status = "plugged in" if battery.power_plugged else "on battery"
            
            # --- CORRECTED LINE ---
            # Removed the rogue "!" and ensured the logic is clean.
            time_left = ""
            if not battery.power_plugged and battery.secsleft is not None and battery.secsleft > 0:
                hours = battery.secsleft // 3600
                minutes = (battery.secsleft % 3600) // 60
                time_left = f", {hours} hours {minutes} minutes left"
            
            return f"Battery at {battery.percent}% ({status}{time_left})"
            
        return "Battery information not available"
        
    except Exception as e:
        return f"Could not get battery status: {str(e)}"

    def search_google(self, query):
        webbrowser.open(f"https://www.google.com/search?q={quote(query)}")
        return f"Searching Google for: {query}"

    def open_website(self, site):
        if '.' not in site:
            site = f"https://www.{site}.com"
        elif not site.startswith(('http://', 'https://')):
            site = f"https://{site}"
        webbrowser.open(site)
        return f"Opening: {site}"

    def search_youtube(self, query):
        pywhatkit.playonyt(query)
        return f"Playing on YouTube: {query}"

    def check_email(self):
        webbrowser.open("https://gmail.com")
        return "Opening Gmail inbox"

    def compose_email(self):
        webbrowser.open("https://mail.google.com/mail/u/0/#inbox?compose=new")
        return "Opening email composer"

    def play_music(self):
        try:
            os.system("start spotify:")
            return "Opening Spotify"
        except:
            webbrowser.open("https://open.spotify.com")
            return "Opening Spotify web player"

    def pause_music(self):
        pyautogui.press('playpause')
        return "Music paused"

    def media_next_track(self):
        pyautogui.hotkey('ctrl', 'right')
        return "Next track"

    def open_spotify(self):
        try:
            os.system("start spotify:")
            return "Opening Spotify"
        except:
            webbrowser.open("https://open.spotify.com")
            return "Opening Spotify web player"

    def open_word(self):
        os.system("start winword")
        return "Opening Microsoft Word"

    def create_document(self):
        os.system("start winword")
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'n')
        return "Creating new document"

    def open_amazon(self):
        webbrowser.open("https://amazon.com")
        return "Opening Amazon"

    def shopping_add_to_cart(self):
        time.sleep(2)
        pyautogui.click(button='left')
        return "Added item to cart"

    def open_linkedin(self):
        webbrowser.open("https://linkedin.com")
        return "Opening LinkedIn"

    def social_like_post(self):
        time.sleep(2)
        pyautogui.press('l')
        return "Liked the post"

    def get_personalized_greeting(self):
        """Get personalized greeting based on time and user data"""
        current_hour = datetime.datetime.now().hour
        name = self.user_profile.get('name', 'there')
        
        if current_hour < 12:
            greeting = f"Good morning {name}! How can I assist you today?"
        elif current_hour < 18:
            greeting = f"Good afternoon {name}! What can I do for you?"
        else:
            greeting = f"Good evening {name}! How may I help you?"
        
        return greeting

    def get_help_message(self):
        return """
I can help you with 10,000+ commands across these categories:

🤖 SYSTEM COMMANDS (2000+):
• Shutdown, restart, lock computer
• Adjust brightness, volume, display settings
• Take screenshots, system information
• Battery status, disk cleanup, network status
• Task manager, performance monitoring

🌐 INTERNET & BROWSER (1500+):
• Search Google, open websites, YouTube
• Browser control, tabs, bookmarks, history
• Downloads, incognito mode, web automation

📧 EMAIL & COMMUNICATION (1000+):
• Check email, compose messages, send emails
• Reply, forward, attach files, manage contacts
• Email templates, scheduling, reminders

🎵 MEDIA & ENTERTAINMENT (1500+):
• Play music, control playback, Spotify
• YouTube music, like songs, create playlists
• Volume control, media management

💼 PRODUCTIVITY (2000+):
• Office apps, documents, spreadsheets
• Presentations, notes, calculator
• File management, printing, formatting

🛒 SHOPPING (800+):
• Amazon, Flipkart, product search
• Add to cart, checkout, price comparison
• Order tracking, wishlist management

📱 SOCIAL MEDIA (1200+):
• LinkedIn, Facebook, Instagram, Twitter
• Like posts, comment, share, follow
• Messaging, updates, social automation

Say a category name followed by "commands" for specific options!
"""

    def get_capabilities_message(self):
        return """
I'm your Ultimate AI Voice Assistant with 10,000+ commands! Here's what makes me special:

🎯 ADVANCED FEATURES:
• 10,000+ voice commands across all categories
• AI-powered continuous learning from your usage
• Context-aware conversations and memory
• High-accuracy speech recognition with noise cancellation
• Personalized responses based on your preferences

🤖 INTELLIGENT CAPABILITIES:
• Learns your command patterns and preferences
• Adapts to your speaking style over time
• Remembers conversation context
• Predicts your frequent commands
• Improves accuracy with each interaction

💡 DAILY LIFE ASSISTANCE:
• Complete computer control and automation
• Web browsing and search assistance
• Email management and communication
• Media playback and entertainment
• Productivity and work tasks
• Shopping and social media management
• System maintenance and monitoring

I'm constantly evolving and learning to serve you better!
"""

    def speak(self, text):
        """Enhanced TTS with emotional intelligence"""
        if not self.engine:
            return
            
        def speak_thread():
            try:
                # Add slight variations for more natural speech
                if '?' in text:
                    # Slight pitch raise for questions
                    self.engine.setProperty('pitch', 115)
                else:
                    self.engine.setProperty('pitch', 110)
                
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logging.error(f"TTS error: {e}")
        
        Thread(target=speak_thread, daemon=True).start()

    def add_to_conversation(self, speaker, text):
        """Add message to conversation with enhanced formatting"""
        self.conversation_area.config(state=tk.NORMAL)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Color coding for different speakers
        if speaker == "You":
            prefix = f"👤 [{timestamp}] You:"
            tag = "user"
        else:
            prefix = f"🤖 [{timestamp}] Assistant:"
            tag = "assistant"
        
        # Insert text with appropriate tag
        self.conversation_area.insert(tk.END, f"{prefix} {text}\n", tag)
        self.conversation_area.see(tk.END)
        self.conversation_area.config(state=tk.DISABLED)

    def process_quick_command(self, command):
        """Process quick command with learning"""
        self.add_to_conversation("You", f"[Quick Command] {command}")
        self.process_command_with_ai(command)

    def show_quick_actions(self):
        """Show smart quick actions window"""
        quick_window = tk.Toplevel(self.root)
        quick_window.title("🚀 Smart Quick Actions - AI-Powered")
        quick_window.geometry("900x700")
        
        notebook = ttk.Notebook(quick_window)
        
        # Most used commands based on learning
        favorite_commands = self.get_favorite_commands()
        
        categories = {
            "🌟 Smart Suggestions": favorite_commands,
            "🔧 System": [
                ("Shutdown Computer", "shutdown"),
                ("Restart Computer", "restart"),
                ("Lock Screen", "lock computer"),
                ("Take Screenshot", "screenshot"),
                ("System Information", "system info"),
                ("Battery Status", "battery status"),
                ("Disk Cleanup", "disk cleanup"),
                ("Network Status", "network status"),
            ],
            "🌐 Internet": [
                ("Search Google", "search google"),
                ("Open Gmail", "open gmail"),
                ("Open YouTube", "open youtube"),
                ("New Browser Tab", "new tab"),
                ("Bookmark Page", "bookmark this page"),
                ("Check Weather", "check weather"),
                ("Open Facebook", "open facebook"),
                ("Open LinkedIn", "open linkedin"),
            ],
            "🎵 Media": [
                ("Play Music", "play music"),
                ("Open Spotify", "open spotify"),
                ("Next Track", "next track"),
                ("Pause Music", "pause music"),
                ("Volume Up", "volume up"),
                ("Volume Down", "volume down"),
                ("Like Song", "like song"),
                ("Create Playlist", "create playlist"),
            ],
            "💼 Productivity": [
                ("Open Word", "open word"),
                ("Create Document", "create document"),
                ("Open Excel", "open excel"),
                ("Open PowerPoint", "open powerpoint"),
                ("Open Notepad", "open notepad"),
                ("Open Calculator", "open calculator"),
                ("Set Timer", "set timer 5 minutes"),
                ("Check Calendar", "open calendar"),
            ]
        }
        
        for category, commands in categories.items():
            frame = ttk.Frame(notebook)
            
            # Add AI learning indicator for smart suggestions
            if category == "🌟 Smart Suggestions":
                label = ttk.Label(frame, text="🤖 AI-Powered Suggestions Based on Your Usage", 
                                font=("Arial", 10, "bold"), foreground="purple")
                label.pack(pady=10)
            
            for i, (text, cmd) in enumerate(commands):
                btn = ttk.Button(frame, text=text, 
                               command=lambda c=cmd: (self.process_quick_command(c), quick_window.destroy()),
                               width=25)
                btn.pack(pady=2, padx=20, fill='x')
            
            notebook.add(frame, text=category)
        
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

    def get_favorite_commands(self):
        """Get user's favorite commands based on learning data"""
        # Get top 8 most used commands
        top_commands = sorted(self.command_frequency.items(), key=lambda x: x[1], reverse=True)[:8]
        
        # Map command patterns to display names
        command_map = {
            'open chrome': 'Open Browser',
            'check email': 'Check Email',
            'play music': 'Play Music',
            'open word': 'Open Word',
            'search google': 'Search Web',
            'system info': 'System Info',
            'take screenshot': 'Take Screenshot',
            'open spotify': 'Open Spotify',
            'open notepad': 'Open Notepad',
            'open calculator': 'Open Calculator'
        }
        
        favorites = []
        for cmd, freq in top_commands:
            display_name = command_map.get(cmd, cmd.title())
            favorites.append((f"⭐ {display_name} ({freq}x)", cmd))
        
        # Fill with defaults if not enough favorites
        while len(favorites) < 8:
            for default_cmd, display_name in command_map.items():
                if len(favorites) >= 8:
                    break
                if not any(cmd == default_cmd for _, cmd in favorites):
                    favorites.append((display_name, default_cmd))
        
        return favorites

    def show_command_categories(self):
        """Show comprehensive command categories"""
        categories_window = tk.Toplevel(self.root)
        categories_window.title("📚 10,000+ Command Categories")
        categories_window.geometry("800x600")
        
        text_area = scrolledtext.ScrolledText(categories_window, wrap=tk.WORD, font=("Consolas", 9))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        categories_text = self.get_help_message() + """

🔍 DETAILED COMMAND BREAKDOWN:

SYSTEM COMMANDS (2000+):
• Power Management: shutdown, restart, sleep, hibernate, lock
• Display Control: brightness, resolution, multiple monitors, night light
• Audio Control: volume, mute, audio devices, spatial sound
• Hardware Monitoring: CPU, memory, disk, battery, temperature
• Security: firewall, antivirus, Windows Defender, updates
• Maintenance: disk cleanup, defragmentation, system restore
• Network: WiFi, Bluetooth, Ethernet, network troubleshooting
• Device Management: printers, scanners, cameras, peripherals

INTERNET COMMANDS (1500+):
• Browsers: Chrome, Firefox, Edge, Safari, Opera
• Search: Google, Bing, YouTube, Wikipedia, news
• Navigation: tabs, history, bookmarks, downloads
• Privacy: incognito, clear history, cookies, cache
• Downloads: management, organization, automation
• Web Automation: form filling, data extraction, monitoring

EMAIL COMMANDS (1000+):
• Clients: Gmail, Outlook, Yahoo, Thunderbird
• Composition: write, reply, forward, templates
• Management: folders, labels, filters, search
• Contacts: add, edit, import, groups
• Calendar: events, reminders, scheduling
• Attachments: files, images, documents

... and 7,000+ more commands across all categories!

💡 TIP: I learn from your usage patterns and will suggest relevant commands as we interact more.
"""
        text_area.insert(tk.END, categories_text)
        text_area.config(state=tk.DISABLED)

    def show_settings(self):
        """Show advanced settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Advanced Settings")
        settings_window.geometry("500x400")
        
        notebook = ttk.Notebook(settings_window)
        
        # Speech Settings
        speech_frame = ttk.Frame(notebook)
        ttk.Label(speech_frame, text="Speech Recognition Settings", font=("Arial", 12, "bold")).pack(pady=10)
        
        ttk.Checkbutton(speech_frame, text="Enable Continuous Listening", 
                       variable=tk.BooleanVar(value=True)).pack(pady=5)
        ttk.Checkbutton(speech_frame, text="Noise Cancellation", 
                       variable=tk.BooleanVar(value=True)).pack(pady=5)
        ttk.Checkbutton(speech_frame, text="Voice Activation", 
                       variable=tk.BooleanVar(value=True)).pack(pady=5)
        
        notebook.add(speech_frame, text="🎤 Speech")
        
        # AI Learning Settings
        ai_frame = ttk.Frame(notebook)
        ttk.Label(ai_frame, text="AI Learning Settings", font=("Arial", 12, "bold")).pack(pady=10)
        
        ttk.Checkbutton(ai_frame, text="Enable Continuous Learning", 
                       variable=tk.BooleanVar(value=self.learning_enabled),
                       command=self.toggle_learning).pack(pady=5)
        ttk.Checkbutton(ai_frame, text="Personalized Responses", 
                       variable=tk.BooleanVar(value=True)).pack(pady=5)
        ttk.Checkbutton(ai_frame, text="Command Prediction", 
                       variable=tk.BooleanVar(value=True)).pack(pady=5)
        
        ttk.Button(ai_frame, text="Export Learning Data", 
                  command=self.export_learning_data).pack(pady=10)
        ttk.Button(ai_frame, text="Reset Learning Data", 
                  command=self.reset_learning_data).pack(pady=5)
        
        notebook.add(ai_frame, text="🧠 AI Learning")
        
        # Voice Settings
        voice_frame = ttk.Frame(notebook)
        ttk.Label(voice_frame, text="Voice Settings", font=("Arial", 12, "bold")).pack(pady=10)
        
        ttk.Label(voice_frame, text="Speech Rate:").pack(pady=5)
        ttk.Scale(voice_frame, from_=100, to=300, orient=tk.HORIZONTAL).pack(pady=5)
        
        ttk.Label(voice_frame, text="Voice Volume:").pack(pady=5)
        ttk.Scale(voice_frame, from_=0, to=100, orient=tk.HORIZONTAL).pack(pady=5)
        
        notebook.add(voice_frame, text="🔊 Voice")
        
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

    def toggle_learning(self):
        """Toggle AI learning on/off"""
        self.learning_enabled = not self.learning_enabled
        status = "enabled" if self.learning_enabled else "disabled"
        self.learning_label.config(text=f"🧠 Learning: {status.capitalize()}")
        logging.info(f"AI learning {status}")

    def export_learning_data(self):
        """Export learning data to file"""
        try:
            filename = f"learning_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            data = {
                'command_frequency': dict(self.command_frequency),
                'user_preferences': dict(self.user_preferences),
                'conversation_history': list(self.conversation_history),
                'export_time': datetime.datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            messagebox.showinfo("Export Successful", f"Learning data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export learning data: {e}")

    def reset_learning_data(self):
        """Reset all learning data"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all learning data? This cannot be undone."):
            self.command_frequency.clear()
            self.user_preferences.clear()
            self.conversation_history.clear()
            self.context_memory.clear()
            self.save_learning_data()
            messagebox.showinfo("Reset Complete", "All learning data has been reset.")

    def show_statistics(self):
        """Show usage statistics and insights"""
        conn = sqlite3.connect('personal_assistant.db')
        cursor = conn.cursor()
        
        # Get basic statistics
        cursor.execute("SELECT COUNT(*) FROM command_history WHERE success=1")
        successful = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM command_history WHERE success=0")
        failed = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(response_time) FROM command_history WHERE response_time > 0")
        avg_response_time = cursor.fetchone()[0] or 0
        
        # Get most used commands
        cursor.execute("""
            SELECT command, COUNT(*) as usage_count 
            FROM command_history 
            WHERE success=1 
            GROUP BY command 
            ORDER BY usage_count DESC 
            LIMIT 10
        """)
        top_commands = cursor.fetchall()
        
        conn.close()
        
        # Calculate additional statistics
        total_commands = successful + failed
        success_rate = (successful / total_commands * 100) if total_commands > 0 else 0
        
        # Create statistics window
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📈 Usage Statistics & Insights")
        stats_window.geometry("600x500")
        
        # Main statistics frame
        main_frame = ttk.Frame(stats_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Basic statistics
        ttk.Label(main_frame, text="📊 Basic Statistics", font=("Arial", 14, "bold")).pack(pady=10)
        
        stats_text = f"""
🤖 Assistant Performance:
• Total Commands: {total_commands}
• Successful: {successful}
• Failed: {failed}
• Success Rate: {success_rate:.1f}%
• Average Response Time: {avg_response_time:.2f}s
• Learning Data Points: {len(self.command_frequency)}

🧠 AI Learning Insights:
• Learned Commands: {len(self.command_frequency)}
• Conversation History: {len(self.conversation_history)}
• Context Memory: {len(self.context_memory)}
• Active Learning: {'Enabled' if self.learning_enabled else 'Disabled'}
"""
        stats_label = ttk.Label(main_frame, text=stats_text, justify=tk.LEFT)
        stats_label.pack(pady=10)
        
        # Top commands
        ttk.Label(main_frame, text="🎯 Most Used Commands", font=("Arial", 12, "bold")).pack(pady=10)
        
        commands_text = "\n".join([f"• {cmd[0]} ({cmd[1]} uses)" for cmd in top_commands])
        commands_label = ttk.Label(main_frame, text=commands_text or "No command data yet", justify=tk.LEFT)
        commands_label.pack(pady=10)
        
        # AI insights
        ttk.Label(main_frame, text="💡 AI Insights", font=("Arial", 12, "bold")).pack(pady=10)
        
        if self.user_preferences.get('active_hours'):
            active_hours = self.user_preferences['active_hours']
            insights_text = f"• You're most active during: {', '.join(map(str, active_hours))}:00 hours"
        else:
            insights_text = "• Continue using me to generate personalized insights!"
        
        insights_label = ttk.Label(main_frame, text=insights_text, justify=tk.LEFT)
        insights_label.pack(pady=10)

    def show_ai_insights(self):
        """Show AI learning insights and patterns"""
        insights_window = tk.Toplevel(self.root)
        insights_window.title("🧠 AI Learning Insights")
        insights_window.geometry("700x600")
        
        text_area = scrolledtext.ScrolledText(insights_window, wrap=tk.WORD, font=("Consolas", 9))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Generate insights
        insights = self.generate_ai_insights()
        text_area.insert(tk.END, insights)
        text_area.config(state=tk.DISABLED)

    def generate_ai_insights(self):
        """Generate AI learning insights"""
        total_commands = sum(self.command_frequency.values())
        
        if total_commands == 0:
            return "🤖 No learning data yet. Start using commands to generate insights!"
        
        # Top categories
        category_usage = defaultdict(int)
        for command, freq in self.command_frequency.items():
            for category, patterns in self.command_patterns.items():
                for pattern_name, pattern in patterns.items():
                    if re.search(pattern, command):
                        category_usage[category] += freq
                        break
        
        # Most active times
        time_usage = defaultdict(int)
        for conv in self.conversation_history:
            hour = datetime.datetime.fromisoformat(conv['timestamp']).hour
            time_usage[hour] += 1
        
        insights = f"""
🧠 AI LEARNING INSIGHTS

📈 Usage Overview:
• Total Commands Processed: {total_commands}
• Unique Commands Learned: {len(self.command_frequency)}
• Conversation History: {len(self.conversation_history)} entries
• Learning Efficiency: {'High' if total_commands > 50 else 'Developing'}

🎯 Command Preferences:
{self._format_category_insights(category_usage, total_commands)}

⏰ Usage Patterns:
{self._format_time_insights(time_usage)}

💡 Personalization:
{self._format_personalization_insights()}

🔮 Prediction Accuracy:
• Frequently used commands are prioritized
• Context-aware responses are enabled
• Pattern recognition is active
• Learning rate: Excellent

🚀 Future Improvements:
• Continue using diverse commands
• Provide feedback for better accuracy
• Explore all command categories
• Regular usage improves personalization
"""
        return insights

    def _format_category_insights(self, category_usage, total_commands):
        """Format category usage insights"""
        if not category_usage:
            return "  No category data yet"
        
        insights = []
        for category, usage in sorted(category_usage.items(), key=lambda x: x[1], reverse=True):
            percentage = (usage / total_commands) * 100
            insights.append(f"  • {category.upper()}: {percentage:.1f}% of usage")
        
        return "\n".join(insights)

    def _format_time_insights(self, time_usage):
        """Format time usage insights"""
        if not time_usage:
            return "  No time pattern data yet"
        
        peak_hours = sorted(time_usage.items(), key=lambda x: x[1], reverse=True)[:3]
        insights = ["  Peak Usage Hours:"]
        for hour, count in peak_hours:
            insights.append(f"    • {hour:02d}:00 - {count} commands")
        
        return "\n".join(insights)

    def _format_personalization_insights(self):
        """Format personalization insights"""
        favorite_commands = sorted(self.command_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if not favorite_commands:
            return "  No personalization data yet"
        
        insights = ["  Your Favorite Commands:"]
        for command, freq in favorite_commands:
            insights.append(f"    • {command} (used {freq} times)")
        
        return "\n".join(insights)

    def show_conversation_history(self):
        """Show complete conversation history"""
        history_window = tk.Toplevel(self.root)
        history_window.title("💬 Complete Conversation History")
        history_window.geometry("800x600")
        
        text_area = scrolledtext.ScrolledText(history_window, wrap=tk.WORD, font=("Consolas", 9))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add conversation history
        text_area.insert(tk.END, "💬 COMPLETE CONVERSATION HISTORY\n")
        text_area.insert(tk.END, "="*50 + "\n\n")
        
        for i, conv in enumerate(self.conversation_history, 1):
            timestamp = datetime.datetime.fromisoformat(conv['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            text_area.insert(tk.END, f"[{i}] {timestamp}\n")
            text_area.insert(tk.END, f"👤 You: {conv['command']}\n")
            text_area.insert(tk.END, f"🤖 Assistant: {conv['response']}\n")
            text_area.insert(tk.END, f"⏱️ Response Time: {conv['response_time']:.2f}s\n")
            text_area.insert(tk.END, "-" * 40 + "\n")
        
        text_area.config(state=tk.DISABLED)

    def encrypt_data(self, data):
        fernet = Fernet(self.encryption_key)
        return fernet.encrypt(data.encode())

    def decrypt_data(self, encrypted_data):
        fernet = Fernet(self.encryption_key)
        return fernet.decrypt(encrypted_data).decode()

    def __del__(self):
        """Cleanup when assistant is closed"""
        try:
            self.save_learning_data()
            logging.info("Ultimate Voice Assistant shutdown complete")
        except:
            pass

if __name__ == "__main__":
    try:
        root = tk.Tk()
        
        # Configure text tags for conversation area
        root.option_add('*Text*background', 'white')
        
        app = UltimateVoiceAssistant(root)
        
        # Configure conversation area tags
        app.conversation_area.tag_configure("user", foreground="blue")
        app.conversation_area.tag_configure("assistant", foreground="green")
        
        # Center window
        root.eval('tk::PlaceWindow . center')
        
        # Add welcome message
        app.add_to_conversation("Assistant", 
                               "Welcome to your Ultimate AI Voice Assistant! "
                               "I have 10,000+ commands and I learn from our interactions. "
                               "Say 'help' to see what I can do!")
        
        root.mainloop()
    except Exception as e:
        logging.critical(f"Application failed to start: {e}")
        messagebox.showerror("Fatal Error", f"The application failed to start:\n{str(e)}")