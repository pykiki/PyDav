#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
from os import path as fpath, remove as fremove, stat as fstat
import signal
from PyDav import pydav

__author__ = "Alain Maibach"
__status__ = "Beta tests"

'''
    Python3 PyDav test #1
    Copyright (C) 2017 MAIBACH ALAIN

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Contact: alain.maibach@gmail.com / 34 rue appienne, 13480 Calas - FRANCE.
'''

python3 = sys.version_info.major == 3

curScriptDir = fpath.dirname(fpath.abspath(__file__))
#parentScriptDir = fpath.dirname(fpath.dirname(fpath.abspath(__file__)))
curScriptName = fpath.splitext(fpath.basename(__file__))[0]

if __name__ == "__main__":
  # Webdav global informations part
  rhost = ""
  rlogin = ""
  rpass = ""
  webdav_root = ""

  # Webdav target path
  share = "/public"

  # local download filesystem path
  lpath = "/home/amaibach/Downloads"

  # logging information
  logdst = "console" # other values: syslog | file
  logfilepath = '/var/log/{0}.log'.format(curScriptName)

  # init webdav
  pydav = pydav.core(host=rhost, login=rlogin, passwd=rpass, root=webdav_root, logtype=logdst, logfile=logfilepath, verbosity=False)

  # connection to webdav server
  connected = pydav.connect()
  if connected['code'] == 1:
   del(pydav)
   exit(connected['code'])

  # checking target path exists
  res = pydav.check(share)
  if res['code'] == 1:
   del(pydav)
   exit(res['code'])

  ############################
  # list target path content #
  ############################
  remotefiles = pydav.list(share)

  directories = []
  files = []
  if len(remotefiles) > 0:
    for f in remotefiles:
      if f[-1] == "/" and f != "{0}/".format(share) :
        directories.append(f)
      elif f != "{0}/".format(share):
        files.append(f)

    # if there is directories
    if len(directories) > 0:
      # print theme
      pydav.sendlog(msg="Directories {0}".format(directories))

    # if there is files
    if len(files) > 0:
      # print theme
      pydav.sendlog(msg="Files {0}".format(files))

      ###########################################
      # downloading a file if present in remote #
      ###########################################

      rfilename = 'exemple.txt'

      if rfilename in files:
        rfileloc = "{0}/{1}".format(share, rfilename)
        fileloc = "{0}/{1}".format(lpath, rfilename)
      pydav.sendlog(msg='Downloading {0}'.format(rfilename))
      res = pydav.download(rfileloc, fileloc)
      if res['code'] == 1:
       del(pydav)
       exit(res['code'])
  else:
    pydav.sendlog(msg="No remote files or directories found", level='warn')

  ######################
  ## Uploading a file ##
  ######################

  lfile = './test.txt'

  lfilename = fpath.splitext(fpath.basename(lfile))[0]
  rfile = "{0}/{1}".format(share,lfilename)
  pydav.sendlog(msg='Uploading {0}'.format(lfile))
  res = pydav.upload(lfile, rfile)
  if res['code'] == 1:
   del(pydav)
   exit(res['code'])

  ###################
  ## Removing file ##
  ###################

  # list remote files ... again...
  remotefiles = pydav.list(share)
  print(remotefiles)

  file2del = 'lfile'
  pydav.delete("{0}/{1}".format(share, file2del))

  # list remote files ... again...
  remotefiles = pydav.list(share)
  print(remotefiles)
