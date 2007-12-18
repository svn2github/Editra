# -*- coding: utf-8 -*-
###############################################################################
# Name: browser.py                                                            #
# Purpose: UI portion of the FileBrowser Plugin                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Provides a file browser panel and other UI components for Editra's
FileBrowser Plugin.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import stat
import zipfile
import shutil
import subprocess
import threading
import wx

# Editra Library Modules
import ed_glob
import ed_menu
import syntax.syntax
import util
from profiler import Profile_Get, Profile_Set
from eclib import platebtn

# Local Imports
import FileInfo

#-----------------------------------------------------------------------------#
# Globals
PANE_NAME = u'FileBrowser'
ID_BROWSERPANE = wx.NewId()
ID_FILEBROWSE = wx.NewId()

# Configure Platform specific commands
if wx.Platform == '__WXMAC__': # MAC
    FILEMAN = 'Finder'
    FILEMAN_CMD = 'open'
    TRASH = 'Trash'
    DIFF_CMD = 'opendiff'
elif wx.Platform == '__WXMSW__': # Windows
    FILEMAN = 'Explorer'
    FILEMAN_CMD = 'explorer'
    TRASH = 'Recycle Bin'
    DIFF_CMD = None
else: # Other/Linux
    # TODO how to check what desktop environment is in use
    # this will work for Gnome but not KDE
    FILEMAN = 'Nautilus'
    FILEMAN_CMD = 'nautilus'
    TRASH = 'Trash'
    DIFF_CMD = None
    #FILEMAN = 'Konqueror'
    #FILEMAN_CMD = 'konqueror'

_ = wx.GetTranslation
#-----------------------------------------------------------------------------#

class BrowserMenuBar(wx.Panel):
    """Creates a menubar with """
    ID_MARK_PATH = wx.NewId()
    ID_OPEN_MARK = wx.NewId()
    ID_REMOVE_MARK = wx.NewId()

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER)

        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_ADD_BM), wx.ART_MENU)
        menub = platebtn.PlateButton(self, bmp=bmp,
                                     style=platebtn.PB_STYLE_NOBG)
        tt = wx.ToolTip(_("Pathmarks"))
        menub.SetToolTip(tt)
        menu = ed_menu.EdMenu()

        # Attributes
        self._saved = ed_menu.EdMenu()
        self._rmpath = ed_menu.EdMenu()
        self._ids = list()  # List of ids of menu items
        self._rids = list() # List of remove menu item ids

        key = u'Ctrl'
        if wx.Platform == '__WXMAC__':
            key = u'Cmd'

        tt = wx.ToolTip(_("To open multiple files at once %s+Click to select "
                          "the desired files/folders then hit Enter to open "
                          "them all at once") % key)
        self.SetToolTip(tt)

        # Build Menus
        menu.Append(self.ID_MARK_PATH, _("Save Selected Paths"))
        menu.AppendMenu(self.ID_OPEN_MARK, 
                        _("Jump to Saved Path"), self._saved)
        menu.AppendSeparator()
        menu.AppendMenu(self.ID_REMOVE_MARK, 
                        _("Remove Saved Path"), self._rmpath)
        menub.SetMenu(menu)

        # Layout bar
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((1, 1))
        men_sz = wx.BoxSizer(wx.HORIZONTAL)
        men_sz.Add((6, 6))
        men_sz.Add(menub, 0, wx.ALIGN_LEFT)
        sizer.Add(men_sz)
        sizer.Add((1, 1))
        self.SetSizer(sizer)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, lambda evt: menub.ShowMenu(), menub)
        # Due to transparency issues dont do painting on gtk
        if wx.Platform != '__WXGTK__':
            self.Bind(wx.EVT_PAINT, self.OnPaint)

    # XXX maybe change to list the more recently added items near the top
    def AddItem(self, label):
        """Add an item to the saved list, this also adds an identical 
        entry to the remove list so it can be removed if need be.

        """
        save_id = wx.NewId()
        self._ids.append(save_id)
        rem_id = wx.NewId()
        self._rids.append(rem_id)
        self._saved.Append(save_id, label)
        self._rmpath.Append(rem_id, label)

    def GetOpenIds(self):
        """Returns the ordered list of menu item ids"""
        return self._ids

    def GetRemoveIds(self):
        """Returns the ordered list of remove menu item ids"""
        return self._rids

    def GetItemText(self, item_id):
        """Retrieves the text label of the given item"""
        item = self.GetSavedMenu().FindItemById(item_id)
        if not item:
            item = self.GetRemoveMenu().FindItemById(item_id)

        if item:
            return item.GetLabel()
        else:
            return u''

    def GetRemoveMenu(self):
        """Returns the remove menu"""
        return self._rmpath

    def GetSavedMenu(self):
        """Returns the menu containg the saved items"""
        return self._saved

    def OnPaint(self, evt):
        """Paints the background of the menubar"""
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        col1 = util.AdjustColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE), -15)
        col2 = util.AdjustColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE), 40)
        rect = self.GetRect()
        grad = gc.CreateLinearGradientBrush(0, 1, 0, rect.height, col2, col1)

        # Create the background path
        path = gc.CreatePath()
        path.AddRectangle(0, 0, rect.width - 0.5, rect.height - 0.5)

        gc.SetPen(wx.Pen(util.AdjustColour(col1, -20), 1))
        gc.SetBrush(grad)
        gc.DrawPath(path)

        evt.Skip()

    def RemoveItemById(self, path_id):
        """Removes a given menu item from both the saved
        and removed lists using the id as a lookup.

        """
        o_ids = self.GetOpenIds()
        r_ids = self.GetRemoveIds()

        if path_id in r_ids:
            index = r_ids.index(path_id)
            self.GetRemoveMenu().Remove(path_id)
            self.GetSavedMenu().Remove(o_ids[index])
            self._rids.remove(path_id)
            del self._ids[index]

