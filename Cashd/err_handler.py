from time import sleep

def countdown_message(message, error, seconds = 10):
   while seconds > 0:
      print(error + "\n", message, seconds, end = "\r", sep ="")
      sleep(1)
      seconds -= 1
   quit()