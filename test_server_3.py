import threading
import kivy
from kivy.app import App
from flask import Flask
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty
import os
from kivy.uix.label import Label
#kivy.require('1.10.0')
new_environ = os.environ.copy()

app = Flask(__name__)
GUI = None

@app.route('/')
def hello():
    global GUI
    GUI.trigger = False
    GUI.trigger = True
    return 'Hello World'

def start_app():
    print("Starting Flask app...")
    app.run(debug=False,port=5000,host='192.168.100.241')

class FlaskHook(Widget):
    trigger = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(FlaskHook, self).__init__(**kwargs)
        global GUI  # Needed to modify global copy of GUI
        GUI = self
        if os.environ.get("WERKZEUG_RUN_MAIN") != 'true':
            threading.Thread(target=start_app).start()
        self.fbind('trigger', self._trigger_callback)
        self.text_widget = Label(text=" Before Call")
        self.add_widget(self.text_widget)

    def _trigger_callback(self, obj1, obj2):
        self.text_widget.text = "After Call"
        print('event on object', obj1, obj2)
        print("Trigger callback")

class MyApp(App):
    def build(self):
        return FlaskHook()


if __name__ == '__main__':
    MyApp().run()