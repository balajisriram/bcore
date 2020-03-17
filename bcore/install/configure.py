#!/usr/bin/env python
# encoding: utf-8

import npyscreen
import json

class GetConfigDetails(npyscreen.NPSApp):
    def main(self):
        # These lines create the form and populate it with widgets.
        # A fairly complex screen in only 8 or so lines of code - a line for each control.
        F  = npyscreen.Form(name = "Configure your BCore installation...",)
        t  = F.add(npyscreen.TitleText, name = "Please provide data_base_path:",)
        path = F.add(npyscreen.TitleFilenameCombo, name="PATH:")

        mode = F.add(npyscreen.TitleSelectOne, max_height=4, value = [1,], name="Pick One",
                values = ["Server","Client","Stand Alone"], scroll_exit=True)

        # This lets the user interact with the Form.
        F.edit()


if __name__ == "__main__":
    App = GetConfigDetails()
    out = App.run()
    print(out)