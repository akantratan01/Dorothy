import asyncio
import edge_tts
import playsound
import speech_recognition as sr
import webbrowser
import wikipedia
import pygetwindow as gw
import pyautogui

import os
import time
import random
import tkinter as tk
from threading import Thread
from tkinter import Scrollbar, Text, END
from PIL import Image, ImageTk, ImageSequence
import sys
import os
from responses4u import responses

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


listener = sr.Recognizer()



async def speak(text):
    print("AI:", text)
    filename = f"output_{int(time.time() * 800)}.mp3"
    communicate = edge_tts.Communicate(
        text,
        voice="ja-JP-NanamiNeural",  # Or try JennyNeural
        rate="-15%",                 # Slightly faster
        pitch="+40Hz"                # Higher pitch = more anime-like
    )
    await communicate.save(filename)
    playsound.playsound(filename)
    
    try:
        os.remove(filename)
    except PermissionError:
        print(f"Could not delete {filename} because it is still in use.")


def listen_command():
    with sr.Microphone() as source:
        print("Listening...")
        listener.adjust_for_ambient_noise(source)
        audio = listener.listen(source, phrase_time_limit=5)
    try:
        command = listener.recognize_google(audio).lower()
        print("You:", command)
        return command
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "network error"

async def open_any_website(command):
    known_sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "instagram": "https://www.instagram.com",
        "chatgpt": "https://chat.openai.com",
        "github": "https://github.com",
        "spotify": "https://open.spotify.com"
    }
    for name, url in known_sites.items():
        if name in command:
            await speak(f"Opening {name}")
            await asyncio.to_thread(webbrowser.open, url)
            return True
    if "open" in command:
        site = command.split("open")[-1].strip().replace(" ", "")
        url = f"https://www.{site}.com"
        await speak(f"Trying to open {site}")
        await asyncio.to_thread(webbrowser.open, url)
        return True
    return False

async def close_application(command):
    keyword = command.replace("close", "").replace("app", "").strip().lower()
    found = False

    for title in gw.getAllTitles():
        if keyword in title.lower():
            window = gw.getWindowsWithTitle(title)[0]
            try:
                window.close()
                await speak(f"Closed window with {keyword}")
                found = True
                break
            except Exception as e:
                print(e)
                continue

    if not found:
        await speak(f"No window found containing '{keyword}'")


async def search_anything(command):
    if "search" in command:
        command = command.lower()

        # Remove filler words
        query = command.replace("search", "").replace("for", "").strip()

        if "youtube" in command:
            query = query.replace("on youtube", "").strip()
            await speak(f"Searching YouTube for {query}")
            await asyncio.to_thread(webbrowser.open, f"https://www.youtube.com/results?search_query={query}")

        elif "chat gpt" in command:
            query = query.replace("on chat gpt", "").strip()
            await speak(f"Searching ChatGPT for {query}")
            await asyncio.to_thread(webbrowser.open, f"https://chat.openai.com/?q={query}")

        else:
            query = query.replace("on google", "").strip()
            await speak(f"Searching Google for {query}")
            await asyncio.to_thread(webbrowser.open, f"https://www.google.com/search?q={query}")


async def repeat_after_me(command):
        if "repeat after me" in command:
           to_repeat = command.split("repeat after me ",)[-1].strip()
        elif "say" in command:
           to_repeat = command.split("say",)[-1].strip()
        else:
            return False  # not a repeat command

        if to_repeat:
           await speak(to_repeat)
           return True

        return False

async def tell_about_topic(command):
    trigger_phrases = ["do you know about", "tell me about", "who is", "what do you know about"]
    for phrase in trigger_phrases:
        if phrase in command.lower():
            try:
                topic = command.lower()
                for p in trigger_phrases:
                    topic = topic.replace(p, "")
                topic = topic.strip()
                summary = wikipedia.summary(topic, sentences=2)
                await speak(summary)
            except wikipedia.exceptions.DisambiguationError:
                await speak(f"There are multiple entries for {topic}. Please be more specific.")
            except wikipedia.exceptions.PageError:
                await speak(f"I couldn't find any information about {topic}.")
            return True
    return False

async def explain_meaning(command):
    trigger_phrases = ["what do you mean by", "define", "explain","what is"]
    for phrase in trigger_phrases:
        if phrase in command.lower():
            try:
                topic = command.lower()
                for p in trigger_phrases:
                    topic = topic.replace(p, "")
                topic = topic.strip()
                summary = wikipedia.summary(topic, sentences=2)
                await speak(summary)
            except wikipedia.exceptions.DisambiguationError:
                await speak(f"There are multiple meanings of {topic}. Can you be more specific?")
            except wikipedia.exceptions.PageError:
                await speak(f"I couldn't find the meaning of {topic}.")
            return True
    return False


import re

async def set_timer(command):
    # Example command: "set a timer for 10 seconds" or "set timer for 2 minutes"
    pattern = r"timer for (\d+)\s*(seconds|second|minutes|minute)"
    match = re.search(pattern, command.lower())
    if match:
        value = int(match.group(1))
        unit = match.group(2)

        seconds = value if "second" in unit else value * 60
        await speak(f"Timer set for {value} {unit}")
        await asyncio.sleep(seconds)
        await speak(f"Time's up! Your {value} {unit} timer has finished.")
    else:
        await speak("Sorry, I couldn't understand the timer duration.")



