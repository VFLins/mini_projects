from time import sleep

def countdown_message(*message, seconds = 10):
   while seconds > 0:
      print(message, seconds, end = "\r", sep ="")
      sleep(1)
      seconds -= 1
   quit()