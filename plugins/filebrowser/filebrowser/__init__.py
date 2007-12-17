# -*- coding: utf-8 -*-
###############################################################################
# Name: __init__.py                                                           #
# Purpose: FileBrowser Plugin                                                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################
# Plugin Meta
"""Adds a File Browser Sidepanel"""
__author__ = "Cody Precord"
__version__ = "0.6"

#-----------------------------------------------------------------------------#
# Imports
import wx.aui

# Libs from Editra
import iface
import plugin
from profiler import Profile_Get, Profile_Set

# Local imports
import browser

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Interface implementation
class FileBrowserPanel(plugin.Plugin):
    """Adds a filebrowser to the view menu"""
    plugin.Implements(iface.MainWindowI)

    def PlugIt(self, parent):
        """Adds the view menu entry and registers the event handler"""
        self._mw = parent
        self._log = wx.GetApp().GetLog()
        if self._mw != None:
            self._log("[filebrowser] Installing filebrowser plugin")
            
            #---- Create File Browser ----#
            self._filebrowser = browser.BrowserPane(self._mw, 
                                                    browser.ID_BROWSERPANE)
            mgr = self._mw.GetFrameManager()
            mgr.AddPane(self._filebrowser, 
                        wx.aui.AuiPaneInfo().Name(browser.PANE_NAME).\
                            Caption("Editra | File Browser").Left().Layer(1).\
                            CloseButton(True).MaximizeButton(True).\
                            BestSize(wx.Size(215, 350)))

            mgr.Update()

    def GetMenuHandlers(self):
        return [(browser.ID_FILEBROWSE, self._filebrowser.OnShowBrowser)]

    def GetUIHandlers(self):
        return list()
