from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.actionbar import ActionBar

from kivy.properties import ListProperty


class BServerApp(App):
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
        BServerWidget = BoxLayout(orientation='vertical')

        BServerActionBar = ActionBar(pos_hint={'top': 1})
        BServerDataBox = BoxLayout(orientation='horizontal', spacing=10)
        BServerWidget.add_widget(BServerActionBar)
        BServerWidget.add_widget(BServerDataBox)

        SubjectBox = GridLayout(cols=1, spacing=1,
            size_hint=(0.3, 1))
        StationBox = GridLayout(cols=3, spacing=1,
            size_hint=(0.7, 1))

        BServerDataBox.add_widget(SubjectBox)
        BServerDataBox.add_widget(StationBox)

        SubjectLabel = Label(
            text='[b]Subjects[/b]',
            font_size=32,
            markup=True,
            size_hint=(1, 0.1))
        SubjectBox.add_widget(SubjectLabel)
        SubjectScrollView = ScrollView(do_scroll_x=False,
            do_scroll_y=True,
            size_hint=(1, 0.9),
            bar_color)
        SubjectList = GridLayout(cols=1, spacing=3, size_hint_y=None)
        SubjectList.bind(minimum_height=SubjectList.setter('height'))
        SubjectBox.add_widget(SubjectScrollView)
        SubjectScrollView.add_widget(SubjectList)

        return (BServerWidget, SubjectList, StationBox)


class BServerAppDefault(BServerApp):
    Subjects = ListProperty(['Sub1', 'Sub2', 'Sub3', 'Sub4', 'Sub5', 'Sub6',
        'Sub7', 'Sub8', 'Sub9', 'Sub10', 'Sub11', 'Sub12',
        'Sub13', 'Sub14', 'Sub15', 'Sub16', 'Sub17', 'Sub18',
        'Sub19', 'Sub20', 'Sub21', 'Sub22', 'Sub23', 'Sub24',
        'Sub25', 'Sub26', 'Sub27', 'Sub28', 'Sub29', 'Sub30',
        'Sub31', 'Sub32', 'Sub33', 'Sub34', 'Sub35', 'Sub36'])
    Stations = ListProperty(['Station1', 'Station2', 'Station3', 'Station4',
        'Station5', 'Station6'])

    def build(self):

        (BServerWidget, SubjectList, StationBox) = super(
            BServerAppDefault, self).build()

        # This part is specific to the build function
        SubjectList = self.createSubjectListing(self.Subjects, SubjectList)
        StationBox = self.createStationListing(self.Stations, StationBox)

        return BServerWidget

if __name__ == "__main__":
    BServerAppDefault().run()