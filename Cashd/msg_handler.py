import time

def countdown_message(*message, seconds = 5):
   while seconds > 0:
      print(message, seconds, end = "\r", sep ="")
      time.sleep(1)
      seconds -= 1
   quit()
