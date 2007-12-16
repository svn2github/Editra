###############################################################################
# Name: PlateButtonDemo.py                                                    #
# Purpose: PlateButton Test and Demo File                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Test file for testing the PlateButton control

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import webbrowser
import wx

sys.path.insert(0, os.path.abspath('../../'))
import src.eclib.platebtn as platebtn

#-----------------------------------------------------------------------------#

class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent)

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_MENU, self.OnMenu)

    def __DoLayout(self):
        """Layout the panel"""
        # Make three different panels of buttons with different backgrounds
        # to test transparency and appearance of buttons under different use
        # cases
        p1 = wx.Panel(self)
        p2 = GradientPanel(self)
        p3 = wx.Panel(self)
        p3.SetBackgroundColour(wx.BLUE)

        self.__LayoutPanel(p1, "Default Background:")
        self.__LayoutPanel(p2, "Gradient Background:", exstyle=True)
        self.__LayoutPanel(p3, "Solid Background:")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([(p1, 0, wx.EXPAND), (p2, 0, wx.EXPAND), 
                       (p3, 0, wx.EXPAND)])
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(sizer, 1, wx.EXPAND)
        self.SetSizer(hsizer)
        self.SetAutoLayout(True)

    def __LayoutPanel(self, panel, label, exstyle=False):
        """Puts a set of controls in the panel
        @param panel: panel to layout
        @param label: panels title
        @param exstyle: Set the PB_STYLE_NOBG or not

        """
        # Bitmaps (32x32) and (16x16)
        devil = getBitmap('devil') # 32x32
        monkey = getBitmap('monkey') # 32x32
        address = getBitmap('address') # 16x16
        folder = getBitmap('home')
        bookmark = getBitmap('bookmark') # 16x16

        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer1.Add((15, 15))
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2.Add((15, 15))
        hsizer3 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer3.Add((15, 15))

        # Button Styles
        default = platebtn.PB_STYLE_DEFAULT
        square  = platebtn.PB_STYLE_SQUARE
        sqgrad  = platebtn.PB_STYLE_SQUARE | platebtn.PB_STYLE_GRADIENT
        gradient = platebtn.PB_STYLE_GRADIENT

        # Create a number of different PlateButtons
        # Each button is created in the below loop by using the data set in this
        # lists tuple
        #        (bmp,   label,                Style,   Variant, Menu, Color, Enable)
        btype = [(None,  "Normal PlateButton", default, None,    None, None,  True),
                 (devil, "Normal w/Bitmap",    default, None,    None, None,  True),
                 (devil, "Disabled",           default, None,    None, None,  False),
                 (None,  "Normal w/Menu",      default, None,    True, None,  True),
                 (folder, "Home Folder",       default, None,    True, None,  True),
                 # Row 2
                 (None,  "Square PlateButton", square,  None,    None, None,  True),
                 (address, "Square/Bitmap",     square,  None,    None, None,  True),
                 (monkey, "Square/Gradient",   sqgrad,  None,    None, None,   True),
                 (address, "Square/Small",       square,  wx.WINDOW_VARIANT_SMALL, True, None, True),
                 (address, "Small Bitmap",      default, wx.WINDOW_VARIANT_SMALL, None, wx.Colour(33, 33, 33), True),
                 # Row 3
                 (devil, "Custom Color",       default, None,    None, wx.RED, True),
                 (monkey, "Gradient Highlight", gradient, None,  None, None,   True),
                 (monkey, "Custom Gradient",   gradient, None,   None, wx.Color(245, 55, 245), True),
                 (devil,  "",                  default, None,    None, None,   True),
                 (bookmark,  "",               default, None,    True, None,   True),
                 (monkey,  "",                 square,  None,    None, None,   True),
                 ]

        # Make and layout three rows of buttons in the panel
        for btn in btype:
            if exstyle:
                # With this style flag set the button can appear transparent on
                # on top of a background that is not solid in color, such as the
                # gradient panel in this demo.
                #
                # Note: This flag only has affect on wxMSW and should only be
                #       set when the background is not a solid color. On wxMac
                #       it is a no-op as this type of transparency is achieved
                #       without any help needed. On wxGtk it doesn't hurt to
                #       set but also unfortunatly doesn't help at all.
                bstyle = btn[2] | platebtn.PB_STYLE_NOBG
            else:
                bstyle = btn[2]

            if btype.index(btn) < 5:
                tsizer = hsizer1
            elif btype.index(btn) < 10:
                tsizer = hsizer2
            else:
                tsizer = hsizer3

            tbtn = platebtn.PlateButton(panel, wx.ID_ANY, btn[1], btn[0], style=bstyle)

            # Set a custom window size variant?
            if btn[3] is not None:
                tbtn.SetWindowVariant(btn[3])

            # Make a menu for the button?
            if btn[4] is not None:
                menu = wx.Menu()
                if btn[0] is not None and btn[0] == folder:
                    for fname in os.listdir(wx.GetHomeDir()):
                        if not fname.startswith('.'):
                            menu.Append(wx.NewId(), fname)
                elif btn[0] is not None and btn[0] == bookmark:
                    for url in ['http://wxpython.org', 'http://slashdot.org',
                                'http://editra.org', 'http://xkcd.com']:
                        menu.Append(wx.NewId(), url, "Open %s in your browser" % url)
                else:
                    menu.Append(wx.NewId(), "Menu Item 1")
                    menu.Append(wx.NewId(), "Menu Item 2")
                    menu.Append(wx.NewId(), "Menu Item 3")
                tbtn.SetMenu(menu)

            # Set a custom colour?
            if btn[5] is not None:
                tbtn.SetPressColor(btn[5])

            # Enable/Disable button state
            tbtn.Enable(btn[6])

            tsizer.AddMany([(tbtn, 0, wx.ALIGN_CENTER), ((10, 10))])

        txt_sz = wx.BoxSizer(wx.HORIZONTAL)
        txt_sz.AddMany([((5, 5)), (wx.StaticText(panel, label=label), 0, wx.ALIGN_LEFT)])
        vsizer.AddMany([((10, 10)),
                        (txt_sz, 0, wx.ALIGN_LEFT),
                        ((10, 10)), (hsizer1, 0, wx.EXPAND), ((10, 10)), 
                        (hsizer2, 0, wx.EXPAND), ((10, 10)), 
                        (hsizer3, 0, wx.EXPAND), ((10, 10))])
        panel.SetSizer(vsizer)

    def OnButton(self, evt):
        self.log.write("BUTTON CLICKED: Id: %d, Label: %s" % \
                       (evt.GetId(), evt.GetEventObject().LabelText))

    def OnMenu(self, evt):
        """Events from button menus"""
        self.log.write("MENU SELECTED: %d" % evt.GetId())
        e_obj = evt.GetEventObject()
        mitem = e_obj.FindItemById(evt.GetId())
        if mitem != wx.NOT_FOUND:
            label = mitem.GetLabel()
            if label.startswith('http://'):
                webbrowser.open(label, True)

#-----------------------------------------------------------------------------#

class GradientPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        col1 = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DSHADOW)
        col2 = platebtn.AdjustColour(col1, -90)
        col1 = platebtn.AdjustColour(col1, 90)
        rect = self.GetClientRect()
        grad = gc.CreateLinearGradientBrush(0, 1, 0, rect.height - 1, col2, col1)

        pen_col = tuple([min(190, x) for x in platebtn.AdjustColour(col1, -60)])
        gc.SetPen(gc.CreatePen(wx.Pen(pen_col, 1)))
        gc.SetBrush(grad)
        gc.DrawRectangle(0, 1, rect.width - 0.5, rect.height - 0.5)

        evt.Skip()
#----------------------------------------------------------------------

def runTest(frame, nb, log):
    win = TestPanel(nb, log)
    return win

class TestLog:
    def __init__(self):
        pass

    def write(self, msg):
        print msg

#----------------------------------------------------------------------

overview = """
"""

#----------------------------------------------------------------------
# Icon Data
# All icons from the Tango Icon Set
from wx import ImageFromStream, BitmapFromImage, EmptyIcon
import cStringIO, zlib

def BookData():
    return zlib.decompress(
'x\xda\x01\x90\x02o\xfd\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\
\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\
\x08\x08\x08|\x08d\x88\x00\x00\x02GIDAT8\x8d\x95\x92\xc9kSQ\x14\x87\xbf;\xbc\
\x97\x974\xdaL\x18\r5\x0eQ\x02\xad\xdd\x14Z\xb0\xfe\x03N\xa8 \x8a\x0b\xc1\
\x8d\xb8\x17\x04\x114\x8b\xba\x10\x17\x8a\xcb\x82[]\x14\xbatB\xb4Z\xb0\xb6](\
\x05\x15\x9a\xb4EJ\x07\x9a\x0e\x16b\xc9k\xc6\xeb\xa2\x1a\x92V*\xfe6\xf7\x9c\
\xcb9\xdf\xef\x9e\xcb\x11\xfcV\xd7\xf1\x9b\xd7A<\xc0\x18\xf3\xe7\xce \x0c\
\x80\x90"{\xff\xe2|\xa2\xfbd.\xa9\x8c\xec2\x94\x974\xd5a\xa2\x1dK\x1a\xa0\
\xb7\xb7\xb7?\x9b\xcd\x9e\x9f\x98\x9c"\xb3\x14\x13wn]\xde \x08\xc0\xc0\xdd{O\
b/\xbe\x96\xdch[\x8c\xbd\xfb\x8f"\xed}\xac\xac\xbc\xfd\x10]\xfevU\x01tvv\xf6\
\xa5R)v\xf8\xfd\x0c\x0c\x7f\'\x18\x8d\xf09=\xc7\xe4\xcc2n\xa1\xc4\xc4\xf847\
\xae\x1d\xa1\xbd\xed\x10v\xf3Y,g?R{\xe3\xb24:\xaf\xa9S.\x97\xa3\\\xca\xb3\
\xb2\xbaJvq\x15\x00GW)\x97\xf2\xe4~\x96)W\xcb\xe8\x8a\x8bP\x92b~\x06\x8f\x94\
9Y\x0f\xa8T*TJ\xeb\x14\x0b.\x05w\x8d\xa2\xbbFi\xdd\xa5\\t\xf92^`fNP\xc9\x0f`\
\xf2\xaf\x99\x9d\x1e\xa6j\n\x9f\x1a\x00\x00B\xd9hmc\xd9\x1e\x94\xe5Ai\x0b!-\
\xf6\xc4\xe2\x84v\x9f\xc0\xad\xb6#\xac\x18\xa3c\x16\x96\xfbc\xac\x01 \x84@[^\
,\xc7\x87\xed\xf8\xf1x\x9b\xb0\x1c/\xda\xf227;G:3\x85\x111\xb0;\x98_lB\x1c\
\x18\\\xd7\x9b_ \xa5BJ\x85\xd2\x16\x00JYH\xa5iii!\x99L\x82\x10\x08\xa11F\x00\
\xd0\x00\xb0m\xbb\x16\xef\n\xf9\xa9Vk+\x81\xe3U\x9b\xbd6\x0c\xeb\x13\x9f\xcf\
\x07\x801\xf0\xf1\xcd\x08#\x03\xa3\xb5\xbdj\xf25#\x84\xd8\x1e\xe0\xf1x\x00x\
\xffj\x88xl\'\x07\xe3\x01\xde\xbd\x1c\xc2\x18\xc3\xc2\xc2\x02\xe9tz\x0b\xa0a\
\x04\xc7q\x00\xb8r\xe1\x18\x97\xceu#\xa5\xa4\xff\xd9\x08\x8f\x9f\x0e\xd2\xda\
\xdaJ"\x91\xd8\x1e\x10\x89Dxx\xfb4J)2\x99\x0cB\x08\xda\x0f\x07y\x94:C0\x18\
\x04\xd82F\x03 \x10\x08\x10\x08\x04\x10B\xd4\n\xeb\xcf\xbf\xfdA\x03 \x14\nm)\
\xf8\x974@8\x1c~\xde\xd3\xd3s\xea\x7f\x1a\xc3\xe1p\x1f\xc0/Ux\xc0\xdfC\x88Z\
\xb7\x00\x00\x00\x00IEND\xaeB`\x82\xfb\xc1\x19T' )

