###############################################################################
# Name: plugdlg.py                                                            #
# Purpose: User interface into the PluginManager, also provides interface for #
#          downloading and installing plugins.                                #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Provides a dialog for downloading, installing and configuring plugins or Editra.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import re
import urllib2
import wx
import wx.lib.delayedresult as delayedresult

# Local Imports
import ed_glob
import plugin
import ed_event
import util
import ed_txt
from profiler import Profile_Get, Profile_Set
import eclib

#-----------------------------------------------------------------------------#
# Globals

CONFIG_PG = 0
DOWNLOAD_PG = 1
INSTALL_PG = 2
PY_VER = str(sys.version_info[0]) + str(sys.version_info[1])
PLUGIN_REPO = "http://editra.org/plugins.php?list=True&py=" + PY_VER

_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

def MakeThemeTool(tool_id):
    """Makes a themed bitmap for the tool book of the plugin dialog.
    @param tool_id: An art identifier id
    @return: 32x32 bitmap
    @todo: why does drawing a bitmap overlay on gtk not draw on transparent area

    """
    osize = Profile_Get('ICON_SZ', default=(24, 24))
    Profile_Set('ICON_SZ', (32, 32))
    base = wx.ArtProvider.GetBitmap(str(tool_id), wx.ART_TOOLBAR)
    Profile_Set('ICON_SZ', osize)
    if not base.IsOk():
        base = wx.ArtProvider.GetBitmap(wx.ART_WARNING,
                                        wx.ART_TOOLBAR,
                                        size=(32, 32))

    over = wx.ArtProvider.GetBitmap(str(ed_glob.ID_PLUGMGR), wx.ART_MENU)
    if over.IsOk():
        # Draw overlay onto button
        mdc = wx.MemoryDC()
        mdc.SelectObject(base)
        mdc.SetBrush(wx.TRANSPARENT_BRUSH)
        mdc.SetPen(wx.TRANSPARENT_PEN)
        mdc.DrawBitmap(over, 15, 15, False)
        mdc.SelectObject(wx.NullBitmap)

    return base

#-----------------------------------------------------------------------------#

class PluginDialog(wx.Frame):
    """Defines a Plugin manager Dialog that can be used to download plugins
    from a defined repository, offers services to install plugins that
    where downloaded with or without the dialog, as well as configure
    already installed plugins. It is instanciated as a standalone window
    when the show method is called so that if downloads are taking along time
    it does not interfere with usage of the editor.

    """
    def __init__(self, parent, id=wx.ID_ANY, title=u'', size=wx.DefaultSize):
        wx.Frame.__init__(self, parent, title=title, size=size,
                              style=wx.DEFAULT_FRAME_STYLE)
        util.SetWindowIcon(self)

        # Attributes
        bstyle = eclib.SEGBOOK_STYLE_NO_DIVIDERS|eclib.SEGBOOK_STYLE_LABELS
        self._nb = eclib.SegmentBook(self, style=bstyle)
        self._cfg_pg = ConfigPanel(self._nb, style=wx.BORDER_SUNKEN)
        self._dl_pg = DownloadPanel(self._nb)
        self._inst_pg = InstallPanel(self._nb)
        self._imglst = list()

        # Setup
        self._imglst.append(MakeThemeTool(ed_glob.ID_PREF))
        self._imglst.append(MakeThemeTool(ed_glob.ID_WEB))
        self._imglst.append(MakeThemeTool(ed_glob.ID_PACKAGE))
        self._nb.SetImageList(self._imglst)
        self._nb.SetUsePyImageList(True)

        self._nb.AddPage(self._cfg_pg, _("Configure"), img_id=0)
        self._nb.AddPage(self._dl_pg, _("Download"), img_id=1)
        self._nb.AddPage(self._inst_pg, _("Install"), img_id=2)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._nb, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetStatusBar(eclib.ProgressStatusBar(self, style=wx.SB_FLAT))
        self.SetInitialSize(size)

        # Event Handlers
        self.Bind(eclib.EVT_SB_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, evt):
        """Handles closing the dialog and unregistering it from
        the mainloop.
        @param evt: Event fired that called this handler
        @type evt: wx.EVT_CLOSE

        """
        if self._dl_pg.IsDownloading():
            dlg = wx.MessageDialog(self, _("Downloads are incomplete"),
                                   _("Do you wish to exit?"),
                                   style=wx.YES_NO|wx.ICON_EXCLAMATION| \
                                           wx.CENTER)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_NO:
                return
            else:
                pass

        wx.GetApp().UnRegisterWindow(repr(self))
        evt.Skip()

    def Show(self, show=True):
        """Shows the dialog
        @postcondition: Dialog is registered with the main loop and shown

        """
        wx.GetApp().RegisterWindow(repr(self), self, True)
        wx.Frame.Show(self, show)

    def Busy(self, busy=True):
        """Set the status of the frame to be busy or not
        @keyword busy: Start or Stop being busy

        """
        if busy:
            self.GetStatusBar().StartBusy()
        else:
            self.GetStatusBar().StopBusy()

    def OnPageChanging(self, evt):
        """Updates pages as they are being changed to.
        @param evt: Event fired that called this handler
        @type evt: segmentbk.EVT_SB_PAGE_CHANGING

        """
        cur_pg = evt.GetSelection()
        self.SetTitle(self.GetTitle().split(" | ")[0] + \
                      " | " + self._nb.GetPageText(cur_pg))
        if cur_pg == CONFIG_PG:
            self._cfg_pg.PopulateCtrl()
            self.SetStatusText(_("Changes will take affect once the"
                                 " program has been restarted"), 0)
        elif cur_pg == DOWNLOAD_PG:
            self._dl_pg.UpdateList()
        elif cur_pg == INSTALL_PG:
            pass
        else:
            pass

        evt.Skip()

