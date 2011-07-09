import pygtk
pygtk.require("2.0")
import gtk
from gtk import DrawingArea

import PIL
import tempfile


def scaleToFit(image, frame, enlarge=False):
    """Proportionally scales a rectangle to fit within another.

    Parameters:
    image -- A tuple of the original dimensions (width, height).
    frame -- A tuple of the target dimensions (width, height).
    enlarge -- Allow image to be scaled up?

    Returns:
    A tuple of the scaled dimensions. Aspect ratio is maintained.

    """
    image_width, image_height = image
    frame_width, frame_height = frame
    image_aspect = float(image_width) / image_height
    frame_aspect = float(frame_width) / frame_height
    # Determine maximum width/height (prevent up-scaling).
    if not enlarge:
        max_width = min(frame_width, image_width)
        max_height = min(frame_height, image_height)
    else:
        max_width = frame_width
        max_height = frame_height
    # Frame is wider than image.
    if frame_aspect > image_aspect:
        height = max_height
        width = int(height * image_aspect)
    # Frame is taller than image.
    else:
        width = max_width
        height = int(width / image_aspect)
    return (width, height)

def stretchToFit(image, frame, enlarge=False):
    """Resizes a rectangle to fit within another.

    Parameters:
    image -- A tuple of the original dimensions (width, height).
    frame -- A tuple of the target dimensions (width, height).
    enlarge -- Allow image to be scaled up?

    Returns:
    A tuple of the new dimensions.

    """
    image_width, image_height = image
    frame_width, frame_height = frame
    # Stop image from being blown up.
    if not enlarge:
        width = min(frame_width, image_width)
        height = min(frame_height, image_height)
    else:
        width = frame_width
        height = frame_height
    return (width, height)

def resizeToFit(image, frame, aspect=True, enlarge=False):
    """Resizes a rectangle to fit within another.

    Parameters:
    image -- A tuple of the original dimensions (width, height).
    frame -- A tuple of the target dimensions (width, height).
    aspect -- Maintain aspect ratio?
    enlarge -- Allow image to be scaled up?

    """
    if aspect:
        return scaleToFit(image, frame, enlarge)
    else:
        return stretchToFit(image, frame, enlarge)


class ResizableImage(DrawingArea):
    
    """GTK control to display a resizable image."""
    
    def __init__(self, aspect=True, enlarge=False,
            interp=gtk.gdk.INTERP_NEAREST, backcolor=None, max=(1600,1200)):
        """Construct a ResizableImage control.

        Parameters:
        aspect -- Maintain aspect ratio?
        enlarge -- Allow image to be scaled up?
        interp -- Method of interpolation to be used.
        backcolor -- Tuple (R, G, B) with values ranging from 0 to 1,
            or None for transparent.
        max -- Max dimensions for internal image (width, height).

        """
        DrawingArea.__init__(self)
        self.pixbuf = None
        # User options.
        self.aspect = aspect
        self.enlarge = enlarge
        self.interp = interp
        self.max = max
        self.backcolor = backcolor
        # Event handling.
        self.connect('expose_event', self.expose)

        self.tmpfile = None
    
    def invalidate(self):
        self.queue_draw()

    #
    # Functions to load an image.
    #

    def set_from_pixbuf(self, pixbuf):
        """Load image from gtk.gdk.Pixbuf."""
        width, height = pixbuf.get_width(), pixbuf.get_height()
        # Limit size of internal pixbuf to increase speed.
        if not self.max or (width < self.max[0] and height < self.max[1]):
            self.pixbuf = pixbuf
        else:
            width, height = resizeToFit((width, height), self.max)
            self.pixbuf = pixbuf.scale_simple(
                width, height,
                gtk.gdk.INTERP_BILINEAR)
        self.invalidate()

    def set_from_pixmap(self, pixmap, mask):
        """Load image from gtk.gdk.Pixmap."""
        image = gtk.image_new_from_pixmap(pixmap, mask)
        self.set_from_pixbuf(image.get_pixbuf())
    
    def set_from_image(self, gdk_image, mask):
        """Load image from gtk.Image."""
        self.set_from_pixbuf(gdk_image.get_pixbuf())

    def set_from_file(self, filename):
        """Load image from file."""
        self.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(filename))

    def set_from_stock(self, stock_id, size):
        """Load image from stock ID."""
        image = gtk.image_new_from_stock(stock_id, size)
        self.set_from_pixbuf(image.get_pixbuf())

    def set_from_icon_set(self, icon_set, size):
        """Load image from icon set."""
        image = gtk.image_new_from_icon_set(icon_set, size)
        self.set_from_pixbuf(image.get_pixbuf())

    def set_from_PIL(self, image):
        """Load from PIL Image."""
        if not self.tmpfile:
            handle, filename = tempfile.mkstemp(prefix="pano", suffix=".png")
            self.tmpfile = filename
        image.save(self.tmpfile, "PNG")
        self.set_from_file(self.tmpfile)

    #
    # Property modifiers.
    #
    
    def set_aspect(self, aspect):
        self.aspect = aspect
        self.invalidate()
    
    def set_enlarge(self, enlarge):
        self.enlarge = enlarge
        self.invalidate()

    #
    # Functions to draw resized image.
    #

    def expose(self, widget, event):
        # Load Cairo drawing context.
        self.context = self.window.cairo_create()
        # Set a clip region.
        self.context.rectangle(
            event.area.x, event.area.y,
            event.area.width, event.area.height)
        self.context.clip()
        # Render image.
        self.draw(self.context)
        return False

    def draw(self, context):
        # Get dimensions.
        rect = self.get_allocation()
        x, y = 0, 0
#        x, y = rect.x, rect.y
#        # Remove parent offset, if any.
#        parent = self.get_parent()
#        if parent:
#            offset = parent.get_allocation()
#            x -= offset.x
#            y -= offset.y
        # Fill background color.
        if self.backcolor:
            context.rectangle(x, y, rect.width, rect.height)
            context.set_source_rgb(*self.backcolor)
            context.fill_preserve()
        # Check if there is an image.
        if not self.pixbuf:
            return
        width, height = resizeToFit(
            (self.pixbuf.get_width(), self.pixbuf.get_height()),
            (rect.width, rect.height),
            self.aspect,
            self.enlarge)
        x += (rect.width - width) / 2
        y += (rect.height - height) / 2
        context.set_source_pixbuf(
            self.pixbuf.scale_simple(width, height, self.interp), x, y)
        context.paint()

