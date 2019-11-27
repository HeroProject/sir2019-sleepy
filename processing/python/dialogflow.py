import AbstractApplication as Base
from threading import Semaphore

class DialogFlowSampleApplication(Base.AbstractApplication):
    def __init__(self, keyfile, agent):
        self.langLock = Semaphore(0)
        self.setLanguage('en-US')
        self.langLock.acquire()

        # Dialogflow
        self.setDialogflowKey(keyfile)
        self.setDialogflowAgent(agent)

    def meetingRobot(self):
        self.talk("Hello, I am Sleepy")

    def askingName(self):
        cloud_context   = 'answer_name'
        listen_timeout  = 5

        self.talk('what is your name?')

        self.name = None
        self.nameLock = Semaphore(0)
        self.setAudioContext(cloud_context)
        self.startListening()
        self.nameLock.acquire(timeout=listen_timeout)
        self.stopListening()
        if not self.name:  # wait one more second after stopListening (if needed)
            self.nameLock.acquire(timeout=1)

        # Respond and wait for that to finish
        if self.name:
            self.sayAnimated('Nice to meet you ' + self.name + '!')
        else:
            self.sayAnimated('Sorry, I didn\'t catch your name.')
            self.askingName()
        self.speechLock.acquire()

    def readStory(self):
        cloud_context   = 'ask_read_story'
        listen_timeout  = 5

        self.talk('Do you want me to read a story?')

        self.read_story = None
        self.read_storyLock = Semaphore(0)
        self.setAudioContext(cloud_context)
        self.startListening()
        self.read_storyLock.acquire(timeout=listen_timeout)
        self.stopListening()
        if not self.read_story:  # wait one more second after stopListening (if needed)
            self.read_storyLock.acquire(timeout=1)

        # Respond and wait for that to finish
        if self.read_story:
            self.sayAnimated('Nice I will read a story.')
        else:
            self.sayAnimated('Sorry, I didn\'t catch your answer.')
            self.readStory()
        self.speechLock.acquire()

    def personalInterest(self):
        cloud_context   = 'personal_interest'
        listen_timeout  = 5

        self.talk('Do you like to play footbal?')

        self.personal_story = None
        self.personal_storyLock = Semaphore(0)
        self.setAudioContext(cloud_context)
        self.startListening()
        self.read_storyLock.acquire(timeout=listen_timeout)
        self.stopListening()
        if not self.personal_story:  # wait one more second after stopListening (if needed)
            self.personal_storyLock.acquire(timeout=1)

        # Respond and wait for that to finish
        if self.personal_story:
            self.sayAnimated('ohh')
        else:
            self.sayAnimated('Sorry, I didn\'t understand.')
            self.personalInterest()
        self.speechLock.acquire()

    def main(self):
        self.meetingRobot()
        self.askingName()
        self.readStory()
        self.personalInterest()

    def talk(self, message):
        self.speechLock = Semaphore(0)
        self.sayAnimated(message)
        self.speechLock.acquire()

    def onRobotEvent(self, event):
        if event == 'LanguageChanged':
            self.langLock.release()
        elif event == 'TextDone':
            self.speechLock.release()
        elif event == 'GestureDone':
            self.gestureLock.release()

    def onAudioIntent(self, *args, intentName):
        print(args)
        print(intentName)
        if intentName == 'answer_name' and len(args) > 0:
            self.name = args[0]
            self.nameLock.release()

        if intentName == 'ask_read_story' and len(args) > 0:
            self.read_story = args[0]
            self.read_storyLock.release()

        if intentName == 'personal_interest' and len(args) > 0:
            self.personal_story = args[0]
            self.personal_storyLock.release()


# Run the application
sample = DialogFlowSampleApplication("keyfile.json", "sleepy-gbdtuq")
sample.main()
sample.stop()