#-----------------------------------------------------------------------------#

class ConfigPanel(wx.Panel):
    """Creates a panel for configuring plugins."""
    def __init__(self, parent, style=wx.SUNKEN_BORDER):
        """Build config panel"""
        wx.Panel.__init__(self, parent, style=style)

        # Attrtibutes
        self._list = eclib.PanelBox(self)

        # Layout Panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._list, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.PopulateCtrl()

        # Event handlers
        self.Bind(ed_event.EVT_NOTIFY, self.OnNotify)

    def GetItemIdentifier(self, name):
        """Gets the named item and returns its identifier. The
        identifier is the combination of the name and version
        strings.
        @param name: name of item in list
        @type name: string
        @return: identifier for the named list item

        """
        identifer = None
        for item in self._list.GetItems():
            if item.GetPluginName().lower() == name.lower():
                identifer = (name, item.GetVersionString())
        return identifer

    @staticmethod
    def OnNotify(evt):
        """Handles the notification events that are
        posted from the list control.
        @param evt: Event fired that called this handler
        @type evt: ed_event.NotificationEvent

        """
        index = evt.GetId()
        enable, pname = evt.GetValue()
        pmgr = wx.GetApp().GetPluginManager()
        pmgr.EnablePlugin(pname, enable)

    def PopulateCtrl(self):
        """Populates the list of plugins and sets the
        values of their states. Any successive calls to
        this function will clear the list and Repopulate it
        with current config values. Returns the number of
        items populated to the list
        @postcondition: list is popluated with all plugins that are
                        currently loaded and sets the checkmarks accordingly
        @return: number of items added to list

        """
        p_mgr = wx.GetApp().GetPluginManager()
        if self._list.GetItemCount():
            self._list.DeleteAllItems()

        p_mgr = wx.GetApp().GetPluginManager()
        p_mgr.ReInit()
        config = p_mgr.GetConfig()
        keys = sorted([ ed_txt.DecodeString(name)
                        for name in config.keys() ],
                      key=unicode.lower)
        for item in keys:
            val = config[item]
            self._list.Freeze()
            mod = sys.modules.get(item)
            pin = PluginData()
            pin.SetName(item)
            pin.SetDescription(getattr(mod, '__doc__',
                                       _("No Description Available")))
            pin.SetAuthor(getattr(mod, '__author__', _("Unknown")))
            pin.SetVersion(str(getattr(mod, '__version__', _("Unknown"))))

            pbi = PBPluginItem(self._list, None, item, pin.GetVersion(),
                               pin.GetDescription(), pin.GetAuthor())

            pbi.SetChecked(val)
            self._list.AppendItem(pbi)
            self._list.Thaw()

        self._list.SendSizeEvent()
        return self._list.GetItemCount()

