###############################################################################
# Name: segmentbk.py                                                          #
# Purpose: SegmentBook Implementation                                         #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Editra Control Library: SegmentBook

A L{SegmentBook} is a Toolbook like class derived from a ControlBox and
SegmentBar. Allows for a multipage control with Icons w/ optional text as
page buttons.

+-----------------------------------------+
| @^@    *>                               |
| <->   /|D                               |
| frog  bird                              |
+-----------------------------------------+
|                                         |
| Main Page Area                          |
|                                         |
|                                         |
|                                         |
|                                         |
|                                         |
|                                         |
|                                         |
|                                         |
+-----------------------------------------+

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = ['SegmentBook', 'SegmentBookEvent', 'SEGBOOK_STYLE_DEFAULT',
           'SEGBOOK_STYLE_NO_DIVIDERS', 'SEGBOOK_STYLE_LABELS',
           'SEGBOOK_NO_WHERE', 'SEGBOOK_ON_SEGMENT', 'SEGBOOK_ON_SEGBAR',
           'SEGBOOK_NAME_STR',
           'edEVT_SB_PAGE_CHANGING', 'EVT_SB_PAGE_CHANGING',
           'edEVT_SB_PAGE_CHANGED', 'EVT_SB_PAGE_CHANGED',
           'edEVT_SB_PAGE_CLOSED', 'EVT_SB_PAGE_CLOSED',
           'edEVT_SB_PAGE_CONTEXT_MENU', 'EVT_SB_PAGE_CLOSED', ]

#-----------------------------------------------------------------------------#
# Imports
import wx

# Local Imports
import ctrlbox

#-----------------------------------------------------------------------------#
# Events
edEVT_SB_PAGE_CHANGING = wx.NewEventType()
EVT_SB_PAGE_CHANGING = wx.PyEventBinder(edEVT_SB_PAGE_CHANGING, 1)

edEVT_SB_PAGE_CHANGED = wx.NewEventType()
EVT_SB_PAGE_CHANGED = wx.PyEventBinder(edEVT_SB_PAGE_CHANGED, 1)

edEVT_SB_PAGE_CLOSED = wx.NewEventType()
EVT_SB_PAGE_CLOSED = wx.PyEventBinder(edEVT_SB_PAGE_CLOSED, 1)

edEVT_SB_PAGE_CONTEXT_MENU = wx.NewEventType()
EVT_SB_PAGE_CLOSED = wx.PyEventBinder(edEVT_SB_PAGE_CONTEXT_MENU, 1)
class SegmentBookEvent(wx.NotebookEvent):
    """SegmentBook event"""
    pass

#-----------------------------------------------------------------------------#
# Global constants

# Styles
SEGBOOK_STYLE_DEFAULT     = 0   # Default Style
SEGBOOK_STYLE_NO_DIVIDERS = 1   # Don't put dividers between segments
SEGBOOK_STYLE_LABELS      = 2   # Use labels below the icons

# Locations used in HitTest Results
SEGBOOK_NO_WHERE = -1
SEGBOOK_ON_SEGMENT = 0
SEGBOOK_ON_SEGBAR = 1

# Misc
SEGBOOK_NAME_STR = u"EditraSegmentBook"

#-----------------------------------------------------------------------------#

