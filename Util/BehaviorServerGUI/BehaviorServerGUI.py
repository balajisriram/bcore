import time

#lint:disable
from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.actionbar import ActionBar
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch

from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.config import Config
from datetimepicker import DatePicker, TimePicker

from BCore.Classes.Subject import Subject, Mouse, Rat, Virtual, Human
from BCore.Classes.Subject import DefaultMouse, DefaultRat, DefaultVirtual
from BCore.Classes.Subject import DefaultHuman
#lint:enable


class HelpText(Label):
    def changeText(self, text):
        self.text = text


class StationButton(Button):
    ux_LIGHTGREENCOLOR = [0.56, 0.93, 0.56, 0.75]
    ux_LIGHTREDCOLOR = [0.93, 0.56, 0.56, 0.75]


class BServerAppScreenManager(ScreenManager):
    cache = ObjectProperty()

    def deCache(self):
        self.cache = []


class SubjectStatisticsScreen(Screen):
    def updateScreen(self, subjLbl, pressedObj):
        # get the data
        textToShow = pressedObj.text
        subjLbl.text = textToShow

    def cleanAndReturn():
        pass


class StationStatisticsScreen(Screen):
    pass


class SubjectIDInput(TextInput):

    def validateSubIDInput(self, call):
        for c in self.text:
            if c in (' ', '-'):
                self.text = 'Only alphanumerics and underscores allowed'


class AddSubjectScreen(Screen):

    def addSubjectToServer(self, value):
        print 'here'

    def presentSpeciesSpecificWidgets(self, layout, present, details, example):
        # now add a vertical box layout and add the choices
        OtherFields = BoxLayout(spacing=3, orientation='vertical')
        # subjectID
        if present['subjectID']:
            subjectIDLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            subjectIDLayout.add_widget(Label(text='Subject ID'))
            subIDInput = SubjectIDInput(text='Press Enter when done',
                multiline=False)
            subIDInput.bind(on_text_validate=subIDInput.validateSubIDInput)
            subjectIDLayout.add_widget(subIDInput)
            OtherFields.add_widget(subjectIDLayout)

        # firstName
        if present['firstName']:
            FirstNameLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            FirstNameLayout.add_widget(Label(text='First Name'))
            firstNameInput = TextInput(text='First',
                multiline=False)
            FirstNameLayout.add_widget(firstNameInput)
            OtherFields.add_widget(FirstNameLayout)

        # lastName
        if present['lastName']:
            LastNameLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            LastNameLayout.add_widget(Label(text='Last Name'))
            lastNameInput = TextInput(text='Last',
                multiline=False)
            LastNameLayout.add_widget(lastNameInput)
            OtherFields.add_widget(LastNameLayout)

        # gender
        if present['gender']:
            genderLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            genderLayout.add_widget(Label(text='Sex'))
            genderInput = Spinner(text=details['allowedGenders'][0],
                values=details['allowedGenders'],
                size=(150, 40))
            genderLayout.add_widget(genderInput)
            OtherFields.add_widget(genderLayout)

        # dob
        if present['dob']:
            dobLayout = BoxLayout(orientation='horizontal', height=88,
                size_hint_y=None)
            dobLayout.add_widget(Label(text='Date of Birth'))
            dobInput = DatePicker()
            dobLayout.add_widget(dobInput)
            OtherFields.add_widget(dobLayout)

        # strains
        if present['strains']:
            strainLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            strainLayout.add_widget(Label(text='Strain'))
            strainInput = Spinner(text=details['allowedStrains'][0],
                values=details['allowedStrains'],
                size=(150, 40))
            strainLayout.add_widget(strainInput)
            OtherFields.add_widget(strainLayout)

        # geneBkgd
        if present['geneBkgd']:
            geneBkgdLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            geneBkgdLayout.add_widget(Label(text='Genetic Background'))
            geneBkgdInput = Spinner(text=details['allowedGeneBkgd'][0],
                values=details['allowedGeneBkgd'],
                size=(150, 40))
            geneBkgdLayout.add_widget(geneBkgdInput)
            OtherFields.add_widget(geneBkgdLayout)
        # anonymize
        if present['anonymize']:
            anonLayout = BoxLayout(orientation='horizontal', height=40,
                size_hint_y=None)
            anonLayout.add_widget(Label(text='Anonymize'))
            anonInput = Switch(active=False)
            anonLayout.add_widget(anonInput)
            OtherFields.add_widget(anonLayout)
        print '[INFO]\t added species specific widgets'
        largeBlankSpace = BoxLayout(orientation='horizontal', height=80,
                size_hint_y=None)
        OtherFields.add_widget(largeBlankSpace)
        print '[INFO]\t added blank space'
        addSubjectLayout = BoxLayout(orientation='horizontal', height=80,
                size_hint_y=None)
        addSubjectButton = Button(text='Add Subject')
        addSubjectButton.bind(on_press=self.addSubjectToServer)
        addSubjectLayout.add_widget(addSubjectButton)
        OtherFields.add_widget(addSubjectLayout)
        print '[INFO]\t added add subject button'
        layout.add_widget(OtherFields)

    def updateSpeciesSpecificChoice(self, species, layout):
        # if there are any old widgets to the layout, clear it
        layout.clear_widgets()
        present = {
            'subjectID': False,
            'firstName': False,
            'lastName': False,
            'gender': False,
            'dob': False,
            'strains': False,
            'geneBkgd': False,
            'anonymize': False
            }
        details = {}
        if species == 'Mouse':
            example = DefaultMouse()
            details['allowedGenders'] = example.allowedGenders()
            details['allowedStrains'] = example.allowedStrains()
            details['allowedGeneBkgd'] = example.allowedGeneBkgd()
            present['subjectID'] = True
            present['gender'] = True
            present['dob'] = True
            present['strains'] = True
            present['geneBkgd'] = True

            self.presentSpeciesSpecificWidgets(
                layout, present, details, example)
        elif species == 'Rat':
            example = DefaultRat()
            details['allowedGenders'] = example.allowedGenders()
            details['allowedStrains'] = example.allowedStrains()
            details['allowedGeneBkgd'] = example.allowedGeneBkgd()
            present['subjectID'] = True
            present['gender'] = True
            present['dob'] = True
            present['strains'] = True
            present['geneBkgd'] = True

            self.presentSpeciesSpecificWidgets(
                layout, present, details, example)
        elif species == 'Virtual':
            example = DefaultVirtual()
            present['subjectID'] = True

            self.presentSpeciesSpecificWidgets(
                layout, present, details, example)
        elif species == 'Human':
            example = DefaultHuman()
            details['allowedGenders'] = example.allowedGenders()
            present['firstName'] = True
            present['lastName'] = True
            present['gender'] = True
            present['dob'] = True
            present['anonymize'] = True

            self.presentSpeciesSpecificWidgets(
                layout, present, details, example)


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
        subjScreen.updateScreen(subjLbl, pressedButton)

    def changeToStationScreen(self, pressedButton):
        screenMgr = self.ids['screen_manager']
        screenMgr.current = 'StationStatistics'
        screenMgr.cache = pressedButton


class BServerApp(App):
    DefaultSubjects = ListProperty()
    DefaultStations = ListProperty()
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