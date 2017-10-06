#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from sys import version_info
from os import path as fpath
import signal
import argparse
from sys import argv
try:
  from PyDav import connect
except:
  print('Please Install PyDav library.')
  exit(1)

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

python3 = version_info.major == 3

curScriptDir = fpath.dirname(fpath.abspath(__file__))
#parentScriptDir = fpath.dirname(fpath.dirname(fpath.abspath(__file__)))
curScriptName = fpath.splitext(fpath.basename(__file__))[0]

def sigint_handler(signum, frame):
  '''
  Class sig handler for ctrl+c interrupt
  '''

  print('\nINFO: Execution interrupted by pressing [CTRL+C]')
  exit(0)

def argCommandline(argv):
  """
  Manage cli script args
  """
  parser = argparse.ArgumentParser(description='Webdav client')
  parser.add_argument(
      "-c",
      "--config",
      action="store",
      dest="configpath",
      type=str,
      default=False,
      help=u"PyDav config file path",
      metavar='path/to/config.ini',
      required=False)

  args = parser.parse_args()
  # print help if no arguments given
  if len(argv) <= 1:
    pass
    #parser.print_help()
    #exit(1)

  result = vars(args)

  return(result)

if __name__ == "__main__":

  # get cli args
  args = argCommandline(argv)

  if not args['configpath']:
    configpath = "{}/config.ini".format(curScriptDir)
  else:
    configpath = args['configpath']

  # calling signal handler
  signal.signal(signal.SIGINT, sigint_handler)

  webdavClient = connect.core(configpath)
  if webdavClient['code'] != 0:
    print(webdavClient['content'])
    exit(1)

  # ici
  del(webdavClient['content'])
  exit(0)

  ############################
  # list target path content #
  ############################
  remotefiles = pydav.list(share)
  if 'code' in remotefiles:
    pydav.sendlog(msg=remotefiles['reason'], level='warn')
    del(pydav)
    exit(remotefiles['code'])

  if len(remotefiles) > 0:
    ########################
    ## Downloading a file ##
    ########################

    # we will look for a matching expr
    search = 'Music'
    res_found = pydav.search(search)
    if 'code' in res_found:
      pydav.sendlog(msg=res_found['reason'], level='warn')
    else:
      for rfilename in res_found:
        fileloc = "{0}/{1}".format(lpath, rfilename)
        res = pydav.download(rfilename, fileloc)
        if res['code'] == 1:
         del(pydav)
         exit(res['code'])
  else:
    pydav.sendlog(msg="No remote files or directories found", level='warn')

  # ici
  del(webdavClient)
  exit(0)

  ######################
  ## Uploading a file ##
  ######################

  lfile = '/home/amaibach/Downloads/pydav-datas/public/todo.txt'
  lfilename = fpath.basename(lfile)
  rfile = "{0}/{1}".format(share,lfilename)

  res = pydav.upload(lfile, rfile)
  if res['code'] == 1:
    pydav.sendlog(msg=res['reason'], level='warn')
    del(pydav)
    exit(res['code'])

  ################################
  # list remote files .. again.. #
  ################################
  remotefiles = pydav.list(share)
  if 'code' in remotefiles:
    pydav.sendlog(msg=remotefiles['reason'], level='warn')
    del(pydav)
    exit(remotefiles['code'])
  else:
    pydav.sendlog(msg=remotefiles, level='info')

  ##################
  ## Copying file ##
  ##################

  file2cp = 'todo.txt'
  dst = 'toto-1/zigzag/zizi/todo-copied.txt'

  file2cp = "{0}/{1}".format(share, file2cp)
  dst = "{0}/{1}".format(share, dst)
  rescp = pydav.duplicate(file2cp, dst)
  if rescp['code'] != 0:
    pydav.sendlog(msg=rescp['reason'], level='warn')
    del(pydav)
    exit(rescp['code'])

  ###################
  ##  Moving  file ##
  ###################

  file2mv = 'toto-1/zigzag/zizi/todo-copied.txt'
  dst = 'toto-2/zigzag/todo-moved.txt'

  file2mv = "{0}/{1}".format(share, file2mv)
  dst = "{0}/{1}".format(share, dst)
  resmv = pydav.move(file2mv, dst)
  if resmv['code'] != 0:
    pydav.sendlog(msg=rescp['reason'], level='warn')
    del(pydav)
    exit(rescp['code'])

  ###################
  ## Removing file ##
  ###################

  file2del= 'toto-1/'
  resdel = pydav.delete("{0}/{1}".format(share, file2del))
  if resdel['code'] != 0:
    pydav.sendlog(msg=resdel['reason'], level='warn')
    del(pydav)
    exit(resdel['code'])
  else:
    # list files to check
    remotefiles = pydav.list(share)
    if 'code' in remotefiles:
      pydav.sendlog(msg=remotefiles['reason'], level='warn')
      del(pydav)
      exit(remotefiles['code'])
    else:
      pydav.sendlog(msg=remotefiles, level='info')

  file2del= 'toto-2/'
  resdel = pydav.delete("{0}/{1}".format(share, file2del))
  if resdel['code'] != 0:
    pydav.sendlog(msg=resdel['reason'], level='warn')
    del(pydav)
    exit(resdel['code'])
  else:
    # list files to check
    remotefiles = pydav.list(share)
    if 'code' in remotefiles:
      pydav.sendlog(msg=remotefiles['reason'], level='warn')
      del(pydav)
      exit(remotefiles['code'])
    else:
      pydav.sendlog(msg=remotefiles, level='info')
