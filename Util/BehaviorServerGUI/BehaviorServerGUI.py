from kivy.app import App
from kivy.core.window import Window

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.listview import ListView
from kivy.uix.button import Button

from kivy.properties import ListProperty

import time
    
class BServerApp(App):
    def createSubjectListing(self, Subjects, Box):
        Box.add_widget(ListView(item_strings=Subjects))
        return Box
        
    def createStationListing(self, Stations, Box):
        for Station in Stations:
            Box.add_widget(Button(text=Station))
        return Box
                
class BServerAppDefault(BServerApp):
    Subjects = ListProperty(['Sub1','Sub2','Sub3','Sub4','Sub5'])
    Stations = ListProperty(['Station1','Station2','Station3','Station4','Station5','Station6'])
    def build(self):
        BServerWidget = BoxLayout(orientation='horizontal', spacing=10)
        
        SubjectBox = BoxLayout(orientation='vertical', spacing=1, size_hint=(0.3,1)); 
        StationBox = GridLayout(cols=3, spacing=1, size_hint=(0.7,1)); 
        
        SubjectBox = self.createSubjectListing(self.Subjects, SubjectBox) 
        StationBox = self.createStationListing(self.Stations, StationBox)
        
        BServerWidget.add_widget(SubjectBox)
        BServerWidget.add_widget(StationBox)
        
        return BServerWidget
        
if __name__ == "__main__":
    BServerAppDefault().run()