def AddressData():
    return zlib.decompress(
'x\xda\x01\xb4\x02K\xfd\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\
\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\
\x08\x08\x08|\x08d\x88\x00\x00\x02kIDAT8\x8d}\x92\xcbK\x94Q\x18\xc6\x7f\xe7|\
\xdf\x99\x8b3\xcex\x19\xc7KS\xa4\x96d\x12\x15X\xd1\x1f\xd0\xa2MB\x9b \xa4e\
\xe1_\x10\xb8Pp!D\xed\x82\xa0E\xbbp_\xb9m\x17\xb4\x08lai:\x06\xa3\x99\x97\
\xb9\xa0s\xff\x9c\xefrZ|\xa9\x99\xd6\x03gs\xe0\xfd\x9d\xe7y\xce+\xb4~\xa8\
\x9e\xbd\xea\x7f\x1e\x0f7\x1e\x95\xea\x01V\xb6\xda)\xd7\x82h\x04\xff\xd1\xd4\
\xcc\xf4\xe8$\x80\x98~\xf9\xf4\xc5\xed+\xdbc\x17/\xdc\x043E\xae\xb0D:7\xc0\
\xe6n3\x1a\x89\x94>h\x1fW\xb5\x1a\x946gyp}\x9cx\xc7\xc8cSI=6\xd0?\x84\x19\
\xb9\x05"D2a\x90/\xce\xb1\x9a\xeb#\xb8ZA\xd5\xf7\xf0\x94A\xa5+A=\x11\xa7\xb3\
-B\t\x88w\x8cP\xcc\xbdybZ\xb6\xc2\x03\xf0,\x90\x12\xd7\xde\xc6\xaeKb\xabY\n=\
ghD\x9b0\xad=\xe2\x99M\\e@[\x84\xa6`\xe3 \x8b\xb9\xb2\xd9F\xae\xdcF\x07\xefq\
]\x81\xe3f)\xa6c\xec${0\x1a6\xc9\xf9\x15\xb4\x10\xec\x9cK\x11\xfb\x91\x85\
\xdeN\xc2\x01\xfb\x10`\xbb\x06e=\x8cU\xdc"\x9f]"\x91\xbcF)\x93ao0Jb!C)\x95$\
\xbaU\xc0\t\x05P5\x0b\x80\x8f\xdf,l\xb5\xcc\xd7\xb9&$@@\x85\xb1\xbcn\xb6\x8a\
\xe7\xa9\xb9\xbdx\xb6D\x0b\x81t\\\xb4a\x80\x10\x04\xcb5\x9cp\xe0\xd8wH\x00!\
\xfc\x8e\xb50\xfc\xabH\x08U\xb5\xb0Z\x9b\xfd\xd7\x03\x8a\xd8\xda6\xa5\xd3\
\x9d\x00xD\x0f#\x1c\xe5\xf9 \xaf\xb7\x8bX\xfa\'\xc5\xb3\xdd8\xe1 \x88\xa3;\
\x11\xca(\xee\xce\xc0\xe5\xc5\x9a\x0f\xd0h\xd0\x90l\x8f\xfbN:Z(\xed9\xc4\xd6\
\xb3\xa8j\x1d7\xa0\xc8\x0f\xf5\x9d\xb8Q\xbe\x03\rJ\x99\xb4\xb4D\xb1l\x87\xce\
\xd6\x08\xb1p\x10\x06N\x1d\xf8\x8a\x1f\xf1\xf8\x17\xa0R\xad\xf3n\xf6\x03\xa6\
\xd4x\xda?\x8e\xa3\x11R\x10P\x06B\x08\x04\xe0\xba\x1e\x99\xf5\xbc\xd7U+\xcb\
\xef\x8b\x8b\x00\xf7L\x80/\xf3+\xdc\x18\x8c\x1c\xac\xedI\x92RR\x13-,\x17\x1a\
r\xad\xf7\x12\xc3\xbf\xcd\x98\x00\xbb\x95*}\xc9fR\xa9\x9ec\x83\xe2\x8f\x02\
\x17\xd2\x1b\'v0\xf5)\x9d\x9fp\xea5o#\xdf\x90\xa1\x90\xc2\xb1\x9d#\x81\xf7\
\x11\x8e\xebq\xe7j\xbb~\xfb\xb9p@\x15\x80\xbc?\xfez\x12\x98\xf8\xa7\xff\x134\
3=*\x00~\x01\xf6\xf4\xf1E\x16`z\x0f\x00\x00\x00\x00IEND\xaeB`\x826S:H' )

