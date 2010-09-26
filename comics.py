#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

import urllib
from datetime import datetime

class Comics:
    # when invoked (via signal delete_event), terminates the application.
    def close_application(self, widget, event, data=None):
        gtk.main_quit()
        return False

    # is invoked when the button is clicked.  It just prints a message.
    def button_clicked(self, widget, data=None):
        print "button %s clicked" % data

    def get_comic_image(self):
        filepath, status = urllib.urlretrieve(self.get_comic_url())
        return filepath

    def get_comic_url(self):
        today = datetime.now()
        return "http://picayune.uclick.com/comics/ch/%s/ch%s.gif" %(
                                                                    today.strftime("%Y"),
                                                                    today.strftime("%y%m%d")
                                                                    )

    def __init__(self):
        # create the main window, and attach delete_event signal to terminating
        # the application
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event", self.close_application)
        window.set_border_width(10)
        window.show()

        # a horizontal box to hold the buttons
        hbox = gtk.HBox()
        hbox.show()
        window.add(hbox)

        # no decoration
        window.set_decorated(False)
        window.set_keep_below(True)
        window.set_skip_taskbar_hint(True)

        image = gtk.Image()
        image.set_from_file(self.get_comic_image())
        image.show()
        hbox.pack_start(image)

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    Comics()
    main()