import datetime

async def time_based_greeting():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        await speak("Good morning! ☀️ How can I help you today?")
    elif 12 <= hour < 17:
        await speak("Good afternoon senpai need help?")
    elif 17 <= hour < 22:
        await speak("Good evening! 🌆 Need any assistance?")
    else:
        await speak("Hello! It's quite late. Do you need help with something?")



async def tell_about_person(command):
    name = command.replace("tell me about", "").replace("who is", "").strip()
    try:
        summary = wikipedia.summary(name, sentences=2)
        await speak(summary)
    except wikipedia.exceptions.DisambiguationError:
        await speak(f"There are multiple people named {name}. Please be more specific.")
    except wikipedia.exceptions.PageError:
        await speak(f"I couldn't find any information about {name}.")

async def play_song_on_spotify(command):
    if "play" in command and "spotify" in command:
        song = command.replace("play", "").replace("on spotify", "").strip()
        await speak(f"Playing {song} on Spotify")
        await asyncio.to_thread(webbrowser.open, f"https://open.spotify.com/search/{song}")
        await asyncio.sleep(5)  # Give time for page to load
        pyautogui.press('tab', presses=5, interval=0.3)  # Navigate to the first result
        pyautogui.press('enter')
        await asyncio.sleep(1)  # Wait for the song page to open
        pyautogui.press('space')  # Press space to play


async def handle_small_talk(command):
    command = command.lower()
    for key in responses:
        if key in command:
            await speak(random.choice(responses[key]))
            return True
    return False

class AssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VIONEX AI")
        self.root.geometry("800x700")
        self.root.configure(bg="black")
        self.root.resizable(False, False)
        self.root.wm_attributes("-topmost", True)
        


        self.canvas = tk.Canvas(self.root, width=800, height=700, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        gif = Image.open(resource_path("elf2.gif"))
        frame_size = (800, 600)
        self.frames = [ImageTk.PhotoImage(img.resize(frame_size, Image.LANCZOS).convert('RGBA'))
                       for img in ImageSequence.Iterator(gif)]
        self.gif_index = 0
        self.bg_image = self.canvas.create_image(0, 0, anchor='nw', image=self.frames[0])
        self.animate()

        self.root.configure(bg="#000000")
        

        self.chat_log = Text(
            self.root,
            bg="#000000",
            fg="sky blue",
            font=("Consolas", 10,),
            wrap='word',
            bd=0
        )
        self.chat_log.place(x=0, y=600, width=800, height=100)
        self.chat_log.insert(END, "[System] Type your command below or press F2 to speak.\n")
        self.chat_log.config(state=tk.DISABLED)

        scrollbar = Scrollbar(self.root, command=self.chat_log.yview)
        scrollbar.place(x=780, y=600, height=100)
        self.chat_log.config(yscrollcommand=scrollbar.set)

        self.entry = tk.Entry(self.root, font=("Segoe UI", 13), bg="#1a1a1a", fg="white", bd=3, insertbackground='white')
        self.entry.place(x=20, y=670, width=700, height=30)
        self.entry.bind("<Return>", self.send_text)

        send_button = tk.Button(self.root, text="Send", command=self.send_text, bg="#222222", fg="white", relief='flat')
        send_button.place(x=730, y=670, width=50, height=30)

        self.root.bind("<F2>", lambda e: Thread(target=self.listen_voice).start())
        # Inside AssistantGUI.__init__(self):
        Thread(target=lambda: asyncio.run(time_based_greeting())).start()


    def animate(self):
        self.canvas.itemconfig(self.bg_image, image=self.frames[self.gif_index])
        self.gif_index = (self.gif_index + 1) % len(self.frames)
        self.root.after(100, self.animate)  # Keeps looping


    def send_text(self, event=None):
        user_input = self.entry.get()
        self.entry.delete(0, END)
        if user_input:
            self.add_text("You: " + user_input)
            Thread(target=lambda: asyncio.run(self.handle_command(user_input))).start()


    def add_text(self, text):
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(END, text + "\n")
        self.chat_log.config(state=tk.DISABLED)
        self.chat_log.see(END)

    def listen_voice(self):
        self.add_text("[System] Listening...")
        command = listen_command()
        if command:
            self.add_text("You: " + command)
            Thread(target=lambda: asyncio.run(self.handle_command(command))).start()

    




    async def handle_command(self, command):
        if command == "network error":
            self.add_text("[System] Network error")
            await speak("Network error.")
            return

        if await handle_small_talk(command):
            return

        if "open" in command:
            if await open_any_website(command):
                return

        if "close" in command:
            await close_application(command)
            return
        
        if "timer" in command:
           await set_timer(command)
           return

        if await repeat_after_me(command):
           return

        if "search" in command:
            await search_anything(command)
            return
        
        if await explain_meaning(command):
           return

        if await tell_about_topic(command):
           return


        if "tell me about" in command or "who is" in command:
            await tell_about_person(command)
            return

        if "play" in command and "spotify" in command:
            await play_song_on_spotify(command)
            return

        if "exit" in command:
            self.add_text("[System] Exiting...")
            await speak("Goodbye!")
            self.root.quit()
            return

        await speak("i dont understand what youre saying")
        self.add_text("AI: Can you repeat that?")

def main():
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()