#-----------------------------------------------------------------------------#

class BrowserPane(wx.Panel):
    """Creates a filebrowser Pane"""
    ID_SHOW_HIDDEN = wx.NewId()

    def __init__(self, parent, id, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER):
        wx.Panel.__init__(self, parent, id, pos, size, style)
        
        # Attributes
        self._mw = parent
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        filters = "".join(syntax.syntax.GenFileFilters())
        self._menbar = BrowserMenuBar(self)
        self._browser = FileBrowser(self, ID_FILEBROWSE, 
                                    dir=wx.GetHomeDir(), 
                                    size=(200, -1),
                                    style=wx.DIRCTRL_SHOW_FILTERS | wx.BORDER_SUNKEN,
                                    filter=filters)
        self._config = PathMarkConfig(ed_glob.CONFIG['CACHE_DIR'])
        for item in self._config.GetItemLabels():
            self._menbar.AddItem(item)
        self._showh_cb = wx.CheckBox(self, self.ID_SHOW_HIDDEN, 
                                     _("Show Hidden Files"))
        self._showh_cb.SetValue(False)
        if wx.Platform == '__WXMAC__':
            self._showh_cb.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

        #---- Add Menu Items ----#
        viewm = self._mw.GetMenuBar().GetMenuByName("view")
        self._mi = viewm.InsertAlpha(ID_FILEBROWSE, _("File Browser"), 
                                     _("Open File Browser Sidepanel"),
                                     wx.ITEM_CHECK,
                                     after=ed_glob.ID_PRE_MARK)

        # Layout Pane
        self._sizer.AddMany([(self._menbar, 0, wx.EXPAND),
                             (self._browser, 1, wx.EXPAND),
                             ((2, 2))])
        cb_sz = wx.BoxSizer(wx.HORIZONTAL)
        cb_sz.Add((4, 4))
        cb_sz.Add(self._showh_cb, 0, wx.ALIGN_LEFT)
        self._sizer.Add(cb_sz, 0, wx.ALIGN_LEFT)
        self._sizer.Add((3, 3))
        self.SetSizer(self._sizer)

        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.Bind(wx.EVT_MENU, self.OnMenu)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        viewm.Bind(wx.EVT_MENU_OPEN, self.UpdateMenuItem)

    def __del__(self):
        """Save the config before we get destroyed"""
        self._config.Save()

    def OnCheck(self, evt):
        """Toggles visibility of hidden files on and off"""
        e_id = evt.GetId()
        if e_id == self.ID_SHOW_HIDDEN:
            style = self._browser.GetTreeStyle()
            self._browser.SetTreeStyle(wx.TR_SINGLE)
            self._browser.Refresh()
            self._browser.ShowHidden(self._showh_cb.GetValue())
            self._browser.SetTreeStyle(style)
            self._browser.Refresh()
        else:
            evt.Skip()

    # TODO after a jump the window should be properly rescrolled
    #      to have the jumped-to path at the top when possible
    def OnMenu(self, evt):
        """Handles the events associated with adding, opening,
        and removing paths in the menubars menus.

        """
        e_id = evt.GetId()
        o_ids = self._menbar.GetOpenIds()
        d_ids = self._menbar.GetRemoveIds()
        if e_id == self._menbar.ID_MARK_PATH:
            items = self._browser.GetPaths()
            for item in items:
                self._menbar.AddItem(item)
                self._config.AddPathMark(item, item)
                self._config.Save()
        elif e_id in o_ids:
            pmark = self._menbar.GetItemText(e_id)
            path = self._config.GetPath(pmark)
            self._browser.ExpandPath(path)
            self._browser.SetFocus()
        elif e_id in d_ids:
            plabel = self._menbar.GetItemText(e_id)
            self._menbar.RemoveItemById(e_id)
            self._config.RemovePathMark(plabel)
            self._config.Save()
        else:
            evt.Skip()

    def OnPaint(self, evt):
        """Paints the background of the panel"""
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        col1 = util.AdjustColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE), -15)
        col2 = util.AdjustColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE), 40)
        rect = self.GetRect()
        x = 0
        y = rect.height - (self._showh_cb.GetSize()[1] + 6)
        grad = gc.CreateLinearGradientBrush(x, y, x, 
                                            y + self._showh_cb.GetSize()[1] + 6,
                                            col2, col1)

        # Create the background path
        path = gc.CreatePath()
        path.AddRectangle(x, y, rect.width - 0.5, 
                          self._showh_cb.GetSize()[1] + 6)

        gc.SetPen(wx.Pen(util.AdjustColour(col1, -20), 1))
        gc.SetBrush(grad)
        gc.DrawPath(path)

        evt.Skip()

    def OnShowBrowser(self, evt):
        """Shows the filebrowser"""
        if evt.GetId() == ID_FILEBROWSE:
            mgr = self._mw.GetFrameManager()
            pane = mgr.GetPane(PANE_NAME)
            if pane.IsShown():
                pane.Hide()
                Profile_Set('SHOW_FB', False)
            else:
                pane.Show()
                Profile_Set('SHOW_FB', True)
            mgr.Update()
        else:
            evt.Skip()

    def UpdateMenuItem(self, evt):
        """Update the check mark for the menu item"""
        mgr = self._mw.GetFrameManager()
        pane = mgr.GetPane(PANE_NAME)
        if pane.IsShown():
            self._mi.Check(True)
        else:
            self._mi.Check(False)
        evt.Skip()

