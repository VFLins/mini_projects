import PySimpleGUI as sgui

layout = [
  [sgui.Text("What's your name?")],
  [sgui.Input(key='-INPUT-')],
  [sgui.Text(size=(40,1), key='-OUTPUT-')],
  [sgui.Button('Ok'), sgui.Button('Quit')]
]

# Create the window
window = sgui.Window('Window Title', layout)

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sgui.WINDOW_CLOSED or event == 'Quit':
        break
    # Output a message to the window
    window['-OUTPUT-'].update('Hello ' + values['-INPUT-'] + "! Thanks for trying PySimpleGUI")

# Finish up by removing from the screen
window.close()