#-----------------------------------------------------------------------------#

class DownloadPanel(eclib.ControlBox):
    """Creates a panel with controls for downloading plugins."""
    ID_DOWNLOAD = wx.NewId()
    EGG_PATTERN = re.compile(r"(?P<name>[^-]+)"
    r"( -(?P<ver>[^-]+) (-py(?P<pyver>[^-]+) (-(?P<plat>.+))? )? )?",
    re.VERBOSE | re.IGNORECASE
    ).match

    def __init__(self, parent, style=wx.NO_BORDER):
        """Initializes the panel"""
        eclib.ControlBox.__init__(self, parent, style=style)

        # Attributes
        self._p_list = dict()           # list of available plugins/meta
        self._dl_list = dict()          # List of download urls
        self._eggcount = 0              # Number of plugins to download
        self._eggbasket = dict()        # Basket of downloaded eggs
        self._list = eclib.PanelBox(self)

        # Layout Panel
        self.CreateControlBar(wx.BOTTOM)
        cbar = self.GetControlBar(wx.BOTTOM)
        cbar.SetVMargin(1, 2)
        cbar.AddStretchSpacer()
        self._downlb = wx.Button(cbar, DownloadPanel.ID_DOWNLOAD, _("Download"))
        self._downlb.Disable()
        cbar.AddControl(self._downlb, wx.ALIGN_RIGHT)
        self.SetWindow(self._list)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(ed_event.EVT_NOTIFY, self.OnNotify)

    def _ResultCatcher(self, delayedResult):
        """Catches the results from the download worker threads"""
        # Check if result has come after the window is dead
        try:
            frame = self.GetGrandParent()
        except wx.PyDeadObjectError:
            return

        self._eggcount = self._eggcount - 1
        try:
            result = delayedResult.get()
            plug = result[0]
            if result[1]:
                self._eggbasket[plug] = result[2]
                frame.SetStatusText(_("Downloaded") + ": " + plug, 0)
        finally:
            if not self._eggcount:
                frame.SetStatusText(_("Finshed downloading plugins"), 0)
                wx.CallAfter(frame.Busy, False)
                inst_pg = self.GetParent().GetPage(INSTALL_PG)
                for key in self._eggbasket:
                    inst_pg.AddItemToInstall(key)
                self.GetParent().SetSelection(INSTALL_PG)

    def _UpdateCatcher(self, delayedResult):
        """Catches the results from the download worker threads"""
        try:
            frame = self.GetGrandParent()
            result = delayedResult.get()
            if len(result):
                self._p_list = self.FormatPluginList(result)
                self.PopulateList()
                frame.SetStatusText(_("Select plugins to download"), 0)
        except wx.PyDeadObjectError:
            return
        except Exception, msg:
            util.Log("[plugdlg][err] Download failed " + str(msg))
            frame.SetStatusText(_("Unable to retrieve plugin list"), 0)
        wx.CallAfter(frame.Busy, False)

    def FormatPluginList(self, data):
        """Formats a list of plugin data served by the server into
        PluginData objects for usage in the list view.
        @return: PluginData of all available plugins
        @rtype: dict

        """
        plugins = data
        p_list = dict()
        if len(plugins) < 2:
            return p_list

        for meta in plugins:
            data = meta.split("\n")

            if len(data) < 4:
                continue

            tmpdat = PluginData()
            for attr in data:
                tmp = attr.split("=")
                if len(tmp) != 2:
                    continue

                set_map = {'author' : tmpdat.SetAuthor,
                           'version' : tmpdat.SetVersion,
                           'name' : tmpdat.SetName,
                           'description' : tmpdat.SetDescription,
                           'url' : tmpdat.SetUrl}
                funct = set_map.get(tmp[0].lower(), None)
                if funct:
                    funct(ed_txt.DecodeString(tmp[1].strip()))

            if tmpdat.GetName() != u'':
                p_list[ed_txt.DecodeString(tmpdat.GetName())] = tmpdat

        # Remove items that have already been installed
        config_pg = self.GetParent().GetPage(CONFIG_PG)
        to_clean = list()
        for pin in p_list:
            cfg_id = config_pg.GetItemIdentifier(pin.lower())
            if cfg_id is not None and cfg_id[1] >= p_list[pin].GetVersion():
                to_clean.append(pin)

        for item in to_clean:
            del p_list[item]

        return p_list

    def GetDownloadedData(self):
        """Returns the dictionary of downloaded data or an
        empty dictionary if no data has been downloaded.
        @return: set of all successfully downloaded plugins

        """
        return self._eggbasket

    def IsDownloading(self):
        """Returns whether the panel has active download
        threads or not.
        @return: status of downloading
        @rtype: boolean

        """
        if self._eggcount:
            return True
        else:
            return False

    def OnButton(self, evt):
        """Handles the Button Events.
        @param evt: Event that called this handler
        @type evt: wx.EVT_BUTTON

        """
        e_id = evt.GetId()
        if e_id == self.ID_DOWNLOAD:
            urls = list()
            for item in self._dl_list:
                if self._dl_list[item] and item in self._p_list:
                    urls.append(self._p_list[item].GetUrl())
            self._eggcount = len(urls)

            # Start a separate thread to download each selection
            for egg in range(len(urls)):
                self.GetGrandParent().SetStatusText(_("Downloading") + "...", 0)
                self.GetGrandParent().Busy(True)
                delayedresult.startWorker(self._ResultCatcher, _DownloadPlugin,
                                          wargs=(urls[egg]), jobID=egg)
        else:
            evt.Skip()

    def OnNotify(self, evt):
        """Handles the notification events that are posted by the
        list control when items are checked.
        @param evt: Event that called this handler
        @type evt: ed_event.NotificationEvent

        """
        index = evt.GetId()
        enable, pin = evt.GetValue()
        self._dl_list[pin] = enable

        if enable:
            self._downlb.Enable()
        else:
            for item in self._dl_list:
                if self._dl_list[item]:
                    self._downlb.Enable()
                    break
            else:
                self._downlb.Disable()

            if pin in self._dl_list:
                del self._dl_list[pin]

    def PopulateList(self):
        """Populates the list control based off data in the plugin data
        list. The plugin data list is set as a result of calling UpdateList
        it is not recomended to call this directly.

        @return: number of items added to control

        """
        if self._list.GetItemCount():
            self._list.DeleteAllItems()

        pins = sorted([ name for name in self._p_list.keys() ], key=unicode.lower)
        for item in pins:
            data = self._p_list[item]
            pbi = PBDownloadItem(self._list, None, data.GetName(),
                                 data.GetVersion(), data.GetDescription(),
                                 data.GetAuthor())
            self._list.AppendItem(pbi)

        self._list.SendSizeEvent()
        return self._list.GetItemCount()

    def RemoveDownloadedItem(self, item):
        """Remove an item from the download cache
        @param item: Name of item to remove

        """
        # Removed downloaded data
        if item in self._eggbasket:
            del self._eggbasket[item]

        # Remove download entry data
        match = self.EGG_PATTERN(item)
        if match:
            plugin_name = match.group('name').lower()
            if plugin_name in self._dl_list:
                del self._dl_list[plugin_name]

    def UpdateList(self, url=PLUGIN_REPO):
        """Update the list of available downloads
        @param url: url to fetch update list from
        @postcondition: Worker thread is started that will update list when it
                        finishes.

        """
        if self._list.GetItemCount():
            self._list.DeleteAllItems()
        frame =  self.GetGrandParent()
        frame.SetStatusText(_("Retrieving Plugin List") + "...", 0)
        frame.Busy(True)
        delayedresult.startWorker(self._UpdateCatcher, _GetPluginListData,
                                  wkwargs={'url' : url}, jobID='update')