#-----------------------------------------------------------------------------#
# Menu Id's
ID_EDIT = wx.NewId()
ID_OPEN = wx.NewId()
ID_REVEAL = wx.NewId()
ID_GETINFO = wx.NewId()
ID_NEW_FOLDER = wx.NewId()
ID_NEW_FILE = wx.NewId()
ID_DELETE = wx.NewId()
ID_DUPLICATE = wx.NewId()
ID_ARCHIVE = wx.NewId()
ARCHIVE_LBL = "Create Archive of \"%s\""

class FileBrowser(wx.GenericDirCtrl):
    """A hack job done to make the genericdirctrl more useful
    and work with Editra's art provider.
    @todo: write my own dirctrl

    """
    def __init__(self, parent, id, dir=u'', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DIRCTRL_SHOW_FILTERS,
                 filter=wx.EmptyString, defaultFilter=0):
        wx.GenericDirCtrl.__init__(self, parent, id, dir, pos, 
                                   size, style, filter, defaultFilter)

        # Attributes
        self._tree = self.GetTreeCtrl()
        self._treeId = 0                # id of TreeItem that was last rclicked
        self._fmenu = self._MakeMenu()
        
        # Set custom styles
        self._tree.SetWindowStyle(self._tree.GetWindowStyle() | wx.TR_MULTIPLE)
        self._tree.Refresh()

        # HACK if the GenericDirCtrl ever changes the order of the images used 
        #      in it this will have to be updated accordingly
        if Profile_Get('ICONS', 'str', 'default').lower() != u'default':
            bmp1 = wx.ArtProvider.GetBitmap(str(ed_glob.ID_FOLDER), wx.ART_MENU)
            fbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU)
            self._imglst = self._tree.GetImageList()
            ids = [ed_glob.ID_FOLDER, ed_glob.ID_OPEN, ed_glob.ID_COMPUTER, 
                   ed_glob.ID_HARDDISK, ed_glob.ID_CDROM, ed_glob.ID_FLOPPY, 
                   ed_glob.ID_USB, ed_glob.ID_FILE, ed_glob.ID_BIN_FILE]

            for art in ids:
                bmp = wx.ArtProvider.GetBitmap(str(art), wx.ART_MENU)
                if bmp.IsOk():
                    self._imglst.Replace(ids.index(art), bmp)

        # Event Handlers
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnOpen)
        if wx.Platform == '__WXMSW__':
            self._tree.Bind(wx.EVT_KEY_UP, self.OnOpen)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContext)
        self.Bind(wx.EVT_MENU, self.OnMenu)
