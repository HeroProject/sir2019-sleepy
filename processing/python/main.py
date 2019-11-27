#!/usr/bin/env python3

"""
Socially Intelligent Robotics
"""

__author__     = 'Ersin Topuz'
__copyright__  = 'Copyright 2019'
__license__    = 'MIT'
__version__    = '0.0.1'
__maintainer__ = 'Ersin, Zeynep, Tomer, Oktay, Marijn and Erkin'
__email__      = 'ersin@hotmail.nl'
__status__     = 'Development'

import yaml
import re
import os
import random
import string
import time
import sys
import AbstractApplication as Base
from threading import Semaphore

class DialogFlowSampleApplication(Base.AbstractApplication):
    dialog_list     = []
    dialog_answers  = {}
    name            = ""
    number_of_tries = 0
    randomString    = ""

    def yaml_open(self, dialog_name):

        # Open yaml file
        print("\033[1;35;40m [!] \x1B[0m running: "+dialog_name)
        with open(r'dialogs/'+dialog_name) as file:

            # load yaml file
            output = yaml.load(file, Loader=yaml.FullLoader)

            # nao pre gesture
            self.play_gesture(self.get_input(output, "pre_gesture"))

            # nao pre talk
            self.talk(self.get_input(output, "pre_talk"))

            # get name, this should correspond to dialogname
            name		= self.get_input(output, "name")
            name_filt   = name.replace("_", "")

            DialogFlowSampleApplication.dialog_list.append(name)

            # load timeouts
            listen_timeout	= self.get_input(output, "listen_timeout")
            lock_timeout	= self.get_input(output, "lock_timeout")

            print("\033[1;35;40m [-] \x1B[0m name: "+name)

            # declare variables
            setattr(self, name_filt, None)
            setattr(self, name_filt+DialogFlowSampleApplication.randomString+"Lock", Semaphore(0))

            self.setAudioContext(name)

            # set eyecolour to blue, since nao is in listen mode
            self.setEyeColour("blue")
            self.startListening()

            # lock mode for audio
            result = getattr(self, name_filt+DialogFlowSampleApplication.randomString+'Lock')
            print(result.acquire(timeout=listen_timeout))

            self.stopListening()

            # print("\033[1;35;40m [-] \x1B[0m response: "+getattr(self, name_filt).str())

            if not getattr(self, name_filt):
                print(result.acquire(timeout=lock_timeout))

            robot_input = DialogFlowSampleApplication.name
            print("robot_input", robot_input)
            self.setEyeColour("white")

            i = 0
            response = False

            print(output)
            total_options = len(self.get_input(output, "catch_success"))

            if "catch_success" in output:

                for catch_success in self.get_input(output, "catch_success"):
                    i += 1
                    regex_match = catch_success["match"]

                    if robot_input:
                        print("match", regex_match)
                        print("input", robot_input)
                        match = re.match(regex_match, robot_input)

                        if match:
                            response = True
                            print("\033[1;35;40m [*] \x1B[0m match true")

                            # Talk
                            sub = self.subs_words(catch_success[True]["talk"], robot_input)
                            for words in DialogFlowSampleApplication.dialog_answers:
                                sub = self.subs_words(sub, DialogFlowSampleApplication.dialog_answers[words], rule='\[[ ]?'+words+'[ ]?\]')

                            self.talk(sub)

                            # Play gesture
                            self.play_gesture(catch_success[True]["gesture"])

                            # Go To next dialog or call a method
                            # print("caatcch", catch_success)
                            print(self.get_goto(catch_success[True]["goto"]))


            if not response:
                # generate new unique string and add +1 to number of tries
                # DialogFlowSampleApplication.randomString    = self.randomString()
                DialogFlowSampleApplication.number_of_tries += 1

                print("\033[1;35;40m [*] \x1B[0m match fail")

                # Play gesture
                self.play_gesture(self.get_input(output["catch_fail_recognize"], "gesture"))

                # Talk
                self.talk(self.get_input(output["catch_fail_recognize"], "talk"))

                # print("\033[1;35;40m [!] \x1B[0m tries ["+DialogFlowSampleApplication.number_of_tries.str()+"/"+self.get_input(output["catch_fail_recognize"])+"]")

                # sleep 1 second, before moving
                time.sleep(1)

                # Go To next dialog or call a method
                if DialogFlowSampleApplication.number_of_tries < self.get_input(output["catch_fail_recognize"], "max_tries"):
                    self.yaml_open(dialog_name)
                else:
                    self.get_goto(self.get_input(output["catch_fail_recognize"], "max_tries_goto"))


            self.speechLock.acquire()
            DialogFlowSampleApplication.name = False

    def pick_story(self):
        print("pick story!")
        with open("story/story.txt") as file:
            split_stories = re.split("\n{5,10}(.+)\n{1}", file.read())

            # 190 - The Heart of a Monkey
            # 136 - Tale of a Tortoise and of a Mischievous Monkey
            # 622 - Why the Fish Laughed
            # 30 - The Cottager And His Cat
            # 66 - The Colony Of Cats
            # 122 - Kisa the Cat
            # 124 - The Lion and the Cat

            # pick_random_story	= random.randrange(0, len(split_stories), 2)
            story_name_1		= split_stories[190-1]
            story_text_1		= split_stories[190]

            self.talk("Would you like to hear "+story_name_1+"?")

            name            = 'read_story'
            name_filt       = name.replace("_", "")
            listen_timeout  = 5

            DialogFlowSampleApplication.dialog_list.append(name)
            # DialogFlowSampleApplication.randomString = self.randomString()

            setattr(self, name_filt, None)
            setattr(self, name_filt+DialogFlowSampleApplication.randomString+"Lock", Semaphore(0))

            self.setAudioContext(name)
            self.startListening()

            result = getattr(self, name_filt+DialogFlowSampleApplication.randomString+'Lock')
            print(result.acquire(timeout=listen_timeout))
            lock_timeout = 5

            self.stopListening()
            if not getattr(self, name_filt):
                print(result.acquire(timeout=lock_timeout))

            robot_input = DialogFlowSampleApplication.name
            # Respond and wait for that to finish
            if robot_input:
                self.talk('Nice, I will read the story')

                # sentences = re.split("(.?).", story_text_1)

                self.talk(story_text_1)
            else:
                self.talk('Sorry, I didn\'t catch your answer.')
                self.pick_story():

            self.speechLock.acquire()


    def subs_words(self, input, replace, rule='\[[ ]?input[ ]?\]'):
        """
        This function subsitutes words
        e.g.
        Input sentence: This [input] / [ input ] is an example
        Replace: method

        returns This method / method is an example
        """
        print("rule", rule)
        print("replace", replace)
        print("input", input)
        return re.sub(rule, replace, input)


    def get_goto(self, goto):
        """
        This function routes particular goto argument to a yaml file
        when a yaml extension is found. If this is not found the
        function will see this as a function and call it.
        """
        # create_random_string = self.randomString()
        create_random_string = "aa"

        # print(create_random_string, type(create_random_string))

        # generate random string. This will prevent locking problems.
        DialogFlowSampleApplication.name            = ""
        DialogFlowSampleApplication.randomString    = create_random_string
        DialogFlowSampleApplication.number_of_tries = 0

        print("")
        print(" == Dialog Answers == ")
        print(DialogFlowSampleApplication.dialog_answers)
        print("")
        print("goto", goto)
        print(type(goto))

        if re.search("(yaml)$", goto):
            self.yaml_open(goto)
        else:
            print(">>>")
            # print(dir(os))
            # goto = "pick_story"
            getattr(self, goto)()
            # getattr(self, goto)()

            # if goto in dir(os):
            #     print("call")
            #     globals()[goto]()

    def play_gesture(self, gesturename):
        if gesturename is not "":
            """ Play gestures """
            print("\033[1;35;40m [-] \x1B[0m gesture start: "+gesturename)

            self.gestureLock = Semaphore(0)

            print("\033[1;35;40m [-] \x1B[0m gesture name: "+gesturename)

            # try:
            # print("--- gesture",
            self.doGesture(gesturename)
            # excepy:
            self.gestureLock.acquire()

            print("\033[1;35;40m [-] \x1B[0m gesture stop")

    def get_input(self, arr, name):
        """
        Check if object exists, if not empty string returned
        """
        try:
            return(arr[name])
        except:
            print("[!] no "+name+" found in ", arr)
        return ""

    def str_to_class(self, str):
        return getattr(sys.modules, str)

    def main(self):

        # a = getattr(self, goto)
        # a
        # globals()[goto]()
        # self.str_to_class(goto)
        # globals()["pick_story"]()

        """ Main """
        self.setRecordAudio(True)
        self.langLock = Semaphore(0)
        self.setLanguage('en-US')
        self.langLock.acquire()

        # Dialogflow
        self.setDialogflowKey("config/keyfile.json")
        self.setDialogflowAgent("sleepy-gbdtuq")

        # name of yaml file, inside dialogs directory
        self.get_goto("meeting_robot.yaml")

    def talk(self, message):
        """ Talk """
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
        elif event == "RightBumperPressed":
            self.talk("Ouch! Don not do that you are so rude! Fuck you")
        elif event == "LeftBumperPressed":
            self.talk("Don't touch my foot")
            self.turnLeft()
        # print("aa")

    def randomString(self, stringLength=10):

        letters = string.ascii_lowercase
        a = ''.join(random.choice(letters) for i in range(stringLength))
        self.talk(a)
        return a

    def onAudioIntent(self, *args, intentName):
        print("args", args)
        print("intentname", intentName)

        if intentName in DialogFlowSampleApplication.dialog_list and len(args) > 0:
            # save in DialogFlowSampleApplication.name
            DialogFlowSampleApplication.name = args[0]
            DialogFlowSampleApplication.dialog_answers[intentName] = args[0]

            # lock nameLock
            lockfunction = getattr(self, intentName.replace("_", "")+DialogFlowSampleApplication.randomString+"Lock")
            lockfunction.release()

# Run the application
sample = DialogFlowSampleApplication()
sample.main()
sample.stop()