def HomeData():
    return zlib.decompress(
'x\xda\x01\xec\x06\x13\xf9\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \
\x00\x00\x00 \x08\x06\x00\x00\x00szz\xf4\x00\x00\x00\x04sBIT\x08\x08\x08\x08\
|\x08d\x88\x00\x00\x06\xa3IDATX\x85\xd5\x97k\x8c\x94\xe5\x15\xc7\x7f\xcf\xf3\
^\xe6\xb63{\xed,r\xd9aY\xae\x82\xd0\x05\xb1-\xc9\x86\x80m!\xb56\rI%VkC\xa2i\
\xd4\x04L#I\xbf\x99~\xf0\x8b\x9f\x0c\xa6\xb1\x97\x04\x04SQn\x89\xb6&n%%\x05I\
pk\x11\x0cVA\xc0\x95\x85eaY\x86\x9d\xcb\xce;\xef\xbc\xcf\xf3\xf4\xc3\\\xd8]\
\x86k\xe2\x87\x9e\xe4M\xde\x99\xf7\xbc\xe7\xfc\xcf\xff\xfc\xcf\x99g\xe0\xff\
\xd9\xde\x91\xf2\xc5\xbf\n1\xba\x13f\xdck\x0cq//\xed\x02\x17\xcb\xda\x91lk[;\
\xb5\xa1!q\xac\xbf\x7f\xb0\xa4\xd4\x0f\x9f\x80/\xbfu\x00; \x19\xb6\xac\x0f\
\xe7vu\xcd\xed\x9c:5\\\x1c\x19!\x93\xcb\xf1\xe9\xc0\xc0%?\x08~\xf6\x04\xf4\
\xddM<y7\xceo\xc2\xd2\xa8\xeb~\xfa\xe0\xd2\xa5\x8b:g\xce\x0c#%\x06\x88\xb8.\
\xdd\x1d\x1d\xed!\xc7y\xff-\xf8\xd1\xb7\x02`\x97\x94\xbfJ\xc4b\xff\xe8\xe9\
\xe9\x99\xda\x96LJ\xa4\x04\xcb\x02!0@\xc8q\xe8N\xa5\xdaB\xae\xfb\xf6;R>~\xa7\
qo\xdb\x82\x97@\xdeoY\xaf\xb5&\x93\xbf\\\xb6|y\x93%%(\x05Z\xa3\xaf]C\xa7\xd3\
\x14\x94B\x01\x06\x08\xb4\xe6\xc4\xc0\xc0U\xcf\xf7\x7f\xbf^\xeb-\xb7\x8bo\
\xdd\xb2jhLZ\xd6\xfe\xaey\xf3\xd6.~\xe8\xa1\x84\xb4*\xeeB\xa0GF0\xe94%\xa5\
\x08Y\x16\xca\x18\x941 \x04m\x89D$\xe3y\xdf\xff\xb9\xd6\x89\xdd\xc6\xfc\xf3\
\x9e\x18\xd8\x0es\xa3\xb6\xdd\xdb\xbdb\xc5\xf4\xf6T\xcaFkP\n\x13\x04\xe8s\
\xe7\x08FG9\x9e\x1e\xe1\xe2\xe5+,K\xa5\x98\x12\x8d2\xa65\x9e1\x18@\x03g\x87\
\x862\x99|~\xcf/\x94zZ\x94\t\xba\xc1\xeaj\xe0-\xcbz$\x11\x8b}\xd4\xf3\xe8\
\xa33\xdb\xe7\xcc\xb1\xb1,\x90\x12\xa3\x14\xfa\xecY\xc6\xae^\xe5\xe3\x91\xcb\
4\xbe\xb0\x89\x07\x8f\x1e\xe5\x9b\xc6\x18grY\xa2R\x12\xaeh\x02c\xe8loO\xb4$\
\x12\x8f\xed\xb6\xedw\x0f\x80}G\x0c\xec\xb2\xed\x97\x12\xad\xad\x9b\xbe\xb7v\
m\xb3\x13\x89\x94\xab\xd6\x1a\x93\xc9\xa0N\x9e\xe4j6\xcb\xe7\x85\x1c\xa9?\
\xbcN\xe4\x81\xc5(\xa5\x10Z3\xf4\xbb\x17\xb1\x8e\x1ega<A\x11\xc8(\x85\xa1\\\
\xf6P:]\x18N\xa7\xff\x93Vj\xcdo`\xac.\x80m\x10\x8eI\xb9w\xc6\xbcy=\x8bV\xaf\
\x8e\x8b\xf1b\xbbt\tu\xea\x14\xe7r9.D\xc2t\xbd\xb1\x1d\xd9\xdaJ\x10\x04H)\
\x91R\xa2\xb5f\xe4\x8f\xaf\x93\xdb\xb9\x93\xee\xc6&\x94\x10\\S\n\r\x18c\xb8\
\x96\xcd\x16/\\\xb9r2\xaf\xd4\xca\rp\xad\x9a\xd7\x02x\x13\xa6G,\xeb\xf0\x92\
\x9e\x9eesV\xae\x8cV\xc7\x0b!\xd0\xfd\xfd\x04\xa7N\xf1y.G\xee\xfe\x05\xcc\
\xde\xbe\x03\x19\x8f\xa3\x94"\x12\x89\xd0\xd2\xd2B,\x16C)Ex\xe92\x9c\x8e\x19\
|\xd1\xdb\xcb\x14\xdb!j\xdbx\xc6\xa0\x017\x14\xb2\xa3\xa1P\xab76\xf6\xd8O\
\x8c\xd9\xfd.\xe4j\x0c\xbc-\xe5`\xcf\xbauS\x9a\xba\xba\xca\x8ch\x8d\t\x02\
\xd4g\x9f\xe1\r\x0cp,\x9b\xa5\xf9\xa9\xa7h\x7f\xee9\x94Rh\xad\x89\xc5b\x84\
\xc3\xe1\t\xed+\x14\n\x14\n\x05\xbc\x13\'8\xf3\xec\xb3<\x10\n\xd1\x10\n1\xac\
\x14\xa5\x8a8\x8b\x9e\xa7\xbf\xb9x\xf1\x82Rj\xd5\xe3pF\x02\xd8R\x16\x9bf\xcf\
\x16X\x16X\x16F)\x82\xbe>2_\x7fM_&\xc3\xf4W^a\xca\xf3\xcfc\x8c\xc1\xb2,\x1a\
\x1b\x1bq]\x17\xadu\xedRJ\xe1\xba.\r\r\r\xc4\x96,a\xfe\xde\xbd\x9c\x90\x92+\
\x85\x02I\xdb\xc6\xad\x88\xd3\t\x85d\xe7\xb4i3,\xcb\xfa\xd7\xc4)\xa8l6\x93\
\xcf\x13\x1c<\xc8\xd0\xf9\xf3\x1c\xd3\x9a\x85{\xf6\xd0\xb8j\x15\xc6\x18l\xdb\
&\x1a\x8dVH\x9a\x98\xbcz/\x84 \x12\x89\x10\x9e6\x8dE\xef\xbd\xc7\xb9d\x92\
\xfe|\x9e\xa4m\x13\xa9\x80\x90\x8e\x83-\xa5\xb9a\x0c\xcd\xa5K\x94\x0e\x1c\
\xe0\xd4\xe5\xcb\x9c\xbb\xef>\xba{{\t\xcf\x9a\x05\x80\xe388\x8e3!\xf1\xe4\
\xe4\xe3/\xc7qp\x1a\x1bY\xb0k\x17\xf9\xe5\xcb\xf9o6\xcbw,\x8b\xb8\x94Hq}\xf8\
j\x00\xd4\xe9\xd3\x14\x0f\x1d\xe2\xc8\xe0 \xc1\xea\xd5,\xde\xb7\x0f\x19\x8fc\
\x8cAJ\x89\x10\xe2\x8e\x92OfC:\x0e\xb3^}\x95\xf0\x93O\xf2\xf1\xc8\x08\xcdR\
\xd2,\xaf\xd7m\x03\x04Z\x87\x87\x8e\x1c\xe1d:\x9d\x1d[\xbf>\xb6\xf4\xe5\x97\
\xa5\xd6\x1aLyy\x19c0f\xe2"\xab~\x16B`\xdb6B\x88\x1b|\xaa~J)\xa6m\xdc\xc8\
\xc1\xd3\xa7K\xc1\xfe\xfd\xc1\xfcD"RT\xaa\xa1\x06\xa0\xa8\xf5\xeaO\x06\x06\
\x0ewn\xd8\xf0\xdb}\xcd\xcd\xdb\x1e\xb6,\x82 `\xff\xfe\x0f\xc9\x8f\xe5k\x89&\
[4\x12c\xcd\x9a5l\xd9\xf2\x1a\xbe_\xbc\xe19\x80\xe3\x86xa\xd3F|\xdfgx\xf6\
\xec\xa0\xf3\xf0\xe1\x1f\x7f28\xf8\xf7\x92\xd6+j\x00~\r_`L\x0b[\xb7\xb2y\xf3\
\xe6m5U\x87\\\xbe:srB@!D\r\xcc\x82\xf9\x0b1\xc6\xe0\xfbET\xea\x11\\\xc7\xc2\
\xb1%Ji\xfc\x92\xa6X\n\xe0\xc2\x07\x18c(\x95JH)\x0b\xeb.^\xfc\x08h\xbaA\x03\
\xe3\xad\xda\xc3\x8e\x19\x1d\xd8\xb6]\x13\xa0\xeb\xba\xb5{\xc7qHu\xa4\xd0ZW\
\x80\x81\x14`\tQ\x16\xd98\xc2\xaam0uzT\xf7\x07\xc2\x18\x83\xd6\x9aT*\x85m\
\xd7u\x01\xa0\xad\xad\xad\x06`\xcc\x0b(\xfa\x8a\xb1b\xc0h\xbeH&_\xa4PT\xfc Z\
.\xa8\xb2\xb6\xfd\xbb\x02`\xd9v\xad\x12Q\xb9\x91\x8ca\x8b~|3\x1f\x045\x00\
\xff\xfer\xa8>\xca\xe8uF\x81\xd2\xe4\xc7\xb7lA5\xb1\xa0B\xa9\x00G|\xc5OW\xfc\
\rKd\x81\xfa\xca\xafgJ)\x80`\xf2\xf77e@)\x05\xc6LT\xbf\x00\x9f\xef\xb2\xfb\
\xd0\xa2Zk\xcaK\xc7eU\xd3\xf1\xba\x89m\xa7\xbc\xb2K\xa5\x12B\x08\xef\xae\x00\
\xd8\x8eC\xb9\xf8\x89#\xe88N\x19\x8f\x00\xcf\xf3x\xe6\x99\xa7\xeb\x8ei5V\xb1\
X\xac\xee\x92\xdb2\x10\xaaV\xa5\xb5F\nY7\xf0x@\xbe\xef\xe3\xfb\xd7\xb5U\xaf%\
RJJ\xa5\x12A\x10h\xa0\x8d\xf2y \x98\x0c\xc0\x05Z\x81\xc0\xf3<;\x1e\x8fO\x98\
\xf9\x9bY<\x1e\xbf\xe5\xf3*\xa0\xe1\xe1a|\xdfW\xc0\x94J\xde\xcb\x80\x1e\x0f\
\xc0\x06\xdc\xd1\xd1\xd17\xb6n\xdd\xba\xc1\x18s\xcb\x133\xc0\x9f\xff\xf4\x97\
\xdb\xb9\x8c7\xaf\xaf\xafo\'\x10\xa6\\\xac\x80\x89gBA\x99\x81V Qq\xba\xf9\
\x12\xb8;\xf3)\x9f\xbe\n\xc0(p\x1e\xf0&\x03\xa8\x9a\x03D*H\xef\xe9\xcfk\x1d3\
\x94w\x80W\xb9jB\xf9\x1f\xa0\xae\\\xe5 \xb9e\xc1\x00\x00\x00\x00IEND\xaeB`\
\x82\\\xa5a\xf8' )