#         self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnDragStart)
#         self.Bind(wx.EVT_TREE_END_DRAG, self.OnDragEnd)

    def _MakeMenu(self):
        """Setup the context menu"""
        menu = wx.Menu()

        # MenuItems
        items = [(ID_EDIT, _("Edit"), None),
                 (ID_OPEN, _("Open with " + FILEMAN), ed_glob.ID_OPEN),
                 (ID_REVEAL, _("Reveal in " + FILEMAN), None),
                 (ID_GETINFO, _("Get Info"), None),
                 (wx.ID_SEPARATOR, '', None),
                 (ID_NEW_FOLDER, _("New Folder"), ed_glob.ID_FOLDER),
                 (ID_NEW_FILE, _("New File"), ed_glob.ID_NEW),
                 (wx.ID_SEPARATOR, '', None),
                 (ID_DELETE, _("Move to " + TRASH), ed_glob.ID_DELETE),
                 (wx.ID_SEPARATOR, '', None),
                 (ID_DUPLICATE, _("Duplicate"), None),
                 (ID_ARCHIVE, _(ARCHIVE_LBL) % '', None)
                ]

        for item in items:
            mitem = wx.MenuItem(menu, item[0], item[1])
            if item[2] is not None:
                bmp = wx.ArtProvider.GetBitmap(str(item[2]), wx.ART_MENU)
                mitem.SetBitmap(bmp)

            menu.AppendItem(mitem)
        return menu

    def _SCommand(self, cmd, *args):
        """Run a tree command that requires de-hacking the windows style
        before running. (Some commands raise errors on msw if the style is
        not set back to TR_SINGLE before calling it.
        @param cmd: self.METHOD
        @keyword args: args to pass to command

        """
        style = self.GetTreeStyle()
        self.SetTreeStyle(wx.TR_SINGLE)
        self.Refresh()
        cmd(*args)
        self.SetTreeStyle(style)
        self.Refresh()

    def GetItemPath(self, itemId):
        """Get and return the path of the given item id
        @param itemId: TreeItemId
        @return: string

        """
        root = self._tree.GetRootItem()
        start = itemId
        atoms = [itemId]
        while self._tree.GetItemParent(start) != root:
            atoms.append(self._tree.GetItemParent(start))
            start = atoms[-1]

        atoms.reverse()
        path = list()
        for atom in atoms:
            path.append(self._tree.GetItemText(atom))

        if wx.Platform == '__WXMSW__':
            r_txt = u''
        else:
            if wx.Platform == '__WXGTK__':
                if path[0].lower() == 'home directory':
                    path[0] = wx.GetHomeDir()
                elif path[0].lower() == 'desktop':
                    path.insert(0, wx.GetHomeDir())
                else:
                    pass

            if wx.Platform == '__WXMAC__':
                if path[0] != "/":
                    path.pop(0)
            r_txt = os.path.sep
        return r_txt + util.GetPathChar().join(path)

    def GetPaths(self):
        """Gets a list of abs paths of the selected items"""
        treeIds = self._tree.GetSelections()
        root = self._tree.GetRootItem()
        ret_val = list()
        for leaf in treeIds:
            ret_val.append(self.GetItemPath(leaf))
        return ret_val

    def GetScrollRange(self, orient=wx.VERTICAL):
        """Returns the scroll range of the tree control"""
        return self._tree.GetScrollRange(orient)

    def GetTreeStyle(self):
        """Returns the trees current style"""
        return self._tree.GetWindowStyle()

    def OnContext(self, evt):
        """Show the popup context menu"""
        self._treeId = evt.GetItem()
        path = self.GetItemPath(self._treeId)
        mitem = self._fmenu.FindItemById(ID_ARCHIVE)
        if mitem != wx.NOT_FOUND:
            mitem.SetItemLabel(_(ARCHIVE_LBL) % path.split(os.path.sep)[-1])

        for item in (ID_DUPLICATE,):
            self._fmenu.Enable(item, len(self._tree.GetSelections()) == 1)
        self.PopupMenu(self._fmenu)

    def OnMenu(self, evt):
        """Handle the context menu events for performing
        filesystem operations

        """
        e_id = evt.GetId()
        path = self.GetItemPath(self._treeId)
        paths = self.GetPaths()
        ok = (False, '')
        if e_id == ID_EDIT:
            self.OpenFiles(paths)
        elif e_id == ID_OPEN:
            worker = OpenerThread(paths)
            worker.start()
        elif e_id == ID_REVEAL:
            worker = OpenerThread([os.path.dirname(fname) for fname in paths])
            worker.start()
        elif e_id == ID_GETINFO:
            last = None
            for fname in paths:
                info = FileInfo.FileInfoDlg(self.GetTopLevelParent(), fname)
                if last is None:
                    info.CenterOnParent()
                else:
                    lpos = last.GetPosition()
                    info.SetPosition((lpos[0] + 14, lpos[1] + 14))
                info.Show()
                last = info
        elif e_id == ID_NEW_FOLDER:
            ok = util.MakeNewFolder(path, _("Untitled_Folder"))
        elif e_id == ID_NEW_FILE:
            ok = util.MakeNewFile(path, _("Untitled_File") + ".txt")
        elif e_id == ID_DELETE:
            print "DELETE"
        elif e_id == ID_DUPLICATE:
            for fname in paths:
                ok = DuplicatePath(fname)
        elif e_id == ID_ARCHIVE:
            ok = MakeArchive(path)
        else:
            evt.Skip()
            return

        if e_id in (ID_NEW_FOLDER, ID_NEW_FILE, ID_DUPLICATE, ID_ARCHIVE):
            if ok[0]:
                self.ReCreateTree()
                self._SCommand(self.SetPath, ok[1])

    def OnOpen(self, evt):
        """Handles item activations events. (i.e double clicked or 
        enter is hit) and passes the clicked on file to be opened in 
        the notebook.

        """
        files = self.GetPaths()
        if wx.Platform == '__WXMSW__':
            key = evt.GetKeyCode()
            if len(files) == 1 and stat.S_ISDIR(os.stat(files[0])[0]):
                evt.Skip()
                if key == wx.WXK_RETURN:
                    self.ExpandPath(files[0])
                return

        self.OpenFiles(files)

    def OpenFiles(self, files):
        """Open the list of files in Editra for editing
        @param files: list of file names

        """
        to_open = list()
        for fname in files:
            try:
                res = os.stat(fname)[0]
                if stat.S_ISREG(res) or stat.S_ISDIR(res):
                    to_open.append(fname)
            except (IOError, OSError), msg:
                util.Log("[filebrowser][err] %s" % str(msg))

        win = wx.GetApp().GetActiveWindow()
        if win:
            win.nb.OnDrop(to_open)

      # TODO implement drag and drop from the control to the editor