#-----------------------------------------------------------------------------#
# Download utility functions

# The obtained meta data must be served as a file that is formated
# as follows. Each meta data item must be on a single line with
# each set of meta data for different plugins separated by three
# hash marks '###'.
def _GetPluginListData(url=PLUGIN_REPO):
    """Gets the list of plugins and their related meta data
    as a string and returns it.
    @return: list of data of available plugins from website

    """
    text = u''
    try:
        try:
            if Profile_Get('USE_PROXY', default=False):
                proxy_set = Profile_Get('PROXY_SETTINGS',
                                        default=dict(uname='', url='',
                                                     port='80', passwd=''))
                proxy = util.GetProxyOpener(proxy_set)
                h_file = proxy.open(url)
            else:
                h_file = urllib2.urlopen(url)

            text = h_file.read()
            h_file.close()
        except (IOError, OSError), msg:
            util.Log("[plugdlg][err] %s" % str(msg))
    finally:
        return text.split("###")

def _DownloadPlugin(*args):
    """Downloads the plugin at the given url.
    @note: *args is really a string that has been exploded
    @return: name, completed, egg data
    @rtype: tuple

    """
    url = "".join(args)
    egg = None
    try:
        try:
            if Profile_Get('USE_PROXY', default=False):
                proxy_set = Profile_Get('PROXY_SETTINGS',
                                        default=dict(uname='', url='',
                                                     port='80', passwd=''))
                proxy = util.GetProxyOpener(proxy_set)
                h_file = proxy.open(url)
            else:
                h_file = urllib2.urlopen(url)

            egg = h_file.read()
            h_file.close()
        except (IOError, OSError), msg:
            util.Log("[plugdlg][err] %s" % str(msg))
    finally:
        return (url.split("/")[-1], True, egg)

