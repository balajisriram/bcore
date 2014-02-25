from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout  # lint:ok
from kivy.uix.scrollview import ScrollView  # lint:ok
from kivy.uix.button import Button
from kivy.uix.label import Label  # lint:ok
from kivy.uix.actionbar import ActionBar  # lint:ok
from kivy.uix.popup import Popup  # lint:ok
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition

from kivy.properties import ListProperty
from kivy.properties import StringProperty
from kivy.clock import Clock

from kivy.config import Config

import time


class HelpText(Label):
    def changeText(self, text):
        self.text = text


class StationButton(Button):

    ux_LIGHTGREENCOLOR = [0.56, 0.93, 0.56, 0.75]
    ux_LIGHTREDCOLOR = [0.93, 0.56, 0.56, 0.75]

class BServerWidget(BoxLayout):
    ux_CurrTime = StringProperty(time.strftime('%H::%M::%S'))

    def updateTime(self, dt):
        self.ux_CurrTime = time.strftime('%H::%M::%S')

    def updateSubjects(self, subjects):
        subjectList = self.ids['subject_listing']
        for subject in subjects:
            subjBtn = Button(text=subject,
                    size_hint=(1, None),
                    height=30,
                    id='Subject_' + subject
                    )
            subjBtn.bind(on_press=self.changeToSubjectScreen)
            subjectList.add_widget(subjBtn)

    def updateStations(self, stations):
        stationList = self.ids['station_listing']
        for station in stations:
            stBtn = StationButton(text=station,
                height=30,
                background_color=(0.56, 0.93, 0.56, 0.75),
                id=station,
                )
            stationList.add_widget(stBtn)
            stBtn.bind(on_press=self.changeToStationScreen)

    def enableScroll(self):
        subjectList = self.ids['subject_listing']
        subjectList.bind(minimum_height=subjectList.setter('height'))

    def changeToSubjectScreen(self, junk):
        screenMgr = self.ids['screen_manager']
        screenMgr.current = 'SubjectStatistics'

    def changeToStationScreen(self, junk):
        screenMgr = self.ids['screen_manager']
        screenMgr.current = 'StationStatistics'


class BServerApp(App):
    DefaultSubjects = ListProperty(
        ['Sub1', 'Sub2', 'Sub3', 'Sub4', 'Sub5', 'Sub6',
        'Sub7', 'Sub8', 'Sub9', 'Sub10', 'Sub11', 'Sub12',
        'Sub13', 'Sub14', 'Sub15', 'Sub16', 'Sub17', 'Sub18',
        'Sub19', 'Sub20', 'Sub21', 'Sub22', 'Sub23', 'Sub24',
        'Sub25', 'Sub26', 'Sub27', 'Sub28', 'Sub29', 'Sub30',
        'Sub31', 'Sub32', 'Sub33', 'Sub34', 'Sub35', 'Sub36'])
    DefaultStations = ListProperty(
        ['Station1', 'Station2', 'Station3', 'Station4',
        'Station5', 'Station6'])

    def createSubjectListing(self, Subjects, Box):
        for Subject in Subjects:
            Box.add_widget(Button(text=Subject,
                size_hint=(1, None),
                height=100))
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
        bserver_widget.updateSubjects(self.DefaultSubjects)
        # allow scroll
        bserver_widget.enableScroll()
        bserver_widget.updateStations(self.DefaultStations)
        return bserver_widget


if __name__ == "__main__":
    BServerApp().run()
    Config('graphics', 'fullscreen', 0)
    Config.write()