#     def OnDragEnd(self, evt):
#         evt.Skip()

#     def OnDragStart(self, evt):
#         print evt.GetLabel()
#         evt.Skip()

#     def SelectPath(self, path):
#         """Selects the given path"""
#         parts = path.split(os.path.sep)
#         root = self._tree.GetRootItem()
#         rtxt = self._tree.GetItemText(root)
#         item, cookie = self._tree.GetFirstChild(root)
#         while item:
#             if self._tree.ItemHasChildren(item):
#                 i_txt = self._tree.GetItemText(item)
#                 print i_txt
#                 item, cookie = self._tree.GetFirstChild(item)
#                 continue
#             else:
#                 i_txt = self._tree.GetItemText(item)
#                 print i_txt
#             item, cookie = self._tree.GetNextChild(item, cookie)

    def SetTreeStyle(self, style):
        """Sets the style of directory controls tree"""
        self._tree.SetWindowStyle(style)

#-----------------------------------------------------------------------------#

class PathMarkConfig(object):
    """Manages the saving of pathmarks to make them usable from
    one session to the next.

    """
    CONFIG_FILE = u'pathmarks'

    def __init__(self, pname):
        """Creates the config object, the pname parameter
        is the base path to store the config file at on write.

        """
        object.__init__(self)

        # Attributes
        self._base = os.path.join(pname, self.CONFIG_FILE)
        self._pmarks = dict()

        self.Load()

    def AddPathMark(self, label, path):
        """Adds a label and a path to the config"""
        self._pmarks[label.strip()] = path.strip()

    def GetItemLabels(self):
        """Returns a list of all the item labels in the config"""
        return self._pmarks.keys()

    def GetPath(self, label):
        """Returns the path associated with a given label"""
        return self._pmarks.get(label, u'')

    def Load(self):
        """Loads the configuration data into the dictionary"""
        file_h = util.GetFileReader(self._base)
        if file_h != -1:
            lines = file_h.readlines()
            file_h.close()
        else:
            return False

        for line in lines:
            vals = line.strip().split(u"=")
            if len(vals) != 2:
                continue
            if os.path.exists(vals[1]):
                self.AddPathMark(vals[0], vals[1])
        return True

    def RemovePathMark(self, pmark):
        """Removes a path mark from the config"""
        if self._pmarks.has_key(pmark):
            del self._pmarks[pmark]

    def Save(self):
        """Writes the config out to disk"""
        file_h = util.GetFileWriter(self._base)
        if file_h == -1:
            return False

        for label in self._pmarks:
            file_h.write(u"%s=%s\n" % (label, self._pmarks[label]))
        file_h.close()
        return True

