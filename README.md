project_template/
├── src/
│   ├── main.coco
│   ├── schedule_manager.coco
│   ├── chatbot.coco
│   ├── github_integration.coco
│   ├── debug_tools.coco
├── tests/
│   ├── test_schedule_manager.coco
│   ├── test_chatbot.coco
│   ├── test_github_integration.coco
├── requirements.txt
├── README.md
├── .gitignore
└── setup.cfgfrom schedule_manager import *
from chatbot import *
from github_integration import *
from debug_tools import *

def main():
    print("Witamy w projekcie {project_name}!")

if __name__ == "__main__":
    main()data Brygada = Brygada(nazwa, pracownicy)

def utworz_harmonogram(brygady, zmiany):
    harmonogram = {}
    for i, brygada w enumerate(brygady):
        harmonogram[brygada.nazwa] = zmiany[i % len(zmiany)]
    return harmonogram

def pokaz_harmonogram(harmonogram):
    for brygada, zmiana w harmonogram.items():
        print(f"{brygada} ma {zmiana}")import speech_recognition as sr
from gtts import gTTS
import os

def rozpoznaj_mowe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Powiedz coś:")
        audio = recognizer.listen(source)
    try:
        tekst = recognizer.recognize_google(audio, language="pl-PL")
        print("Rozpoznano: " + tekst)
        return tekst
    except sr.UnknownValueError:
        print("Nie rozpoznano mowy")
    except sr.RequestError as e:
        print("Błąd usługi rozpoznawania mowy; {0}".format(e))

def generuj_mowe(tekst):
    tts = gTTS(text=tekst, lang='pl')
    tts.save("mowa.mp3")
    os.system("mpg321 mowa.mp3")import requests

def pobierz_repozytoria_uzytkownika(uzytkownik):
    url = f"https://api.github.com/users/{uzytkownik}/repos"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def pobierz_szczegoly_repozytorium(uzytkownik, repo):
    url = f"https://api.github.com/repos
I😁- 👋 Hi, I’m @Thenomad123
- 👀 I’m interested in ...
- 🌱 I’m currently learning ...
- 💞️ I’m looking to collaborate on ...
- 📫 How to reach me ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...

<!---
Thenomad123/Thenomad123 is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->
examples/audio.py