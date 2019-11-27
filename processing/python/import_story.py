import re

with open("story/story.txt") as file:
    split_stories = re.split("\n{5,10}(.+)\n{1}", file.read())

    i = 1
    for s in split_stories:
      if(i % 2 == 0):
        if isinstance(s, str):
           print(str(i)+' '+s.lower().capitalize())
      i += 1
