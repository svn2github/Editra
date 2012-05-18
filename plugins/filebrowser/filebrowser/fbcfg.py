# -*- coding: utf-8 -*-
###############################################################################
# Name: fbcfg.py                                                              #
# Purpose: FileBrowser configuration                                          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2012 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FileBrowser configuration

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Editra libraries
import ed_basewin
from profiler import Profile_Get, Profile_Set

#-----------------------------------------------------------------------------#

_ = wx.GetTranslation

FB_PROF_KEY = "FileBrowser.Config"
FB_SYNC_OPT = "SyncNotebook"
FB_SHF_OPT = "ShowHiddenFiles"

#-----------------------------------------------------------------------------#

class FBConfigDlg(ed_basewin.EdBaseDialog):
    def __init__(self, parent):
        super(FBConfigDlg, self).__init__(parent)

        # Attributes
        self.Panel = FBConfigPanel(self)

#-----------------------------------------------------------------------------#

class FBConfigPanel(wx.Panel):
    def __init__(self, parent):
        super(FBConfigPanel, self).__init__(parent)

        # Attributes
        self._sb = wx.StaticBox(self, label=_("Actions"))
        self._sbs = wx.StaticBoxSizer(self._sb, wx.VERTICAL)
        self._sync_cb = wx.CheckBox(self,
                                    label=_("Synch tree with tab selection"),
                                    name=FB_SYNC_OPT)
        self._vsb = wx.StaticBox(self, label=_("View"))
        self._vsbs = wx.StaticBoxSizer(self._vsb, wx.VERTICAL)
        self._vhf_cb = wx.CheckBox(self,
                                   label=_("Show Hidden Files"),
                                   name=FB_SHF_OPT)

        # Setup
        self.__DoLayout()
        self._sync_cb.Value = GetFBOption(FB_SYNC_OPT, True)
        self._vhf_cb.Value = GetFBOption(FB_SHF_OPT, False)

        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self._sync_cb)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self._vhf_cb)

    def __DoLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self._sbs.Add(self._sync_cb, 0, wx.ALL, 5)
        sizer.Add(self._sbs, 0, wx.ALL, 5)
        self._vsbs.Add(self._vhf_cb, 0, wx.ALL, 5)
        sizer.Add(self._vsbs, 0, wx.ALL, 5)
        self.SetSizer(sizer)

    def OnCheck(self, evt):
        """Update Profile"""
        e_obj = evt.GetEventObject()
        cfgobj = Profile_Get(FB_PROF_KEY, default=dict())
        if e_obj in (self._vhf_cb, self._sync_cb):
            cfgobj[e_obj.Name] = e_obj.Value
            Profile_Set(FB_PROF_KEY, cfgobj)
        else:
            evt.Skip()

#-----------------------------------------------------------------------------#

def GetFBOption(opt, default=None):
    """Get FileBrowser option from the configuration"""
    cfgobj = Profile_Get(FB_PROF_KEY, default=dict())
    return cfgobj.get(opt, default)
