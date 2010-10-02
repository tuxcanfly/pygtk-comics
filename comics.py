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

    def get_image_from_url(self, url):
        filepath, status = urllib.urlretrieve(url)
        return filepath

    def __init__(self):
        # create the main window, and attach delete_event signal to terminating
        # the application
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event", self.close_application)
        window.set_border_width(10)
        window.show()

        # no decoration
        #window.set_decorated(False)
        #window.set_keep_below(True)
        #window.set_skip_taskbar_hint(True)

        table = gtk.Table(3,6,False)
        window.add(table)

        # Create a new notebook, place the position of the tabs
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        table.attach(notebook, 0,6,0,1)
        notebook.show()
        self.show_tabs = True
        self.show_border = True

        for plugin_enabled in plugins_enabled:
            plugin = plugin_enabled()
            title = plugin.comic_name

            frame = gtk.Frame()
            frame.set_border_width(10)
            frame.set_size_request(100, 75)
            frame.show()

            image = gtk.Image()
            image_file = self.get_image_from_url(plugin.comic_url)
            image.set_from_file(image_file)
            frame.add(image)
            image.show()

            label = gtk.Label(title)
            notebook.append_page(frame, label)
        
        table.show()

class BaseComicsPlugin:
    def __init__(self, comic_name, comic_author=None):
        self.comic_name = comic_name
        self.comic_author = comic_author
        self.comic_url = self._get_image_url()

    def _get_image_url(self, date=datetime.today()):
        pass

class CalvinAndHobbesPlugin(BaseComicsPlugin):
    def __init__(self):
        BaseComicsPlugin.__init__(self, comic_name="Calvin and Hobbes", 
                                        comic_author="by Bill Waterson")


    def _get_image_url(self, date=datetime.today()):
        return "http://picayune.uclick.com/comics/ch/%s/ch%s.gif" %(
                                                                    date.strftime("%Y"),
                                                                    date.strftime("%y%m%d")
                                                                    )
plugins_enabled = [CalvinAndHobbesPlugin]

def main():

    gtk.main()
    return 0

if __name__ == "__main__":
    Comics()
    main()
