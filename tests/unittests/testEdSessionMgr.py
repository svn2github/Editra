###############################################################################
# Name: testEdSessionMgr.py                                                   #
# Purpose: Unit tests for the session manager class.                          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Unittest cases for testing EdSessionMgr class"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: $"
__revision__ = "$Revision: $"

#-----------------------------------------------------------------------------#
# Imports
import os
import unittest

import common

# Module to test
import ed_session

#-----------------------------------------------------------------------------#
# Test Class

class EdSessionMgrTest(unittest.TestCase):
    def setUp(self):
        self._mgr = ed_session.EdSessionMgr(common.GetTempDir())
        common.CopyToTempDir(common.GetDataFilePath('__default.session'))

    def tearDown(self):
        common.CleanTempDir()

    #---- Tests ----#

    def testGetSavedSessions(self):
        """Test retrieving the list of saved sessions"""
        slist = self._mgr.GetSavedSessions()
        self.assertTrue(isinstance(slist, list))
        self.assertEquals(len(slist), 1)

    def testLoadSession(self):
        """Test loading a serialized session file"""
        dsession = self._mgr.DefaultSession
        rval = self._mgr.LoadSession(dsession)
        self.assertTrue(isinstance(rval, list))
        self.assertEquals(len(rval), 8)

    def testSaveSession(self):
        """Test saving a session file to disk"""
        files = ['foo.py', 'bar.py']
        rval = self._mgr.SaveSession('foobar', files)
        self.assertTrue(rval) # Saved successfully
        loaded = self._mgr.LoadSession('foobar')
        self.assertEquals(len(loaded), 2)
        self.assertTrue('foo.py' in loaded)
        self.assertTrue('bar.py' in loaded)
