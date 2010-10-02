#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

import Image
import urllib
import simplejson
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
        self.show_border = False

        for plugin_class in BaseComicsPlugin.plugins:
            plugin = plugin_class()
            title = plugin.comic_name

            frame = gtk.Frame()
            frame.set_border_width(10)

            image = gtk.Image()
            image_file = self.get_image_from_url(plugin.get_comic_url())
            image.set_from_file(image_file)
            frame.add(image)
            image.show()

            image_data = Image.open(image_file)
            x_size, y_size = image_data.size
            frame.set_size_request(x_size, y_size)
            frame.show()

            label = gtk.Label(title)
            notebook.append_page(frame, label)
        
        table.show()

class RegisteredPlugin(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)

class BaseComicsPlugin(object):
    __metaclass__ = RegisteredPlugin

class CalvinAndHobbesPlugin(BaseComicsPlugin):
    comic_name = "Calvin and Hobbes"
    comic_author = "Bill Waterson"

    def get_comic_url(self, date=datetime.today()):
        return "http://picayune.uclick.com/comics/ch/%s/ch%s.gif" %(
                                                                    date.strftime("%Y"),
                                                                    date.strftime("%y%m%d")
                                                                    )

class XKCDPlugin(BaseComicsPlugin):
    comic_name = "XKCD"
    comic_author = "Randall Munroe"

    def get_comic_url(self, date=datetime.today()):
        xkcd_url = "http://xkcd.com/info.0.json"
        xkcd_data = urllib.urlopen(xkcd_url)
        json = simplejson.loads(xkcd_data.read())
        return json["img"]

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    Comics()
    main()