#-----------------------------------------------------------------------------#
# Utilities
def DuplicatePath(path):
    """Create a copy of the item at the end of the given path. The item
    will be created with a name in the form of Dirname_Copy for directories
    and FileName_Copy.extension for files.
    @param path: path to duplicate
    @return: Tuple of (success?, filename OR Error Message)

    """
    head, tail = os.path.split(path)
    if os.path.isdir(path):
        name = util.GetUniqueName(head, tail + "_Copy")
        copy = shutil.copytree
    else:
        tmp = [ part for part in tail.split('.') if len(part) ]
        if tail.startswith('.'):
            tmp[0] = "." + tmp[0]
            if '.' not in tail[1:]:
                tmp[0] = tmp[0] + "_Copy"
            else:
                tmp.insert(-1, "_Copy.")

            tmp = ''.join(tmp)
        else:
            tmp = '.'.join(tmp[:-1]) + "_Copy." + tmp[-1]

        if len(tmp) > 1:
            name = util.GetUniqueName(head, tmp)
        copy = shutil.copy2

    try:
        copy(path, name)
    except Exception, msg:
        return (False, str(msg))

    return (True, name)

def MakeArchive(path):
    """Create a Zip archive of the item at the end of the given path
    @param path: full path to item to archive
    @return: Tuple of (success?, file name OR Error Message)
    @rtype: (bool, str)
    @todo: support for zipping multiple paths

    """
    dname, fname = os.path.split(path)
    ok = True
    name = ''
    if dname and fname:
        name = util.GetUniqueName(dname, fname + ".zip")
        files = list()
        cwd = os.getcwd()
        head = dname
        try:
            try:
                os.chdir(dname)
                if os.path.isdir(path):
                    for dpath, dname, fnames in os.walk(path):
                        files.extend([ os.path.join(dpath, fname).\
                                       replace(head, '', 1).\
                                       lstrip(os.path.sep) 
                                       for fname in fnames])

                zfile = zipfile.ZipFile(name, 'w', compression=zipfile.ZIP_DEFLATED)
                for fname in files:
                    zfile.write(fname.encode(sys.getfilesystemencoding()))
            except Exception, msg:
                ok = False
                name = str(msg)
        finally:
            zfile.close()
            os.chdir(cwd)

    return (ok, name)

#-----------------------------------------------------------------------------#
class OpenerThread(threading.Thread):
    """Job runner thread for opening files with the systems filemanager"""
    def __init__(self, files):
        self._files = files
        threading.Thread.__init__(self)

    def run(self):
        """Do the work of opeing the files"""
        for fname in self._files:
            subprocess.call([FILEMAN_CMD, fname])
