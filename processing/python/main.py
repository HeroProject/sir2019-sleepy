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
import json
import AbstractApplication as Base
from threading import Semaphore

class DialogFlowSampleApplication(Base.AbstractApplication):
    dialog_list     = []
    dialog_answers  = {}
    name            = ""
    number_of_tries = 0
    randomString    = ""

    # the number represents the story id
    animal_story_list = {
        "gorilla":  [190, 124, 622, 30, 66, 124],
        "elephant": [622, 30],
        "cats":     [66, 124],
        "lion":     [124, 122, 30]
    }

    def yaml_open(self, dialog_name):

        # Open yaml file
        print("\033[1;35;40m [-] \x1B[0m \t \033[1;37;40m running: \x1B[0m "+dialog_name)
        with open(r'dialogs/'+dialog_name) as file:

            # load yaml file
            output = yaml.load(file, Loader=yaml.FullLoader)

            # print("\n"+json.dumps(output, indent=4, sort_keys=True))


            # nao pre gesture
            self.play_gesture(self.get_input(output, "pre_gesture"))

            # nao pre talk
            # self.talk(self.get_input(output, "pre_talk"))

            sub3 = self.get_input(output, "pre_talk")
            for words in DialogFlowSampleApplication.dialog_answers:
                sub3 = self.subs_words(sub3, DialogFlowSampleApplication.dialog_answers[words], rule='\[[ ]?'+words+'[ ]?\]')

            self.talk(sub3)

            # get name, this should correspond to dialogname
            name		= self.get_input(output, "name")
            name_filt   = name.replace("_", "")

            DialogFlowSampleApplication.dialog_list.append(name)

            # load timeouts
            listen_timeout	= self.get_input(output, "listen_timeout")
            lock_timeout	= self.get_input(output, "lock_timeout")

            print("\033[1;35;40m [-] \x1B[0m \t \033[1;37;40m name: \x1B[0m "+name)

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
            print("\033[1;35;40m [-] \x1B[0m \t \033[1;37;40m robot_input: \x1B[0m "+robot_input)
            self.setEyeColour("white")

            i = 0
            response = False

            # print(output)
            total_options = len(self.get_input(output, "catch_success"))

            if "catch_success" in output:

                for catch_success in self.get_input(output, "catch_success"):
                    i += 1
                    regex_match = catch_success["match"]

                    if robot_input:
                        print("\033[1;35;40m [-] \x1B[0m \t \033[1;37;40m Regex match: \x1B[0m "+regex_match)
                        print("\033[1;35;40m [-] \x1B[0m \t \033[1;37;40m Regex input: \x1B[0m "+robot_input)
                        match = re.match(regex_match, robot_input)

                        if match:
                            response = True
                            print("\033[1;35;40m [ \U00002714 ] \x1B[0m \t \033[1;38;40m Match True: \x1B[0m ")

                            # Talk
                            sub = self.subs_words(catch_success[True]["talk"], robot_input)
                            for words in DialogFlowSampleApplication.dialog_answers:
                                sub = self.subs_words(sub, DialogFlowSampleApplication.dialog_answers[words], rule='\[[ ]?'+words+'[ ]?\]')

                            self.talk(sub)

                            # Play gesture
                            if self.get_input(catch_success[True], "gesture") != "":
                                self.play_gesture(catch_success[True]["gesture"])



                            # Talk
                            if self.get_input(catch_success[True], "post_talk") != "":
                                sub2 = self.subs_words(catch_success[True]["post_talk"], robot_input)
                                for words in DialogFlowSampleApplication.dialog_answers:
                                    sub2 = self.subs_words(sub2, DialogFlowSampleApplication.dialog_answers[words], rule='\[[ ]?'+words+'[ ]?\]')

                                self.talk(sub2)

                            # Go To next dialog or call a method
                            # print("caatcch", catch_success)
                            print(self.get_goto(catch_success[True]["goto"]))
                        else:
                            print("\033[5;33;40m [ \U00002757 ] \x1B[0m \t \033[1;33;40m Match False: \x1B[0m ")


            if not response:
                # generate new unique string and add +1 to number of tries
                # DialogFlowSampleApplication.randomString    = self.randomString()
                DialogFlowSampleApplication.number_of_tries += 1
                self.setEyeColour("red")
                print("\033[5;32;40m [ \U00002757 ] \x1B[0m match fail")

                # Play gesture
                self.play_gesture(self.get_input(output["catch_fail_recognize"], "gesture"))

                # Talk
                self.talk(self.get_input(output["catch_fail_recognize"], "talk"))

                # sleep 1 second, before moving
                time.sleep(1)

                # Go To next dialog or call a method
                self.setEyeColour("white")
                if DialogFlowSampleApplication.number_of_tries < self.get_input(output["catch_fail_recognize"], "max_tries"):
                    self.yaml_open(dialog_name)
                else:
                    DialogFlowSampleApplication.dialog_answers[name] = ""
                    self.get_goto(self.get_input(output["catch_fail_recognize"], "max_tries_goto"))


            self.speechLock.acquire()
            DialogFlowSampleApplication.name = False

    def pick_story(self):
        print("\033[1;35;40m [ \U00002714 ] \x1B[0m \t \033[1;38;40m pick story! \x1B[0m ")
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


            # when favorite animal exists, otherwise the favorite animal question is skipped
            read_story_id = 190
            DialogFlowSampleApplication.dialog_answers["favorite_animal"] = "gorilla"
            if "favorite_animal" in DialogFlowSampleApplication.dialog_answers:
                if DialogFlowSampleApplication.dialog_answers["favorite_animal"] in DialogFlowSampleApplication.animal_story_list:

                # when the favorite animal is inside the story list
                    if not DialogFlowSampleApplication.animal_story_list[DialogFlowSampleApplication.dialog_answers["favorite_animal"]]:
                        # list is empty
                        print("empty")
                    else:
                        print(DialogFlowSampleApplication.animal_story_list)
                        # pick the first numer
                        read_story_id = random.choice(DialogFlowSampleApplication.animal_story_list[DialogFlowSampleApplication.dialog_answers["favorite_animal"]])
                        print(read_story_id)

                        # remove from list
                        DialogFlowSampleApplication.animal_story_list[DialogFlowSampleApplication.dialog_answers["favorite_animal"]].remove(read_story_id)

            story_name_1		= split_stories[read_story_id-1]
            story_text_1		= split_stories[read_story_id]
            print(story_name_1)

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

            print("robot input", robot_input)
            # Respond and wait for that to finish
            if robot_input:

                if re.match("^(yes)", robot_input):
                    self.talk('Nice, I will read the story: '+story_name_1)

                    for sentence in story_text_1.split("."):
                        print(sentence)
                        self.talk(sentence)
                        time.sleep(1)

                else:
                    # pick another story
                    self.pick_story()
                    return

            else:
                print("\033[5;32;40m [ \U00002757 ] \x1B[0m Fail recognizing")
                self.talk('Sorry, I didn\'t catch your answer.')
                self.pick_story()

            self.speechLock.acquire()


    def subs_words(self, input, replace, rule='\[[ ]?input[ ]?\]'):
        """
        This function subsitutes words
        e.g.
        Input sentence: This [input] / [ input ] is an example
        Replace: method

        returns This method / method is an example
        """
        return re.sub(rule, replace, input)


    def get_goto(self, goto):
        """
        This function routes particular goto argument to a yaml file
        when a yaml extension is found. If this is not found the
        function will see this as a function and call it.
        """

        # generate random string. This will prevent locking problems.
        DialogFlowSampleApplication.name            = ""
        DialogFlowSampleApplication.randomString    = "randomstring"
        DialogFlowSampleApplication.number_of_tries = 0

        print("")
        print("------------------------------")
        print("\033[1;37;40m  == \U0001F916 ==  \x1B[0m")

        if bool(DialogFlowSampleApplication.dialog_answers):
            print("\n\033[5;34;36m"+json.dumps(DialogFlowSampleApplication.dialog_answers, indent=4, sort_keys=True)+"\x1B[0m")

        print("\033[1;36;40m  goto: "+goto+" \x1B[0m")
        print("------------------------------")
        print("")

        if re.search("(yaml)$", goto):
            self.yaml_open(goto)
        else:
            if hasattr(self, goto):
                print("function call")
                getattr(self, goto)()

    def play_gesture(self, gesturename):
        if gesturename is not "":
            """ Play gestures """
            print("\033[1;35;40m [-] \x1B[0m \t \033[1;37;40m gesture start: \x1B[0m "+gesturename)

            self.gestureLock = Semaphore(0)

            self.doGesture(gesturename)

            self.gestureLock.acquire()

            print("\033[1;35;40m [-] \x1B[0m \t \033[1;37;40m gesture stop \x1B[0m ")

    def get_input(self, arr, name):
        """
        Check if object exists, if not empty string returned
        """
        try:
            return(arr[name])
        except:
            print("\033[1;32;40m [ \U00002757 ] \x1B[0m [!] no "+name+" found in ", arr)
        return ""

    def str_to_class(self, str):
        return getattr(sys.modules, str)

    def main(self):
        """ Main """
        self.setRecordAudio(True)
        self.langLock = Semaphore(0)
        # self.setLanguage('tr-TR')
        self.setLanguage('en-US')
        self.langLock.acquire()

        # Dialogflow
        self.setDialogflowKey("config/keyfile.json")
        self.setDialogflowAgent("sleepy-gbdtuq")

        # name of yaml file, inside dialogs directory
        self.get_goto("meeting_robot.yaml")
        # self.get_goto("pick_story")

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
        elif event == 'MiddleTactilTouched':
            print("stop")
            self.talk("it was nice to meet you")

        # elif event == "RightBumperPressed":
        #     self.talk("Ouch! Don not do that you are so rude! Fuck you")
        #     self.speechLock.release()
        #     self.gestureLock.release()
        # elif event == "LeftBumperPressed":
        #     self.talk("Don't touch my foot")
        #     self.speechLock.release()
        #     self.turnLeft()
        #     self.gestureLock.release()
        # print(event)

    def randomString(self, stringLength=10):
        letters = string.ascii_lowercase
        r = ''.join(random.choice(letters) for i in range(stringLength))
        return r

    def onAudioIntent(self, *args, intentName):
        # print("args", args)
        # print("intentname", intentName)

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
