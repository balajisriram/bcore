#from BCore.Classes.ClientAndServer.BServer import BServer
#import Kivy

from kivy.app import App

from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout


class BServerGUI(App):

    def __init__(self, *args):
        if not args:
            self.data = None
        else:
            self.data = args[0]

    def build(self):
        f = FloatLayout()
        s = Scatter()
        l = Label(text="Hello!",
                font_Size=150)
        f.add_widget(s)
        s.add_widget(l)
        return f


if __name__ == "__main__":
    BServerGUI().run()