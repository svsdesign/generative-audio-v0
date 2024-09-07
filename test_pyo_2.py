from pyo import Server

# Start the server without GUI and MIDI
s = Server().boot()
s.start()

# A simple sine wave as a test
a = Sine().out()

# Keep the script running
s.gui(locals(), exit=False)