#-----------------------------------------------------------------------------#

class InstallPanel(eclib.ControlBox):
    """Creates a panel for installing plugins."""
    ID_INSTALL = wx.NewId()
    ID_USER = wx.NewId()
    ID_SYS = wx.NewId()
    ID_REMOVE_ITEM = wx.NewId()

    def __init__(self, parent, style=wx.NO_BORDER):
        """Initializes the panel"""
        eclib.ControlBox.__init__(self, parent, style=style)

        # Attributes
        self.CreateControlBar(wx.BOTTOM)
        toolt = wx.ToolTip(_("To add a new item drag and drop the plugin file "
                             "into the list.\n\nTo remove an item select it "
                             "and hit Delete or Backspace."))
        self._install = wx.ListBox(self, wx.ID_ANY,
                                   style=wx.LB_SORT|wx.BORDER_NONE)
        self._install.SetToolTip(toolt)
        self._install.SetDropTarget(util.DropTargetFT(self._install,
                                                      None, self.OnDrop))

        bbar = self.GetControlBar(wx.BOTTOM)
        bbar.SetVMargin(1, 2)
        self._instb = wx.Button(bbar, self.ID_INSTALL, _("Install"))
        self._instb.Disable()
        self._usercb = wx.CheckBox(bbar, self.ID_USER, _("User Directory"))
        self._usercb.SetValue(True)
        toolt = wx.ToolTip(_("Install the plugins only for the current user"))
        self._usercb.SetToolTip(toolt)
        self._syscb = wx.CheckBox(bbar, self.ID_SYS, _("System Directory"))
        toolt = wx.ToolTip(_("Install the plugins for all users\n"
                             " **requires administrative privileges**"))
        self._syscb.SetToolTip(toolt)
        if not os.access(ed_glob.CONFIG['SYS_PLUGIN_DIR'], os.R_OK | os.W_OK):
            self._syscb.Disable()

        # Layout Panel
        self.SetWindow(self._install)
        bbar.AddControl(self._usercb)
        bbar.AddControl(self._syscb)
        bbar.AddStretchSpacer()
        bbar.AddControl(self._instb, wx.ALIGN_RIGHT)
        self.SendSizeEvent()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)
        self._install.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

    def _Install(self):
        """Install the plugins in the list.
        @postcondition: all plugins listed in the list are installed and loaded

        """
        items = self._install.GetItems()
        inst_loc = ed_glob.CONFIG['PLUGIN_DIR']
        if self._syscb.GetValue():
            inst_loc = ed_glob.CONFIG['SYS_PLUGIN_DIR']

        for item in items:
            egg_name = item.split(os.sep)[-1]
            if os.path.isabs(item):
                try:
                    reader = file(item, "rb")
                    egg = reader.read()
                    reader.close()
                except (IOError, SystemError, OSError):
                    continue
            else:
                dl_pg = self.GetParent().GetPage(DOWNLOAD_PG)
                egg = dl_pg.GetDownloadedData().get(item, None)
                if not egg:
                    continue

            try:
                writer = file(inst_loc + egg_name, "wb")
                writer.write(egg)
                writer.close()
            except (IOError, OSError):
                continue
            else:
                # If successfully installed remove from list
                ind = self._install.FindString(item)
                dl_pg = self.GetParent().GetPage(DOWNLOAD_PG)
                if ind != wx.NOT_FOUND:
                    self._install.Delete(ind)
                    dl_pg.RemoveDownloadedItem(item)

        if not len(self._install.GetItems()):
            # All plugins installed correctly
            grand_p = self.GetTopLevelParent()
            grand_p.SetStatusText(_("Successfully Installed Plugins"), 0)
            dlg = wx.MessageDialog(self, _("Go to configuration page?"),
                                   _("Finished Installing Plugins"),
                                   style=wx.YES_NO | wx.CENTER | \
                                         wx.ICON_INFORMATION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
                # Note: need to do this because Setselection doesn't fire a
                #       page change.
                wx.GetApp().GetPluginManager().ReInit()
                self.GetParent().SetSelection(CONFIG_PG)
            self._instb.Disable()
        else:
            self.GetGrandParent().SetStatusText(_("Error"), 1)
            dlg = wx.MessageDialog(self,
                                   _("Failed to install %d plugins") % \
                                   self._install.GetCount(),
                                   _("Installation Error"),
                                   style = wx.OK | wx.CENTER | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def AddItemToInstall(self, item):
        """Adds an item to the install list, the item
        should be a string of the path to the item or
        the items name if it is an in memory file from the
        download page.
        @param item: path or name of plugin item
        @type item: string

        """
        if self._install.FindString(item) == wx.NOT_FOUND:
            self._instb.Enable()
            self._install.Append(item)
        else:
            pass

    def OnButton(self, evt):
        """Handles button events generated by the panel.
        @param evt: Event that called this handler
        @type evt: wx.EVT_BUTTON

        """
        if evt.GetId() == self.ID_INSTALL:
            self._Install()
        else:
            evt.Skip()

    def OnCheckBox(self, evt):
        """Handles the checkbox events to make sure that
        only one of the two check boxes is checked at a time
        @param evt: Event that called this handler
        @type evt: wx.EVT_CHECKBOX

        """
        e_id = evt.GetId()
        val = evt.GetEventObject().GetValue()
        u_cb = self.FindWindowById(self.ID_USER)
        s_cb = self.FindWindowById(self.ID_SYS)
        if e_id == self.ID_USER:
            if not s_cb.IsEnabled():
                u_cb.SetValue(True)
            else:
                s_cb.SetValue(not val)
        elif e_id == self.ID_SYS:
            u_cb.SetValue(not val)
        else:
            pass
        evt.Skip()

    def OnDrop(self, files):
        """Get Drop files and place paths in control
        @status: should also check entry points in addition to filetype
        @param files: list of file paths
        @postcondition: all non egg files are filtered only placing
                        the eggs in the list.
        """
        # Filter out any files that are not eggs
        good = [ fname for fname in files if fname.split(u'.')[-1] == u'egg' ]
        for item in good:
            if self._install.FindString(item) == wx.NOT_FOUND:
                self._install.Append(item)

        if self._install.GetCount():
            self._instb.Enable()

    def OnKeyUp(self, evt):
        """Key Event handler. Removes the selected item from
        the list control when the delete or backspace kis is pressed.
        @param evt: Event that called this handler
        @type evt: wx.KeyEvent(wx.EVT_KEY_UP)

        """
        if evt.GetKeyCode() in [wx.WXK_DELETE, wx.WXK_BACK]:
            item = self._install.GetSelection()
            if item != wx.NOT_FOUND:
                self._install.Delete(item)

            if not self._install.GetCount():
                self._instb.Disable()

        evt.Skip()

#-----------------------------------------------------------------------------#

class PBPluginItem(eclib.PanelBoxItemBase):
    """PanelBox Item to display configuration information about a plugin."""
    def __init__(self, parent, bmp=None, title=u'Plugin Name', version=u'0.0',
                 desc=u'Description', auth='John Doe', enabled=False):
        """Create teh PanelBoxItem
        @param parent: L{PanelBox}

        """
        eclib.PanelBoxItemBase.__init__(self, parent)

        # Attributes
        self._bmp = bmp
        self._title = wx.StaticText(self, label=title)
        self._version = wx.StaticText(self, label=version)
        self._desc = wx.StaticText(self, label=desc)
        self._auth = wx.StaticText(self, label=_("Author: %s") % auth)
        self._enabled = wx.CheckBox(self, label=_("Enable"))
        self._enabled.SetValue(enabled)
        self._config = wx.Button(self, label=_("Configure"))
        self._config.Hide()

        # Setup
        font = self._title.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self._title.SetFont(font)
        self._version.SetFont(font)

        if wx.Platform == '__WXMAC__':
            self._desc.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            self._auth.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            self._enabled.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            self._config.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)

    def __DoLayout(self):
        """Layout the panel"""
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left side Bitmap and Checkbox
        hsizer.Add((5, 5), 0)
        if self._bmp is not None:
            self._bmp = wx.StaticBitmap(self, bitmap=self._bmp)
            hsizer.Add(self._bmp, 0, wx.ALIGN_CENTER_VERTICAL)

        # Central area main content
        csizer = wx.BoxSizer(wx.VERTICAL)
        tsizer = wx.BoxSizer(wx.HORIZONTAL)
        tsizer.AddMany([(self._title, 0), ((20, -1), 1, wx.EXPAND),
                        (self._version, 0, wx.ALIGN_RIGHT)])

        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.AddMany([(self._auth, 0), ((20, -1), 1, wx.EXPAND),
                        (self._enabled, 0, wx.ALIGN_CENTER_VERTICAL),
                        ((5, 5), 0),
                        (self._config, 0, wx.ALIGN_CENTER_VERTICAL)])
        csizer.AddMany([(tsizer, 1, wx.EXPAND), ((3, 3), 0),
                        (self._desc, 0), ((3, 3), 0),
                        (bsizer, 0, wx.EXPAND)])

        # Finish Layout
        hsizer.AddMany([((5, 5), 0), (csizer, 1, wx.EXPAND), ((5, 5), 0)])
        vsizer.AddMany([((4, 4), 0), (hsizer, 0, wx.EXPAND), ((4, 4), 0)])
        self.SetSizer(vsizer)
        self.SetAutoLayout(True)

    def GetPluginName(self):
        """Get the name of the plugin
        @return: string

        """
        return self._title.GetLabel()

    def GetVersionString(self):
        """Get the version of the plugin
        @return: string

        """
        return self._version.GetLabel()

    def OnCheck(self, evt):
        """Notify container of changes to state of plugin"""
        enabled = self._enabled.GetValue()
        pname = self._title.GetLabel()
        event = ed_event.NotificationEvent(ed_event.edEVT_NOTIFY, self.GetId(),
                                           (enabled, pname), self)
        wx.PostEvent(self.GetParent(), event)

    def SetChecked(self, check=True):
        """Set the checkbox
        @param check: bool

        """
        self._enabled.SetValue(check)

#-----------------------------------------------------------------------------#

class PBDownloadItem(PBPluginItem):
    """PanelBox Item to display download information about a plugin."""
    def __init__(self, parent, bmp=None, title=u'Plugin Name', version=u'0.0',
                 desc=u'Description', auth='John Doe'):
        """Create the PanelBoxItem
        @param parent: L{PanelBox}

        """
        PBPluginItem.__init__(self, parent, bmp, title, version, desc, auth)

        # Setup
        self._enabled.SetLabel(_("Download"))
        self.Layout()

#-----------------------------------------------------------------------------#

class PluginData(plugin.PluginData):
    """Plugin Metadata storage class used to store data
    about plugins and where to download them from
    @see: plugin.PluginData

    """
    def __init__(self, name=u'', descript=u'', author=u'', \
                 ver=u'', url=u''):
        """Extends PluginData to include information about url
        to get it from.
        @param url: url to download plugin from

        """
        plugin.PluginData.__init__(self, name, descript, author, ver)
        self._url = url

    def GetUrl(self):
        """Returns the URL of the plugin
        @return: url string of plugins location

        """
        return self._url

    def SetUrl(self, url):
        """Sets the url of the plugin.
        @param url: fully qualified url string

        """
        if not isinstance(url, basestring):
            try:
                url = str(url)
            except (TypeError, ValueError):
                url = u''
        self._url = url

#-----------------------------------------------------------------------------#

