import re
import os
import time
import logging
import requests
import unicodedata
from os import path
from gtts import gTTS
from pygame import mixer
from modules import app, cbpi, DBModel
from thread import start_new_thread

mixer.init()
SayIt = None
SayIt_Voice = None
SayIt_Volume = None
RootDir = os.path.dirname(os.path.abspath(__file__))
SayItLang = [["el", "Greek"], ["zh-cn", "Chinese (Mandarin/China)"], ["my", "Myanmar (Burmese)"], ["mr", "Marathi"], ["pt-br", "Portuguese (Brazil)"], ["ml", "Malayalam"], ["uk", "Ukrainian"], ["en-in", "English (India)"], ["en-nz", "English (New Zealand)"], ["de", "German"], ["sk", "Slovak"], ["mk", "Macedonian"], ["sv", "Swedish"], ["sw", "Swahili"], ["no", "Norwegian"], ["sq", "Albanian"], ["sr", "Serbian"], ["pt-pt", "Portuguese (Portugal)"], ["te", "Telugu"], ["km", "Khmer"], ["en-ca", "English (Canada)"], ["ja", "Japanese"], ["hu", "Hungarian"], ["fi", "Finnish"], ["bs", "Bosnian"], ["hi", "Hindi"], ["es-us", "Spanish (United States)"], ["da", "Danish"], ["ko", "Korean"], ["jw", "Javanese"], ["bn", "Bengali"], ["en-ie", "English (Ireland)"], ["hr", "Croatian"], ["en-tz", "English (Tanzania)"], ["hy", "Armenian"], ["fr", "French"], ["ta", "Tamil"], ["pl", "Polish"], ["is", "Icelandic"], ["ro", "Romanian"], ["en-za", "English (South Africa)"], ["th", "Thai"], ["tl", "Filipino"], ["si", "Sinhala"], ["lv", "Latvian"], ["ne", "Nepali"], ["tr", "Turkish"], ["en-gh", "English (Ghana)"], ["zh-tw", "Chinese (Mandarin/Taiwan)"], ["en-uk", "English (UK)"], ["la", "Latin"], ["pt", "Portuguese"], ["en-ph", "English (Philippines)"], ["nl", "Dutch"], ["ru", "Russian"], ["en-gb", "English (UK)"], ["es", "Spanish"], ["id", "Indonesian"], ["es-es", "Spanish (Spain)"], ["et", "Estonian"], ["cs", "Czech"], ["su", "Sundanese"], ["fr-fr", "French (France)"], ["ar", "Arabic"], ["cy", "Welsh"], ["en-ng", "English (Nigeria)"], ["it", "Italian"], ["fr-ca", "French (Canada)"], ["en-us", "English (US)"], ["ca", "Catalan"], ["vi", "Vietnamese"], ["af", "Afrikaans"], ["en-au", "English (Australia)"], ["en", "English"], ["eo", "Esperanto"]]


@cbpi.initalizer(order=9000)
def init(cbpi):
    print("Initializing the SayIt plugin by Lawrence Wagy")
    cbpi.app.logger.info("Initializing the SayIt plugin.")
    global SayIt

    SayItVoice()
    SayItVolume()
    if SayIt_Voice is None or not SayIt_Voice:
        cbpi.notify("SayIt Plugin Error", "Check the SayIt voice parameter", type="Warning", timeout=None)
    else:
        try:
           mixer.music.set_volume(float("{0:.1f}".format(float(SayIt_Volume)/9)))
        except:
            cbpi.notify("SayIt Error", "Unable to set the volume.", type="Warning", timeout=None)
            return
        SayIt = "SayIt Initialized"
        messageEvent({'headline': '', 'id': '', 'message': 'SayIt Plugin has been Initialized. Volume level ' + SayIt_Volume, 'timeout': None, 'type': ''})

            
def SayItVoice():
    global SayIt_Voice
    SayIt_Voice = cbpi.get_config_parameter("SayIt_Voice", None)
    if SayIt_Voice is None:
        try:
            VoiceOptions = []
            for key, value in SayItLang:
                VoiceOptions.insert(1, value)
            cbpi.add_config_parameter("SayIt_Voice", "", "select", "SayIt Voice Selection", VoiceOptions)
        except:
            cbpi.notify("SayIt Error", "Unable to update the database. Update the CraftBeerPi and try rebooting.", type="Warning", timeout=None)


def SayItVolume():
    global SayIt_Volume
    SayIt_Volume = cbpi.get_config_parameter("SayIt_Volume", None)
    if SayIt_Volume is None:
        try:
            VolumeOptions = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            cbpi.add_config_parameter("SayIt_Volume", "0", "select", "SayIt Volume Level", VolumeOptions)
            SayIt_Volume = cbpi.get_config_parameter("SayIt_Volume", None)
        except:
            cbpi.notify("SayIt Error", "Unable to update the database. Update the CraftBeerPi and try rebooting.", type="Warning", timeout=None)
            cbpi.app.logger.error("SayIt Error - Unable to update the database. Update the CraftBeerPi and try rebooting.")

def CleanFileName(value):
    value = str(value).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w]', '', value)


@cbpi.event("MESSAGE", async=True)
def messageEvent(message):
    if SayIt is not None:
        SayIt_Message ='{0}, {1}, {2}'.format(message["type"], message["headline"], message["message"])
    
        for key, value in SayItLang:
            if value == SayIt_Voice:
                tts = gTTS(SayIt_Message, lang=key)

        TypeDir = os.path.join(RootDir, 'Notifications' , SayIt_Voice, CleanFileName(message["type"]))
        AudioFile = CleanFileName(message["message"])
        AudioFilePath = os.path.join(TypeDir, AudioFile)
        if os.path.exists(TypeDir) == False:
            os.makedirs(TypeDir)
        try:
            if os.path.exists(AudioFilePath) == False:
                tts.save(AudioFilePath)
        except Exception as ex:
            os.remove(AudioFilePath)
            print('SayIt - Unable to save audio file: ' + ex.message)
            return

        mixer.music.load(AudioFilePath)
        mixer.music.play()
