#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
from os import path as fpath, remove as fremove, stat as fstat
import logging, logging.handlers
import signal
import webdav.client as wc

__author__ = "Alain Maibach"
__status__ = "Beta tests"

'''
    Python3 skel helper
    Copyright (C) 2016 MAIBACH ALAIN

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

''' Sources
  https://pypi.python.org/pypi/webdavclient/1.0.8
  https://github.com/CloudPolis/webdav-client-python
  https://journeyman-to-zen.blogspot.fr/2014/04/how-to-use-pycurl-to-provide-status-bar.html
'''

# check python version
'''
if( sys.version_info.major != 3 ):
    print("This script requires Python 3")
    exit(1)
elif( sys.version_info.minor < 4 ):
    print("This script requires Python >= 3.4")
    exit(1)
elif( sys.version_info.micro < 1 ):
    print("This script requires Python >= 3.4.1")
'''
# Fin check

python3 = sys.version_info.major == 3

curScriptDir = fpath.dirname(fpath.abspath(__file__))
#parentScriptDir = fpath.dirname(fpath.dirname(fpath.abspath(__file__)))
curScriptName = fpath.splitext(fpath.basename(__file__))[0]

class pywebdav():
  '''
  Main class to instanciate
  '''

  def __init__(
    self,
    host,
    login,
    passwd,
    root,
    logtype='syslog',
    logfile=None,
    verbosity=False
    ):
    '''
    Init and connect to webdav.
    :param xxx: desc.
    :type xxx: Boolean.
    '''

    self.__verbose = verbosity
    self.__host = host
    self.__login = login
    self.__error = {'code':0, 'reason':''}

    self.__options = {
      'webdav_hostname': host,
      'webdav_login':    login,
      'webdav_password': passwd,
      'root': root,
      #'proxy_hostname':  "http://127.0.0.1:8080",
      #'proxy_login':     "p_login",
      #'proxy_password':  "p_password",
      #'cert_path':       "/etc/ssl/certs/certificate.crt",
      #'key_path':        "/etc/ssl/private/certificate.key",
      #'recv_speed' : 3000000,
      #'send_speed' : 3000000,
      'verbose'    : verbosity
    }

    # calling signal handler
    signal.signal(signal.SIGINT, self.sigint_handler)

    if logtype not in ['console','file','syslog']:
      self.sendlog(msg="Log destination not set or incorrect, logging to syslog", dst='console', level='warn')
      self.__logtype = 'syslog'
    else:
      self.__logtype = logtype

    if self.__logtype == 'file' and logfile is None:
      self.sendlog(msg="Log destination file not set, logging to syslog", dst='console', level='warn')
      self.__logtype = 'syslog'
    else:
      self.__logfile = logfile

  def sigint_handler(self, signum, frame):
    '''
    Class sig handler for ctrl+c interrupt
    '''

    if self.__verbose:
      if self.__logtype == 'file':
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, msg="Execution interrupted by pressing [CTRL+C]")
      else:
        self.sendlog(msg="Execution interrupted by pressing [CTRL+C]", dst=self.__logtype)

    # Do something more here during cancel action.
    exit(0)

  def progress(self, total_to_download, total_downloaded, total_to_upload, total_uploaded):
    '''
     Callback function invoked when download/upload has progress
     with pretty print progress and percentage 
    '''

    if total_to_upload:
      percent_completed = float(total_uploaded)/total_to_upload       # You are calculating amount uploaded
      rate = round(percent_completed * 100, ndigits=2)                # Convert the completed fraction to percentage
      completed = "#" * int(rate)                                     # Calculate completed percentage
      spaces = " " * ( 100 - int(rate) )                              # Calculate remaining completed rate
      status = '[%s%s] %s%%' %(completed, spaces, rate)
      sys.stdout.write('\r' + str(status))                            # the pretty progress [####     ] 34%
      sys.stdout.flush()

    if total_to_download:
      percent_completed = float(total_downloaded)/total_to_download   # You are calculating amount uploaded
      rate = round(percent_completed * 100, ndigits=2)                # Convert the completed fraction to percentage
      completed = "#" * int(rate)                                     # Calculate completed percentage
      spaces = " " * ( 100 - int(rate) )                              # Calculate remaining completed rate
      status = '[%s%s] %s%%' %(completed, spaces, rate)
      sys.stdout.write('\r' + str(status))                            # the pretty progress [####     ] 34%
      sys.stdout.flush()

  def file_size(self, fname):
    '''
    '''
    statinfo = fstat(fname)
    return(statinfo.st_size)

  def sendlog(self, msg, level='INFO', dst=False, logfpath=False):
    '''
    Allow to send log easily to a stream of your choice
    Use: your message, level of the message (info, warn, debug etc..), destination stream (console, file or syslog)
    '''

    if not dst:
      dst = self.__logtype

    if not logfpath:
      logfpath = self.__logfile

    message = str(msg)
    loglvl = str(level)

    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - [{0} %(processName)s] %(levelname)s: %(message)s'.format(curScriptName))

    if str(dst) == 'syslog':
      # create syslog handler
      handler = logging.handlers.SysLogHandler(address = '/dev/log')
      formatter = logging.Formatter('[{0} %(processName)s] %(levelname)s: %(message)s'.format(curScriptName))
      handler.setFormatter(formatter)
    elif str(dst) == 'file':
      # create file handler
      if not logfpath:
        handler = logging.handlers.WatchedFileHandler(r'{0}/pyWebdav.log'.format(curScriptDir))
      else:
        handler = logging.handlers.WatchedFileHandler(r'{0}'.format(logfpath))
      handler.setFormatter(formatter)
    else:
      # create console handler
      handler = logging.StreamHandler()
      handler.setFormatter(formatter)

    # send log
    logger.addHandler(handler)
    if loglvl == 'DEBUG' or loglvl == 'debug':
      logger.debug(message)
    elif loglvl == 'INFO' or loglvl == 'info':
      logger.info(message)
    elif loglvl == 'WARN' or loglvl == 'warn':
      logger.warn(message)
    elif loglvl == 'ERROR' or loglvl == 'error':
      logger.error(message)
    else:
      logger.critical(message)
    logger.removeHandler(handler)

  def connect(self):
    '''
     function to connect to webdav
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    try:
      self.__client = wc.Client(self.__options)
    except wc.WebDavException as exception:
      if self.__logtype == 'file': 
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level='error', msg=exception)
      else:
        self.sendlog(msg=exception, dst=self.__logtype, level='error')
      self.__error = {'code':1, 'reason':'Unable to connect'}

    if self.__logtype == 'file':
      self.sendlog(logfpath=self.__logfile, dst=self.__logtype, msg="Connected to {0} as {1}".format(self.__host, self.__login))
    else:
      self.sendlog(msg="Connected to {0} as {1}".format(self.__host, self.__login), dst=self.__logtype)

    self.__error = {'code':0}

    return(self.__error)

  def check(self, target):
    '''
     Check target exists on remote webdav server
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    try:
      if not self.__client.check(target):
        if self.__logtype == 'file': 
          self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="warn", msg="Unable to find {0}".format(target))
        else:
          self.sendlog(dst=self.__logtype, level="warn", msg="Unable to find {0}".format(target))

        self.__error = {'code':1,'reason':"Unable to find {0}".format(target)}
      else:
        self.__error = {'code':0}
    except wc.WebDavException as exception:
      if self.__logtype == 'file': 
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="error", msg=exception)
      else:
        self.sendlog(dst=self.__logtype, level="errot", msg=exception)

      self.__error = {'code':1,'reason':"Unable to find {0}".format(target)}

    return(self.__error)

  def list(self, target):
    '''
     List share content
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    remotefiles = self.__client.list(target)
    return(remotefiles)

  def getinfo(self, target):
    '''
     Get infos about file
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    fileinfos = self.__client.info(target)
    return(fileinfos)

  def download(self, remote, local):
    '''
     Downloading file from webdav
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    # ici
    # check if it is a directory or a file and adapt below to be able to download in any cases
    #client.download_directory(remote_path="/{0}/Terminator 2.avi".format(share), local_path="{0}/Terminator-2.avi".format(lpath), progress=progress)
    # ici

    fileinfo = self.getinfo(remote)
    rfilesize = fileinfo['size']

    self.__client.download(remote_path=remote, local_path=local, progress=self.progress)
    # print console carriage return after progress bar
    #self.sendlog(dst='console', msg='')
    print('')

    lfilesize = self.file_size(local)

    if int(lfilesize) == int(rfilesize) :
      if self.__logtype == 'file': 
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, msg='File {0} downloaded correctly'.format(rfilename))
      else:
        self.sendlog(dst=self.__logtype, msg='File {0} downloaded correctly'.format(rfilename))

      self.__error = {'code':0}
    else:
      if self.__logtype == 'file': 
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="warn", msg='Download failed: partially retrieved.')
      else:
        self.sendlog(dst=self.__logtype, level="warn", msg='Download failed: partially retrieved.')

      fremove(location)
      self.__error = {'code':1,'reason':"Unable to find {0}".format(target)}

    return(self.__error)

  def upload(self, local, remote): 
    '''
     Uploading file to Webdav
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    self.__client.upload(remote_path=remote, local_path=local, progress=self.progress)
    # print console carriage return after progress bar
    #self.sendlog(dst='console', msg='')
    print('')
    if not self.__client.check(remote):
      if self.__logtype == 'file': 
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="warn", msg="Unable to upload {0}".format(local))
      else:
        self.sendlog(dst=self.__logtype, level="warn", msg="Unable to upload {0}".format(local))
      self.__error = {'code':1,'reason':"Unable to upload {0}".format(local)}
    else:
      self.__error = {'code':0}

    return(self.__error)

  def createdir(self, target):
    '''
     Create directory
    '''
    self.__client.mkdir(target)

  def delete(self, target):
    '''
     Delete resource
    '''
    self.__client.clean(target)

  def duplicate(self, target, twin):
    '''
     Copy resource
    '''
    self.__client.copy(remote_path_from=target, remote_path_to=twin)

  def move(self, target, new):
    '''
     Move resource
    '''
    self.__client.move(remote_path_from=target, remote_path_to=new)

if __name__ == "__main__":
  """
  Main part used if self-executed
  """

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
  pydav = pywebdav(host=rhost, login=rlogin, passwd=rpass, root=webdav_root, logtype=logdst, logfile=logfilepath, verbosity=False)

  # connection to webdav server
  connected = pydav.connect()
  if connected['code'] == 1:
   print(connected['reason'])
   exit(connected['code'])

  # cheking target path exists
  res = pydav.check(share)
  if res['code'] == 1:
   print(res['reason'])
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
       print(res['reason'])
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
   print(res['reason'])
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
