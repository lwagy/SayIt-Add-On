from thread import start_new_thread
from modules import app, cbpi
import requests
import logging
import pyttsx
import time

SayIt_Volume = None
SayIt_Voice = None
SayIt = None
TTS = pyttsx.init()



@cbpi.initalizer(order=9000)
def init(cbpi):
    print("Initializing the SayIt plugin by Lawrence Wagy")
    cbpi.app.logger.info("Initializing the SayIt plugin by Lawrence Wagy")
    global SayIt
    cbpi.app.logger.info("Initialize SayIt Plugin")
    SayItVoice()
    SayItVolume()
    if SayIt_Voice is None or not SayIt_Voice:
        cbpi.notify("SayIt Plugin Error", "Check the SayIt voice parameter", type="Warning", timeout=None)
    else:
        voices = TTS.getProperty('voices')
        for voice in voices:
            if SayIt_Voice == voice.name:
                TTS.setProperty('voice', voice.id)
                try:
                    TTS.setProperty('volume', float(SayIt_Volume)/9)
                except:
                    cbpi.notify("SayIt Error", "Unable to set the volume.", type="Warning", timeout=None)
                    cbpi.app.logger.error("SayIt Error - Unable to set the volume.")
        TTS.setProperty('rate', 150)
        SayIt = "SayIt Initialized"
        TTS.say(SayIt)
        
        


def SayItVoice():
    global SayIt_Voice
    SayIt_Voice = cbpi.get_config_parameter("SayIt_Voice", None)
    if SayIt_Voice is None:
        try:
            VoiceOptions = []
            voices = TTS.getProperty('voices')
            
            for voice in voices:
                VoiceOptions.insert(1,voice.name)
            
            cbpi.add_config_parameter("SayIt_Voice", "", "select", "SayIt Voice Selection", VoiceOptions)
        except:
            cbpi.notify("SayIt Error", "Unable to update the database. Update the CraftBeerPi and try rebooting.", type="Warning", timeout=None)
            cbpi.app.logger.error("SayIt Error -Unable to update the database. Update the CraftBeerPi and try rebooting.")
            


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
            


@cbpi.event("MESSAGE", async=True)
def messageEvent(message):
    if SayIt == None: return
    SayIt_Message ='{0},{1},{2}'.format(message["type"], message["headline"], message["message"])
    TTS.say(SayIt_Message)
    TTS.runAndWait()
    #TTS.startLoop()
    #TTS.endLoop()
