from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.actionbar import ActionBar

from kivy.properties import ListProperty
from kivy.properties import StringProperty
from kivy.clock import Clock

import time

class BServerWidget(BoxLayout):
    ux_CurrTime = StringProperty(time.strftime('%H::%M::%S'))
    
    def updateTime(self, dt):
        self.ux_CurrTime = time.strftime('%H::%M::%S')

class BServerApp(App):
    DefaultSubjects = ListProperty(['Sub1', 'Sub2', 'Sub3', 'Sub4', 'Sub5', 'Sub6',
        'Sub7', 'Sub8', 'Sub9', 'Sub10', 'Sub11', 'Sub12',
        'Sub13', 'Sub14', 'Sub15', 'Sub16', 'Sub17', 'Sub18',
        'Sub19', 'Sub20', 'Sub21', 'Sub22', 'Sub23', 'Sub24',
        'Sub25', 'Sub26', 'Sub27', 'Sub28', 'Sub29', 'Sub30',
        'Sub31', 'Sub32', 'Sub33', 'Sub34', 'Sub35', 'Sub36'])
    DefaultStations = ListProperty(['Station1', 'Station2', 'Station3', 'Station4',
        'Station5', 'Station6'])
        
    def createSubjectListing(self, Subjects, Box):
        for Subject in Subjects:
            Box.add_widget(Button(text=Subject,
                size_hint=(1, None),
                height=30))
        return Box

    def createStationListing(self, Stations, Box):
        for Station in Stations:
            Box.add_widget(Button(text=Station,
                font_size=14
                ))
        return Box

    def build(self):
        bserver_widget = BServerWidget()
        Clock.schedule_interval(bserver_widget.updateTime, 1)
        return bserver_widget


if __name__ == "__main__":
    BServerApp().run()