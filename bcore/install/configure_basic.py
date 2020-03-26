from kivy.app import App

from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.spinner import Spinner

configuration = dict()

Builder.load_string('''
<ConfigurationWidget>:
    orientation: 'vertical'
    BoxLayout:
    	size_hint: (1,0.1)
    	orientation: 'horizontal'
    	Label:
    		text: 'How will you use this installation?'
    	Spinner:
    		id: mode_spinner
    		text: 'Server'
    		values: 'Server', 'Client', 'Standalone'
    		on_text: root.set_mode()
    BoxLayout:
    	orientation: 'horizontal'
    	size_hint: (1,0.8)
    	Label:
    		text: 'Choose where database will be stored:'
    	FileChooserListView:
    		dirselect: True
    BoxLayout:
    	orientation: 'horizontal'
    	size_hint: (1,0.1)
    	Button:
    		size_hint : (0.9,1)
    		text: 'Save configuration'
    		background_color: (0.2,0.9,0.2,1)
    	Button:
    		size_hint: (0.1,1)
    		text: 'Cancel'
    		background_color: (0.9,0.2,0.2,1)

''')


#     		on_value: app.configuration['mode']=self.value	

class ConfigurationWidget(BoxLayout):
	def set_mode(self,*args):
		spin = self.ids['mode_spinner']
		configuration['mode'] = spin.text
		print(configuration['mode'])
		# print(dir(spin))

class BasicConfigurationApp(App):
    def build(self):
        return ConfigurationWidget()

if __name__ == "__main__":
    BasicConfigurationApp().run()
    print(configuration)