class SegmentBook(ctrlbox.ControlBox):
    """Notebook Class"""
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=SEGBOOK_STYLE_DEFAULT,
                 name=SEGBOOK_NAME_STR):
        """Initialie the SegmentBook"""
        ctrlbox.ControlBox.__init__(self, parent, id, pos, size,
                                    wx.TAB_TRAVERSAL|wx.NO_BORDER, name)

        # Attributes
        self._pages = list()
        self._imglist = None
        self._use_pylist = False

        # Setup
        bstyle = ctrlbox.CTRLBAR_STYLE_GRADIENT | \
                 ctrlbox.CTRLBAR_STYLE_BORDER_BOTTOM
        if style & SEGBOOK_STYLE_NO_DIVIDERS:
            bstyle |= ctrlbox.CTRLBAR_STYLE_NO_DIVIDERS
        if style & SEGBOOK_STYLE_LABELS:
            bstyle |= ctrlbox.CTRLBAR_STYLE_LABELS

        self._segbar = ctrlbox.SegmentBar(self, style=bstyle)
        self.SetControlBar(self._segbar, wx.TOP)

        # Event Handlers
        self.Bind(ctrlbox.EVT_SEGMENT_SELECTED, self._OnSegmentSel)
        self._segbar.Bind(wx.EVT_RIGHT_DOWN, self._OnRightDown)

    def _DoPageChange(self, psel, csel):
        """Change the page and post events
        @param psel: previous selection (int)
        @param csel: current selection (int)

        """
        # Post page changing event
        event = SegmentBookEvent(edEVT_SB_PAGE_CHANGING,
                                 self.GetId(), csel, psel)
        event.SetEventObject(self)
        handler = self.GetEventHandler()
        if not handler.ProcessEvent(event) or event.IsAllowed():
            # Do the actual page change
            self.Freeze()
            self.ChangePage(csel)
            self.Thaw()

            # Post page changed event
            event.SetEventType(edEVT_SB_PAGE_CHANGED)
            handler.ProcessEvent(event)
            changed = True
        else:
            # Reset the segment selection
            self._segbar.SetSelection(max(psel, 0))
            changed = False
        return changed

    def _OnRightDown(self, evt):
        """Handle right click events"""
        pos = evt.GetPosition()
        where, index = self.HitTest(pos)
        print where, index
        if where in (SEGBOOK_ON_SEGBAR, SEGBOOK_ON_SEGMENT):
            if where == SEGBOOK_ON_SEGMENT:
                self._segbar.SetSelection(index)
                changed = self._DoPageChange(self.GetSelection(), index)
                if changed:
                    # Send Context Menu Event
                    pass
            else:
                # TODO: Handle other right clicks
                pass

        evt.Skip()

    def _OnSegmentSel(self, evt):
        """Change the page in the book"""
        psel = evt.GetPreviousSelection()
        csel = evt.GetCurrentSelection()
        self._DoPageChange(psel, csel)

    def AddPage(self, page, text, select=False, img_id=-1):
        """Add a page to the notebook
        @param page: wxWindow object
        @param text: Page text
        @keyword select: should the page be selected
        @keyword img_id: Image to use

        """
        page.Hide()
        self._pages.append(dict(page=page, img=img_id))
        segbar = self.GetControlBar(wx.TOP)
        if self._use_pylist:
            bmp = self._imglist[img_id]
        else:
            bmp = self._imglist.GetBitmap(img_id)
        segbar.AddSegment(wx.ID_ANY, bmp, text)
        idx = len(self._pages) - 1

        if select or idx == 0:
            segbar.SetSelection(idx)
            self._DoPageChange(segbar.GetSelection(), idx)

    def ChangePage(self, index):
        """Change the page to the given index"""
        cpage = self._pages[index]['page']
        page = self.ChangeWindow(cpage)
        if page is not None:
            page.Hide()
        cpage.Show()
        self.Layout()

    def DeleteAllPages(self):
        """Remove all pages from the control"""
        for page in reversed(range(len(self._pages))):
            self.DeletePage()

    def DeletePage(self, index):
        """Delete the page at the given index
        @param index: int

        """
        cpage = self._segbar.GetSelection() 
        self._segbar.RemoveSegment(index)
        npage = self._segbar.GetSelection()
        self._DoPageChange(cpage, npage)

        self._pages[index]['page'].Destroy()
        del self._pages[index]
        
    def CurrentPage(self):
        """Get the currently selected page
        @return: wxWindow or None

        """
        idx = self._segbar.GetSelection()
        if idx != -1:
            return self._pages[idx]['page']
        else:
            return None

    def GetImageList(self):
        """Get the notebooks image list
        @return: wxImageList or None

        """
        return self._imglist

    def GetPage(self, index):
        """Get the page at the given index
        @param index: int

        """
        return self._pages[index]['page']

    def GetPageCount(self):
        """Get the number of pages in the book
        @return: int

        """
        return len(self._pages)

    def GetPageImage(self, index):
        """Get the image index of the current page
        @param index: page index
        @return: int

        """
        return self._pages[index]['img']

    def SetPageCloseButton(self, index, button):
        """Set the property of a page
        @param prop: Property to set

        """
        if wx.Platform != '__WXMAC__':
            self._segbar.SetSegmentOption(index, ctrlbox.SEGBTN_OPT_CLOSEBTNR)
        else:
            self._segbar.SetSegmentOption(index, ctrlbox.SEGBTN_OPT_CLOSEBTNL)

    def GetPageText(self, index):
        """Get the text of the current page
        @param index: page index
        @return: string

        """
        return self._segbar.GetSegmentLabel(index)

    def GetSelection(self):
        """Get the current selection
        @return: int

        """
        return self._segbar.GetSelection()

    def HasMultiplePages(self):
        """Does the book have multiple pages
        @return: bool

        """
        return bool(self.GetPageCount())

    def HitTest(self, pt):
        """Find if/where the given point is in the window
        @param pt: wxPoint
        @return: where, index

        """
        where, index = (SEGBOOK_NO_WHERE, -1)
        index = self._segbar.GetIndexFromPosition(pt)
        if index != wx.NOT_FOUND:
            where = SEGBOOK_ON_SEGMENT

        # TOOD check for clicks elsewhere on bar
        return where, index

    def InsertPage(self, index, page, text, select=False, image_id=-1):
        """Insert a page a the given index
        @param index: index to insert page at
        @param page: page to add to book
        @param text: page text
        @keyword select: bool
        @keyword image_id: image list index

        """
        raise NotImplementedError

    def SetImageList(self, imglist):
        """Set the notebooks image list
        @param imglist: wxImageList

        """
        self._imglist = imglist

    def SetPageImage(self, index, img_id):
        """Set the image to use on the given page
        @param index: page index
        @param img_id: image list index

        """
        page = self._pages[index]
        page['img'] = img_id
        self._segbar.SetSegmentImage(self._imglst.GetBitmap(img_id))
        self.Layout()

    def SetPageText(self, index, text):
        """Set the text to use on the given page
        @param index: page index
        @param text: string

        """
        self._segbar.SetSegmentLabel(index, text)

    def SetSelection(self, index):
        """Set the selected page
        @param index: index of page to select

        """
        csel = self._segbar.GetSelection()
        if csel != index:
            self._segbar.SetSelection(index)
            self._DoPageChange(csel, index)

    def SetUsePyImageList(self, use_pylist):
        """Set whether the control us using a regular python list for
        storing images or a wxImageList.
        @param use_pylist: bool

        """
        self._use_pylist = use_pylist
