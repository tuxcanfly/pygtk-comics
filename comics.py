#!/usr/bin/env python

# Copyright 2010 Jakh Daven<tuxcanfly@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import pygtk
pygtk.require('2.0')
import gtk

import os
import Image
import urllib
import feedparser
import simplejson
from datetime import datetime

from resizableimage import ResizableImage

COMICS_PATH = os.environ['HOME'] + '/.local/share/comics'
X_PADDING = 50
Y_PADDING = 90

class Comics:
    # when invoked (via signal delete_event), terminates the application.
    def close_application(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def get_image_from_url(self, url, location):
        if os.path.isfile(location):
            filepath = location
        else:
            filepath, status = urllib.urlretrieve(url, location)
        return filepath

    def __init__(self):
        # create the main window, and attach delete_event signal to terminating
        # the application
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.close_application)
        self.window.set_border_width(10)
        self.window.show()
        theme = gtk.icon_theme_get_default()
        icon = theme.load_icon("face-smile", 36, gtk.ICON_LOOKUP_FORCE_SVG) 
        self.window.set_icon(icon)

        self.page_data = {}

        # ensure cache dir
        if not os.path.isdir(COMICS_PATH):
            os.makedirs(COMICS_PATH)

        # no decoration
        #self.window.set_decorated(False)
        #self.window.set_keep_below(True)
        #self.window.set_skip_taskbar_hint(True)

        table = gtk.Table(3,6,False)
        self.window.add(table)

        # Create a new notebook, place the position of the tabs
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        table.attach(notebook, 0,6,0,1)
        notebook.show()
        self.show_tabs = True
        self.show_border = False

        notebook.connect("switch-page", self._page_switched)

        for page_num, plugin_class in enumerate(BaseComicsPlugin.plugins):
            #assuming all plugins are active
            plugin = plugin_class()
            title = plugin.comic_name

            frame = gtk.Frame()
            frame.set_border_width(10)
            # pickle plugin data for lazy load
            self.page_data[page_num] = plugin
            frame.show()

            label = gtk.Label(title)
            notebook.append_page(frame, label)
        
        table.show()

    def _page_switched(self, notebook, page, page_num):
        try:
            plugin = self.page_data[page_num]
        except:
            # tab not intialized by us, so no comic here
            return
        cur_frame = notebook.get_nth_page(page_num)
        
        try:
            image = cur_frame.get_children()[0]
        except IndexError:
            image = ResizableImage()
        location = "%s/%s-%s" %(COMICS_PATH, plugin.comic_name, datetime.today().strftime("%d-%m-%Y"))
        image_file = self.get_image_from_url(plugin.get_comic_url(), location)
        image.set_from_file(image_file)
        cur_frame.add(image)
        image.show()

        image_data = Image.open(image_file)
        x_size, y_size = image_data.size
        self.window.resize(x_size + X_PADDING, y_size + Y_PADDING)

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
    comic_author = "Bill Watterson"

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

class DilbertPlugin(BaseComicsPlugin):
    comic_name = "Dilbert"
    comic_author = "Scott Adams"

    def get_comic_url(self, data=datetime.today()):
        dilbert_url = "http://pipes.yahoo.com/pipes/pipe.run?_id=44e23d1c1507ad6741685fe23c81cb51&_render=rss"
        feed = feedparser.parse(dilbert_url)
        return feed['entries'][0]['summary']

class SMBCPlugin(BaseComicsPlugin):
    comic_name = "Saturday Morning Breakfast Cereal"
    comic_author = "Zach Weinersmith"
    
    def get_comic_url(self, date=datetime.today()):
        smbc_url = "https://www.smbc-comics.com/comic/rss"
        feed = feedparser.parse(smbc_url)
        return feed['entries'][0]['description']

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    Comics()
    main()
