from tkinter import *

class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    
    Slightly modified from:
    http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        self.config(background='white')
        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bg='white', bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)
        
#==============================================================================
#         # Mouse wheel binding - Windows OS
#         def _on_mousewheel(event):
#             canvas.yview_scroll(round(-1*(event.delta/120)), "units")
#         canvas.bind_all("<MouseWheel>", _on_mousewheel)
#==============================================================================
        
        # Mouse wheel binding - Linux OS
        def _on_mousewheel(event):
            wheelcount = 0
            if event.num == 5 or event.delta == 120:
                wheelcount = -1
            if event.num == 4 or event.delta == -120:
                wheelcount = 1
            canvas.yview_scroll(wheelcount, "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
