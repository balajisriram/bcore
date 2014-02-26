from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout  # lint:ok
from kivy.uix.scrollview import ScrollView  # lint:ok
from kivy.uix.button import Button
from kivy.uix.label import Label  # lint:ok
from kivy.uix.actionbar import ActionBar  # lint:ok
from kivy.uix.popup import Popup  # lint:ok
from kivy.uix.screenmanager import ScreenManager, Screen  # lint:ok

from kivy.properties import ListProperty, StringProperty, ObjectProperty
# from kivy.properties import StringProperty
from kivy.clock import Clock

from kivy.config import Config

#from BCore.Classes.ClientAndServer.BServer import BServer
#from BCore.Classes.ClientAndServer.BServerLocal import BServerLocal

import time


class HelpText(Label):
    def changeText(self, text):
        self.text = text


class StationButton(Button):
    pass


class BServerAppScreenManager(ScreenManager):
    cache = ObjectProperty()


class SubjectStatisticsScreen(Screen):
    def updateScreen(self, subjLbl, pressedObj):
        # get the data
        print self.ids
        textToShow = pressedObj.text
        subjLbl.text = textToShow

    def cleanAndReturn():
        pass


class StationStatisticsScreen(Screen):
    pass

    ux_LIGHTGREENCOLOR = [0.56, 0.93, 0.56, 0.75]
    ux_LIGHTREDCOLOR = [0.93, 0.56, 0.56, 0.75]


class BServerWidget(BoxLayout):
    ux_CurrTime = StringProperty(time.strftime('%H::%M::%S'))
    serverData = ObjectProperty()

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

    def changeToSubjectScreen(self, pressedButton):
        screenMgr = self.ids['screen_manager']
        screenMgr.current = 'SubjectStatistics'
        subjScreen = self.ids['subject_statistics']
        subjLbl = self.ids['subject_label']
        print self.serverData
        subjScreen.updateScreen(subjLbl, pressedButton)

    def changeToStationScreen(self, pressedButton):
        screenMgr = self.ids['screen_manager']
        screenMgr.current = 'StationStatistics'
        screenMgr.cache = pressedButton


class BServerApp(App):
    DefaultSubjects = ListProperty(
        ['Sub1', 'Sub2', 'Sub3', 'Sub4', 'Sub5', 'Sub6'])
    DefaultStations = ListProperty(
        ['Station1', 'Station2', 'Station3', 'Station4',
        'Station5', 'Station6'])
    serverData = ObjectProperty()
    cache = ObjectProperty()

    def build(self, *args):
        bserver_widget = BServerWidget()
        Clock.schedule_interval(bserver_widget.updateTime, 1)
        bserver_widget.updateSubjects(self.DefaultSubjects)
        # allow scroll
        bserver_widget.enableScroll()
        bserver_widget.updateStations(self.DefaultStations)
        bserver_widget.serverData = self.options['serverData']
        return bserver_widget


if __name__ == "__main__":
    Config.set('graphics', 'fullscreen', 'fake-fullscreen')
    Config.write()
    bserverWidget = BServerApp(serverData=1).run()
    Config.set('graphics', 'fullscreen', 0)
    Config.write()