def MonkeyData():
    return zlib.decompress(
'x\xda\x01\x81\x08~\xf7\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\
\x00\x00 \x08\x06\x00\x00\x00szz\xf4\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\
\x08d\x88\x00\x00\x088IDATX\x85\xed\x96k\x8c]U\x15\x80\xbf\xbd\xf79\xf7\xdc{\
\xe7>f\xe6\x0e\xd3\x99a\xa6\xd3)t\x86\x99\xd0\x16\x8b\xa2@\x8b\xa55\x1a\x03\
\r\xda\xa0\x08\x81\x88\x1a0\x02\x89\xe2\x0f#F\x13~\x18cLLD\x83\xc6\x88\x10\
\x12\x1bc" \x18\xa9?\xb4\xa5\xf6a\x91\xd0RJ\xa7\x9d\x16\xa6\xd3\xa1\xf3~\xdc\
\xb9\xef\xf3\xdc\xdb\x1f\xf7N\x18\xdbbR5\xd1\x1f\xaedeg?\xd7\xb7\xd6^g\xed\
\x03\xff\x97\xff\xb2\x88\xcbY\xbcy(5$\xd0w\xc4\x84\xbeS\x1b\xd1\x13i\xd1\x0c\
\xa0\xa4Y\x92\xc2\xbc\xeb\x1b\xf9[\x83|\xf1\xc0py\xf8?\n\xb0\xb9\xbfi\x83m\
\xeb\'S\xc9\xd4\xa6\r\xeb\xba\xacu\xbd]\xb1\x96L\x8aD"\x01@\xadZ%_,sf|\xd2?v\
z2\xa8\xd6*G\xfd@>|\xe0t\xe5\xcd\x7f\x1b`\xeb5\x89\x87\x9dD\xe2\x07\x1f\xbfq\
}\xfc\x9a\xbe.Y\x9d\x1b\xa3\x9a\x9f \xa8.a\x82\x1a\x00V,\x89\x95\xcc\x92l\
\xed&\xd9\xb6\x86\x93\xa3\xef\xea\xdd\x07\x8f\xbb\x81\xe7}\xe3\x95S\xb5\'\
\xffe\x80[\x87\xe2\xdfl\xce6\x7f\xfb\xee\xdbnn\n\x16\xce\x91\x1f?\x0e\xdaG\t\
\x90\r\x15\x80\x01\xb4\xa9+\x96Ck\xefu\x88t\x07\xbb~\xbf\xbfR\xacT\xbe\xbbw\
\xd8\xfd\xfee\x03\xdc2\xd0\xb4\xbe).\xf7\xdf\xbfs{v\xfe\xec\x11\x96\xca\x15\
\xdcHb0$lI2,\x90Q>R@)\x8aQRYj\x81F"\x88+M[\xb6\x99\xe6\xd5C\xfc\xf2\xb9=\x85\
\x9a\xc7\x96\xbf\x8cT\x8e_\x16\xc0\xb6\xc1\xc4\xf0\xed\xb7\\;\xe8\x04K\xcc\
\x95\x8al\xd9\xfc1\x06\x876\xa0\xac\x18\xd3\xd3\x13\xec\xd9\xb3\x1b\xb34^?\
\xa0y5\xdb\xb6\xddFg\xe7\x95\x84Q\xc8\xa9So\xb1\x7f\xefn:\xdaZ)\x076\x7f8t\
\xfa\xe4\x9e\x93\xb5\xa1\xf7\x05\xb8i \x97\x8e\xa9\xea\x8f\x8c\xe1n\x8cPR\
\xf2\xd7T\xdc\xfe\xc0};6gFN\xbc\xc6\xed;>KWG\x07Qu\x11\x13\x05\x08e\xa3\xed\
\x0cO\xefz\x16\x80/\xde{?\xd2/bB\x0f\xa1,\xac\xd4\x15L\xcd\xcd\xf3\xd2\x0b\
\xbb\x18Z\xffa\x9e~~O\xb1\x1a\x98\xa3Zs#\xc2DB\xf0k?J~\xed\xd0\xc8BI\x01\xf4\
w\x8a=]\xcd\xea\x13\x1f\xea\x8b%ZSR\x95=V\xf7]\x99\x8b\xc7L\x85L\xa6\x99\x1b\
6]O\xb04\x85\t]L\xe8c|\x17\x19\xb9\\3\xb4\x89\xfe\xab\x07H\x84\x05\xb4[\xc0D\
!&\xf4\xd1n\x81lk\'\x933\xd3\x94\xf2\x0b\x84\x06\xa7\xe6y\xab\x07\xbblk\xa0\
\xc3\xb2C\xcd\xa0\x17\x04\xdb\xce\xce\x06O\xab[\xfa\x93\x9fl\xcf\x88\x87\x06\
\xbb\x9c\xd4\xe9Y\xc9\xd0Uk\x99\xcfWE\xf7\xaaV\x8c_d\xe3\x86\xebi\x89\x0b\
\xb4W\xc2\x84\x01&\xf21\x91\x8f\xf6\xabXa\x15\'\xaa\xd4\xe7\xa2\x00\xa3\x03\
\x8c\x0e!\x8a\x00\x83tR\x8c\x8e\x8e\xa0bM\xcc\x17jb\xd3\xfa!N\x9d/\xd0\x97SV\
\xd5\x0b\xb3\xb9&\xfb\x98\x8c\xc7ylc\x8f\x95=\xbb\xa8\xf8\xd6\x17v\xb0\xf3\
\xe6!z;Z0\x80\xd1\x86d\xc2A\xbb%L\xe0b\x8cf2\xef\xf1\xcc\x9f\xcf2U\x02a\xc5\
\x10\x96\xc3T\x19\x9e\xd9{\x8e\xc9B\x84\x90\x16\xc6h\xb4["\x99L\xa2\xb5\x06`\
\xa0;\xc7\xce-\xeb\xf9\xceC\xf7r\xbeh\xb1\xb1\xc7\xca\xc6\xe3<&\xa3\x88\x81@\
\x0b\x86\xd6\xf6\x90\x89\tL\x14\xd0\xde\x96\xa3\\\xa9!\xa4\xc0\xf5\x02P62\
\x96B:)\x1e\xfc\xc9~\x1e\xdf\xf57\x1ex\xe2\x15\xa4\x93F:i\x1ex\xe2\x15\x1e\
\xff\xd5\xab<\xf8\xe3}H\xa7\xbeN\xdaI\xfc\x08\xa4R\x94\xaa.\xed\xb9\x16\xb4_\
#a\xc1\xc6\xc1u\x84Z\x10E\x0cH@hm\xb0\x04\x98\xd0G\xc6\x92\xf4\xf7\xf50[\xf4\
\x89\xc5SL\xcd\xceb5\xe5\x90N\x132\xd6\xc4\xd8L\x01\x80\xb1\x99B\x1d \x9eflz\
y\xacX\x07\x8d5a\xa5\xdb\x99\x98\x9a\xc4I\xa4\x98Z\xac\xb2\xae\xb7\x07\x13x\
\x98\xd0\xc7R\n\xad\r\x80\x90\x96\x12gbJpb\xf4<\xae\xeb"\x94\xc3\x9a\x9e+97\
\xb5H&\xdb\xc6\xc9\x91a\xc2x\x1b\xc2I#\x9d\x14\x8f~n+\xe9\xa4\xc3\xa3\xf7lG:\
i\x94\x93\xe2\xd1{\xb6\xd7\xc7\xee\xbe\xb5\xee}<\x83Nur\xe2\xc4\x1b\xa4\xd2-\
L\xcc\x97\xe9\xeb\xee\x00)\t\x82\x807O\x9e\xc1V\x02K\x893b\xeb`\xe2\x8e\xcef\
\xf5\xec\xdav\';SVl\xbfa#/\x1d8AK&FO\x8b \xd7\xde\xcd\x1d\x9f\xba\x17S\x9eEH\
\x0b\xa1l\x84\xb2A*\x84\x90,\xd7Bc4\xe8\xa8\x91\x8c\x11*\xdb\xcd\xf3\xcf=C~z\
\x94\xd1\xe9\x1as\xc5\x80\x9d\x9b\xfb9<<N\xc2r9?\xef\x16\xa6\x96\xa2\xcf\xab\
\xb1\xf9pdU\xd6\xfe\x8c$j\xedn\xd6\xd6\xd1\xb7\'Y(\xb8l\xba:G*\x95f\xf3\xd6O\
\xf3\xc6\xd1\xd7Y(V\xa8\xf8\x9aH(P\x0e\x96\xd3\x84\x15K"\xac\x18!\x8ar- _\
\xac013\xcf\xdb\xe7&89r\x92\xebo\xb8\x95\x99\xa912q\xc3\xe9\xf1\x05\xa6\x17\
\x17\xc9%=\xe6\x96\x02or\xc9\x8c\xec\x1d\xae~]\x00|d(\xd3\x9a$\xfcY\xa0\xd9\
\xa9$\xea\xba\xbef\x91k\x82;\xef\xfa2\xb9L\x92\xc0\x0f\x98Y\xaa2\xb3Xdvq\x89\
\xf9|\x91\x85\xa5"\xae\xeb\x12i\x8dm[\xb4d\xb3\xb4\xe7ZX\xd5\xd6JW[\x0b\x9d\
\xb9\x0cN\xdc!_\xf5\xf9\xcd\xb3?d\xae\xe0sl\xbcb"MdK\x9e\xafb}\xe5\xf0pq\xd1\
\x028<\\\\\x04\xee\xfa\xe8G\xb1\xcclb\xb6%\x9dh\xf1\xfd\x12-m\x1d\x187\x8f\
\xed\xc4Y\xdd\xddBo\xdfUH+\x8e\xb0\xe3\x08\xcb\xa9_\x87\x90\x18\xa3\xeb\xa1\
\x0f=L\xe0\xa2C\xb7\xd1z\xb4\\\xd1\x8d\x17\x04\xb4f\x9a0\xa6\xbc$W\xd5\xda\
\xf7\xec#\\.\xc5re]\xde\xb7\x8fPCBJ\t\xc6 \x94\x85\x90\n!U\xfd\xce\xa5\x02\
\xb5\x9c\x07\x0e\xd2N\xd6\xbf\x04;\x89Pu \x1a{\x90\n\xa9,\x10\x02\x8cA*\x89\
\x86\xc4\xbe\x15\xc6/\x02\x00P0W\xae\xb9X\xca"??\x8d\xb0\x13`LCi\xa8\x01t\
\xdds\x1d\xd6\x13\x10}\xd1\x1ai\'Y\x9c\x9b\xc0\xb2l*5\x1f\x05s\x17\xda\xbb\
\x08\x00\xcc\x8b\xd3\x0b\x95 \xd4ph\xffn\xacdk\xdd\x0b\x1d\xd6\x8dE\xfe{\xa1\
\xf6\xcah\xaf\x84\xf6\xca\xf5J\x19z\xf5y\x1d \x00\x95n\xe3\xd0\xde\xdf\xa15L\
\xe5+\x01\x98\x17/\xe1\xf0?J\xcf*\xeb\xadR%\xfcRO{:QX\x9a\xc5R\x92\x9e\xfeM\
\x10\xfa\xf5:\xcfr4\xa2z?\xf4\xdf\x83\n=L\xe4!\xa4\x85\x9d\xed\xe0\xb5\x83/s\
\xec\xf5\xfdh\x11\xe3\xf8X\xb1\x18I\xee\x1b\x9f\x0b\x8b\xff\x14`|.,\xf6\xe6,\
\xbdX\xf6n\xechM\xc5\xde\x1d;\xc5\xfc\xdc\x04\xbd\xfd\x9bpR\xcd`\x0cFG\x8dG\
\xa9\xf18\xe9\xb0\x9136*\xd9\x8cg$\x7f|\xe1)\x8e\x1c\xfe\x13F9\x1cy\'_v=\xfd\
\xbd\xfd\xa7\xdc\xdd\x17\xda\xbb\xd4\x0f\x89\r\xc47\x0f$~\x91N\xd8;\xd6\xf7\
\xa6\x936\x1eJY\\5p-\xd7^\xb7\x99\xf6\xae54\xa5sX\x8e\x03\x08\xc20\xa0Z\\dnz\
\x9c\xb7\x8e\x1e\xe0\xcc\xf0\x11\xa2($\xc0\xe1\xf8\xb9R\xb5X\xf5_>x\xda}\x04\
p\x01\xaf\xd1^\x12 \xde\xd0\x04\x10\xff\xe0Z\xe7\x91t\xc2z\xa8;\x97\xb0zrq\
\xcbD.\xb6\x92\x08)\x89tTO\xb6\xc6)J*\xb4\xd1\x84\xa1F\xaa8\xe7\xf3^8>W\r\
\x0b\x95\xe0\xa9#c\xfe\xcf\x1bF]\xa0\xd6h\xab\x80\xb9\x10 \xb1B\xe3@\xa23\
\xab\xae^\xd3n\x7f\xd5V\xf2\xa6\xd6\xb4\x13\xb5\xa5\xadD:n\xe18\n\xd5\xd8\
\x1d\x19\xf0\xfc\x88\xb2\x1b1W\x0c\xdc\xc5\x92\xa7\xfc0zut6\xf8\xe9lQ\x8f\
\xae0\xba\x0cP\x05*\x97\x8a\x80\x00\x1c \xd9\x00p\x96\xdbL\x93\xba\xa2\xa7\
\xd9\xda\x92I\x8a-J\xb1N"Z5"V\xdfd\x02\x83Y\x0cC\xf3N\xa1\xca\xc1\xf3\xf9\
\xf0P\xa9\x16\xcd7\xc2\xbd\xac\xcb\xc6\xcb\x8d\xfe\xfb\xe6\xc0\xb2( \xb6\xe2\
Zb\x80\xb5B\x97_\xa2\xe53\xea\xc5\x01B \x02\x82\x15^\xbb\x80\xdf\x98\xbf\xc8\
\xe3\xcb\x11q\x81\xe1e]\xce\x06\xbd\x02\xc4\\\xea\x80\xff9\xf9;~\xcc\x03\x9c\
\xc4\x14l\xa6\x00\x00\x00\x00IEND\xaeB`\x82\x86\xa8"\xb3' )

