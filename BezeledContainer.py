import clutter
from clutter import cogl
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
class BezeledRectangle(clutter.Rectangle, clutter.Container):
    """
    Custom actor used to draw a rectangle that can have rounded corners
    """
    __gtype_name__ = 'BezeledRectangle'
 
    def __init__(self, border_width=4):
        """
        Creates a new rounded rectangle
        """
        #clutter.Rectangle(self).__init__()
        #clutter.Group(self).__init__()
        super(BezeledRectangle, self).__init__()

        self._color = [0.75,0.75,0.75]
        self._highlight_color = [0.9,0.9,0.9]
        self._lowlight_color = [0.5,0.5,0.5]
        self._border_width = border_width
        self.set_border_width( border_width )
        
        self._children = []        
        
    def paint_self(self):
        #self._border_width = self.get_border_width()
        (self._width, self._height) = self.get_size()
        if (self._width < self._border_width) or \
            (self._height < self._border_width):
            return
        self._arc = 10
        self._step = 10

        cogl.path_polygon(0.0, 0.0, self._width, 0.0, 0.0, self._height)
        cogl.path_close()
        cogl.path_fill()
        
        glBegin(GL_TRIANGLES)
        # Draw the highlight
        glColor(*self._highlight_color)
        glVertex2f(0.0, self._height)
        glVertex2f(0,0)
        glVertex2f(self._width,0.0)    
        # Draw the lowlight
        glColor(*self._lowlight_color)   
        glVertex2f(self._width, self._height)
        glVertex2f(0.0, self._height)
        glVertex2f(self._width,0.0)

        # draw the middle
        glColor(*self._color)
        glVertex2f(self._border_width, self._height - self._border_width)
        glVertex2f(self._border_width,self._border_width)
        glVertex2f(self._width - self._border_width,self._border_width) 
        glVertex2f(self._width - self._border_width, self._height - self._border_width)
        glVertex2f(self._border_width, self._height - self._border_width)
        glVertex2f(self._width - self._border_width,self._border_width) 
        glEnd()
        # draw the inside
#        cogl.set_source_color(self._color)
#        cogl.path_rectangle(self._border_width, self._border_width,
#                            self._width - self._border_width,
#                            self._height - self._border_width)
#        cogl.path_close()
#        cogl.path_fill() 
         
#        cogl.clip_pop()
 
    def pick_self(self, color):
        if self.should_pick_paint() == False:
            return
        cogl.path_round_rectangle(0, 0, self._width, self._height, self._arc, self._step)
        cogl.path_close()
        # Start the clip
        cogl.clip_push_from_path()
        # set color to border color
        cogl.set_source_color(color)
        # draw the rectangle for the border which is the same size and the
        # object
        cogl.path_round_rectangle(0, 0, self._width, self._height, self._arc, self._step)
        cogl.path_close()
        cogl.path_fill() 
        cogl.clip_pop()
         
    def do_add(self, *children):
        for child in children:
            if child in self._children:
                raise ValueError("Actor %s is already a children of %s" % (
                    child, self))

            self._children.append(child)
            child.set_parent(self)
            self.queue_relayout()

    def do_remove(self, *children):
        for child in children:
            if child in self._children:
                self._children.remove(child)
                child.unparent()
                self.queue_relayout()
            else:
                raise ValueError("Actor %s is not a child of %s" % (
                    child, self))


    def do_remove_all(self):
        """Removes all child actors from the ExampleBox"""
        self.do_remove(*self._children)

    def do_show_all(self):
        for child in self._children:
            child.show()

    def do_hide_all(self):
        for child in self._children:
            child.hide()

    def do_foreach(self, func, data):
        for child in self._children:
            func(child, data)

    def do_paint(self):
        cogl.push_matrix()
        self.paint_self()
        for child in self._children:
            if child.props.mapped:
                child.paint()

        cogl.pop_matrix()

    def do_pick(self, color):
        if not self.should_pick_paint():
            return
        self.pick_self(color)
        for child in self._children:
            if child.props.mapped:
                try:
                    child.do_pick(color)
                except TypeError:
                    child.do_pick(child, color)

    def do_allocate(self, box, flags):
        current_x = current_y = maximum_y = self._border_width
        our_width = box.x2 - box.x1
        our_height = box.y2 - box.y1
        for child in self._children:
            # Discover what size the child wants
            child_width, child_height = child.get_preferred_size()[2:]
            
            if current_x + child_width + self._border_width > our_width:
                current_x = self._border_width
                current_y = maximum_y
                

            # Position the child just after the previous child, horizontally
            child_box = clutter.ActorBox()
            child_box.x1 = current_x
            child_box.x2 = current_x + child_width
            current_x = child_box.x2

            # Position the child at the top of the container
            child_box.y1 = current_y
            child_box.y2 = child_box.y1 + child_height
            maximum_y = max( child_box.y2, maximum_y )
            # Tell the child what position and size it may actually have
            child.allocate(child_box, flags)

        clutter.Actor.do_allocate(self, box, flags)

    def get_preferred_height(self):
        min_height = natural_height = 0
        # For this container, the preferred height is the maximum height
        # of the children. The preferred height is independent of the given width.

        # Calculate the preferred height for this container,
        # based on the preferred height requested by the children
        for child in self._children:
            if not child.props.visible:
                child_min_height, child_natural_height = child.get_preferred_height(-1)
                min_height = max(min_height, child_min_height)
                natural_height = max(natural_height, child_natural_height)

        return min_height, natural_height

    def get_preferred_width(self):
        min_width = natural_width = 0

        # For this container, the preferred width is the sum of the widths
        # of the children. The preferred width depends on the height provided
        # by for_height.

        # Calculate the preferred width for this container,
        # based on the preferred width requested by the children
        for child in self._children:
            if child.props.visible:
                child_min_width, child_natural_width = child.get_preferred_width(for_height)

                min_width += child_min_width
                natural_width += child_natural_width

        return min_width, natural_width
 