def DevilData():
    return zlib.decompress(
'x\xda\x01\x03\x07\xfc\xf8\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \
\x00\x00\x00 \x08\x06\x00\x00\x00szz\xf4\x00\x00\x00\x04sBIT\x08\x08\x08\x08\
|\x08d\x88\x00\x00\x06\xbaIDATX\x85\xed\x96[\x8c\x95W\x15\xc7\x7f\xfb\xbb\
\x9e\xcb\xcc\xb9\x0cs\x98\x1b\xc3e(\xbcTn\xa5\rH5\xd4d\x92J\xc8<4i-!Q\x12\
\xa9<\xa0R\xab>\x19\x91\xa0I\x1f4\xb1I\xdf\xd4\x90\x92\xb6F$dLj\xb0\xa9Ui\
\xa5-\xad\x8e\n3\xad\xa5Pf\x80\x99\xce}\xce\xfd\xccw\xff\xb6\x0f\xe7;\x93\
\xd3\x11\x01\x1b\x13_\xfaO\xfe9\xdf^g\xed\xbd\xfe{\xed\xb5\xb27|\x8a\xff3D\
\xf3\xe0\xb4\xa2\x9c\xf5\xa5|P\n\xf1}=\x0c\x7f\xfe%p\x8f\x81\xa1\xc3\x174\
\xc1>\x05>\x17B.\x94\xb4*\x82\x8a\x02s\xa1\xe4\r\x1fNyp\xee8\xb8\xa7\xc1\xf0\
\x14\xe5\x1b\x02\x8e\xaa\xf0\xd6\xe3a\xb8\xf7\xee\x05\x98j\xf1\xe1\x9fnJ\xdf\
|\'\xef|\xf0\x9b\xa9\xc2l\xc5{\xa9\xa2\xf0\xd8\xca\xae\x84\xbanc\xaa5\xb7*)b\
\xad:zL\xc5\xb3\x02\xac\x8a\xc7\xdcDM^\xbfR\xae\xccN/\x06\xad!\x83+\xb3\xc6\
\xc0\xbd\x8fug\xba\xb7d\x8c\xb3\xdf\xbcT\xda\x1f\xca\xcc\xed\x04\xa8\xcd\x83\
G\xa40[;s\xbb\xd6h\x1b\xcdV\xdbh\xa9\x15\n\xf7\xf5t%\xe2;\xf6t\x99i,\xa1\xe7\
\x0b\x88\x99\x05\xe4\xc4\x1c,\x940j\x16\xe9\xb4&\xfa>\xd3n\xcaI\'\x9eMg\xef{\
\xe0\xa1\x07\x92\x1d\x9d\xbd\xea\x8d\x91yg\xfa\xbd\xf9\x1f\x0fJ\xf9\xfa]g\
\xe0\x05H\xa9\x8a2\xf5\xf9u\xeb\x12-\x86A\xd5q\xb80~\x9d\xed\xdbA\x8d\x83j\
\x82\xd0\xea\xb3d\x00\xa1\x0b\xa1\rAM24,\xd8\xbd\xae\x8f\x98\xaeSu]\xce\x8f\
\x8e..J\xd9\xf9\x04Tn\'@k\x1e\xdc\x80\xd6\x15Rrea\x8e\xbeL\x1b\xc3\xd3\x93\
\xac\xee\x05\xad\x05\xb4$\xa81\x81\xd0\x9b\x048\x10\x18\x12\x14AO\'\x0c}4\
\xce\xa6\xcen\xae\xe5\x17(\x83\x9c\x87\x14w\x10\xa04>$\x08\x1d\xcen\xdc\x9c3\
\x8b\x9e\xc5\xdf\'o\xb2\xb2\xc3\xa3k-h-\x02\xadU\xa0\xa5A\xcf\n\x8c\xac@\xcf\
\x80\x9e\x8a\xfeKB\xcf\x1a\xc8d\\\x86&nP\xf2,\xd6o\xcc\xc6t8+\x97ey9\x96j\
\xc0\x80}\xdd\xed\xf1/\xdf\xbb\xb5=\xdeV\xc8\xd3\xd9%I\xad\x14xq\xf8\xfa%\
\xc9\x93o\x87\xfc\xf1#\xd8\xb9A\xd0\xd9.p\x10|\xf5\x95\x90\'/\x84\x9c\x9b\
\x87m\x19Ao\x02V\x18\x90\x96!\xd9\xbev\xa5Xr\x12\xbf\xb3\x83\xb1?\xc1\xbb\
\xb7\xcd\xc01\xd04xf\xeb\x96\x95)\xe7\xd2\x14H\x89P\xeb\xe7\xfd\xec\xa8\xa47\
\x05\xd7\x0ei\x1c\xb8_\xf0\xed\xdf\x87\xe8\x19\xc1O\xfe\x1a\xb2:+\xb8r@e\xff\
z\xc1\xd1\xab!\x8a&\xea\xf3\x908\xef\xcf\xb3yc[J\x83g\x8e-;\xeaf\x08\x80\x1f\
A\x7fO{\xfc\xccg\xb7v\xa4\x9dw\xae\xa3g\x04z\x96z\xaa\xb3\x02-\x0bfd\xd32\
\x02-\x0e^\x01\x9c\x82\xc4/J\xbc\x02\xd8yIP\x04\xaf q\x0b\x12\xaf\x08\xb1\
\xed]\\\xb8\x9c/M\x95\x9cG\x8f\xc2\x1f\xa2\xa3\x8e#\xc4\x19\xa0\x82\x94O+\
\x00&\xec\xeb\xednI\xf9\x13\x15dX\xf7B\x82\x0cA\x86\x12\x11\xd4\x8bNz\x10Z\
\xe0\x97!t$\xf8\x91=\x00E\x82\x94\x12\xd9\x98+\xc1\x9f\xae\xd1\xd3\x9eH\x99\
\xb0O\x82*\x85\xf8!\xf0\x040\x0e\x04\xc0H#5\xbb\xb3+\x12\xc2\xbf8\x13-(\x91\
\xbe@\xfa \xddz\xbb\x05\xb6Dh\x02\x19HP"\x9bUo\xc3\xd0\xabSz\xd4\xe7\x04\xf5\
\xe5\xfd\x82M\xdb=m\x02\xd8\xed\xc1N]\xcaQ\x01\'\xa5\x94\x06\xa0\t\x90\x1a@\
\x08\xb9XLe\xc4\x860\xd0Qjq\x82\xa9r\x94\x8aO\x8e\x94\x96\xa4WW\x08!W\x80\
\xe98<\x0e\x9c\x14\xe0Rg\xbd8\x02Hk\x86\x8a\x0cB6\x0c\x0e\x92\xec\xe8 \x91\
\xcb1::\xca\xb6m\xdb0M\x13\xd34Q\xd5z\xd3\x8c\x8c\x8c\xb0i\xd3\xa6\x8f\x05\
\x0b\xc3\x90\xa1\xa1!\xfa\xfa\xfa\xb0m\x9b\xd9\xf3\xe7\xb9~\xf80\x86&\x08 \
\xdd\x01\xd7& ;\r\xfd\x9dQ=@\xd4\x05*\x94\xbcE\x0f\xe9y\xe8==\xa8\xa9\x14\
\x00\xba\xae\xdfrg\x9av\xeb\xa2n\xf67\xba\xba\xf0]\x07\xcf\xf6Q\xa1\x04\x90\
\x87#Uxv\x02v}L\x80\x02sv\xcdCkI\xe2MN\xde1\xd0\xdd\x08\xf0\x0b\x054E\xc1\
\xb2\x03\x14\x98\x03\xd8\x0c\x85\n|\xad\x0c\xbf\xfd\x106,\t\x00^_\x98\xb7d\\\
W\xb0/_\xbe\xe5\x82w#\xa0\xd9n]\xb9\x82\xa9\x84,\x94\x1c\t,]H\xdb\xe0\xcd\
\x12\xfc\xaa\x04\'\x97\x048pjb\xa6V\xce\xb5k\xe4\x9f\x7f\xfe\x7f\x92\x81\xf9\
\x17_$\x9b\xd2\x98,\xd8e\x07N5\xfbU\xe1D\x15v\xbd\x01\xeb\x15\x00\x1f^[(9\
\x96\x96\xd0\xf0?\xbcJuh\xe8\x13e\xa0\xe1_\x1d\x1e\xc6\x1d\x1bE3U\n5\xcf\xf2\
\xe1\xb5f\xbf2d+@\rB\x05\xe08\xf8><\xf5\xee\xb5by\xf5\xea\x04cG\x8e\xe0-,\
\xfc\xc7@\x8dn\xb8\x95\x00\xafT\xe2\x9f\x07\x0f\xb2\xaaM\xe5\xbd\xc9j\xd9\
\x87\xa7\x8e\x83\x0fp\x1a\xd4_\xc0@\x05^(\xc3\x9b\x0f\xc3\xd8\xd2m\xf8=\xf8\
\xf5l\xc5\x1d+\xd8~\x903\\\x86\xf7\xee%\x9c\x9d\xfd\xaf2 \xcbe\xfe\xd2\xdfO\
\xca-\x93w\xc3p\xd2\xf2\xadI\xb8\xff\xbb\xf0\xb3\x1f\xc0\xab\xd7`\xa6\x0c/\
\x95a\xb6\n\xfb\xa0\xe9:\x16 \xcb0p\xf1F\xa9\xa0\xa4\x0c\xda\x95EF\xf6\xec\
\xe1\xc6\x89\x13\xc80\xbc\xa3\x80\x9b\xa7N\xf1\xd6\x8e\x1d\xb4T\xe6\xd0\x93\
\x1a\xff\x98\xa9)\xd7\xa1\xc3\x82\xef\x94\xe0\xd0<\xf4\xcf\xc2\xf84|\xeb*\
\xec<\x04\x13Q\xdc%\x18@\xec \xec\xb8Gpfko*\x993Uu|\xc6G&\x92\xac;p\x80\x9e\
\x81\x01\x92k\xd7\x12&\x12\xa8\x96Em|\x9c\xa9\x97_f\xec\xb9\xe7\x08\xf2\x0b\
\xf4\xa4\x05\xb3\xbe\xe4\xe2LM^\x86\x89*LJ\x98pax\x0e\xde\xfe\x1b|\x00X\x80\
\x1d\xd1m\x08P\x80x\x83\x0fA_?\x9c\xcc\xa5\x8c\xce\xcd\xdd\xad1\xc5\xf6)\x16\
=lt\\\xd7\xc3u\x1ct\xd3\xc0\xd0ub\x81K\xbaUC\x9a*\x97\xe6\x16\xdd\x99\x9a\
\x97\xff%<}\xb5\xbe\xc3F0k\x19\x1b\xb6Zs\x06bM"bIh\xf9\n\xec_\x05\x873I]]\
\x932\xe2+\x12\xba04\x05]Qp\xfd\x00\xd7\x0b\x98\xaf\xf9\xf2f\xd5\xb5\x8b\x96\
/G`p\x10^\xf5`\xb1i\x97\xd6-\xbe-\xeaO5\x7f\xf9sI\x07\x12\x80\x19\t2\xd3\xd0\
\xf2Exp-\xeci\x81-\nd\x04\xc4%\xd8\x01\x94\x8a\xf0\xfee\xf8\xf39\xb8d\x81\
\x03x\x11\x1b\x17\x8e\xd3D\x0b\xa8E\xbfry\r4CD5\xd1\x10bD\xe2\xb4\x88jtl"b\
\xf4\n \xa4~\xcf\xfb\x11\xdd\xa6\x1d\xbb\x91\xed\xdf\x02\xdd-\x1a\x01\x95&6\
\xa3!\xa0\xc1\x86\xa8Oq[\xfc\x0bx\x08\x03IE\xb9\x98\x93\x00\x00\x00\x00IEND\
\xaeB`\x82\x9aiO\x94' )

def getBitmap(name=''):
    return BitmapFromImage(getImage(name))

def getImage(name=''):
    if name =='bookmark':
        stream = cStringIO.StringIO(BookData())
    elif name == 'home':
        stream = cStringIO.StringIO(HomeData())
    elif name =='monkey':
        stream = cStringIO.StringIO(MonkeyData())
    elif name == 'devil':
        stream = cStringIO.StringIO(DevilData())
    else: # 'address'
        stream = cStringIO.StringIO(AddressData())

    return ImageFromStream(stream)

#-----------------------------------------------------------------------------#
if __name__ == '__main__':
    try:
        import sys
        import run
    except ImportError:
        app = wx.PySimpleApp(False)
        frame = wx.Frame(None, title="PlateButton Test")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(TestPanel(frame, TestLog()), 1, wx.EXPAND)
        frame.CreateStatusBar()
        frame.SetSizer(sizer)
        frame.SetInitialSize()
        frame.Show()
        app.MainLoop()
    else:
        run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
