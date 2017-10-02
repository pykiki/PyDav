#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
from os import path as fpath, remove as fremove, stat as fstat, listdir, makedirs
import logging, logging.handlers
import signal
try:
  import webdav.client as wc
except:
  packages = ""
  with open("../requirements.txt", "rb") as requirements:
    req_tab = requirements.read().splitlines()
#     size_tab = len(req_tab)
    for indice, line in enumerate(req_tab):
      if indice == 0 :
        packages = "{0}".format(line.decode('utf-8'))
      else:
        packages = "{0}, {1}".format(packages, line.decode('utf-8'))

  print('Please install python libraries: {0}'.format(packages))
  exit(1)

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

class core():
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
    logfile='',
    verbosity=False
    ):
    '''
    Init and connect to webdav.
    :param xxx: desc.
    :type xxx: Boolean.
    '''

    self.__error = {'code':0, 'reason':''}

    if logtype not in ['console','file','syslog']:
      self.sendlog(msg="Log destination not set or incorrect, logging to syslog", dst='console', level='warn')
      self.__logtype = 'syslog'
    else:
      self.__logtype = logtype

    if self.__logtype == 'file' and logfile == '':
      self.__logtype = 'syslog'
      self.sendlog(msg="Log destination file not set, logging to syslog", dst='console', level='warn')
    else:
      self.__logfile = logfile

    self.__verbose = verbosity
    if host != "" and host is not None:
      self.__host = host
    else:
      self.sendlog(msg="Host cannot be empty.", dst=self.__logtype, level='warn')
      self.__error = {'code':1, 'reason':'Host cannot be empty.'}

    if login != "" and login is not None:
      self.__login = login
    else:
      self.sendlog(msg="Login cannot be empty.", dst=self.__logtype, level='warn')
      self.__error = {'code':1, 'reason':'Login cannot be empty.'}

    if passwd == "" or passwd is None:
      self.sendlog(msg="Empty password set.", dst=self.__logtype, level='warn')

    self.__root = root

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

  def __del__(self):
    pass

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
    if self.__error['code'] == 1:
      return(self.__error)

    statinfo = fstat(fname)
    return(statinfo.st_size)

  def sendlog(self, msg, level='INFO', dst=False, logfpath=False):
    '''
    Allow to send log easily to a stream of your choice
    Use: your message, level of the message (info, warn, debug etc..), destination stream (console, file or syslog)
    '''

    if self.__error['code'] == 1:
      return(self.__error)

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

    self.__client = wc.Client(self.__options)
    try:
      self.__client.list()
    except:
      errmsg = "Unable to connect to server: {0}.".format(self.__host)
      if self.__logtype == 'file':
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level='error', msg=errmsg)
      else:
        self.sendlog(msg=errmsg, dst=self.__logtype, level='error')
      self.__error = {'code':1, 'reason':errmsg}
      return(self.__error)

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
        self.sendlog(dst=self.__logtype, level="error", msg=exception)

      self.__error = {'code':1,'reason':"Unable to find {0}".format(target)}

    return(self.__error)

  def list(self, target):
    '''
     List share content
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    try:
      remotefiles = self.__client.list(target)
    except wc.WebDavException as exception:
      if self.__logtype == 'file':
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="warn", msg=exception)
      else:
        self.sendlog(dst=self.__logtype, level="warn", msg=exception)
      self.__error = {'code':1,'reason':exception}
      return(self.__error)
    else:
      return(remotefiles)

  def getinfo(self, target):
    '''
     Get infos about file
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    try:
      fileinfos = self.__client.info(target)
    except wc.WebDavException as exception:
      if self.__logtype == 'file':
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="warn", msg=exception)
      else:
        self.sendlog(dst=self.__logtype, level="warn", msg=exception)
      self.__error = {'code':1,'reason':exception}
      return(self.__error)
    else:
      return(fileinfos)

  def download(self, remote, local):
    '''
     Downloading file from webdav
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    isdir = False
    fileinfo = self.getinfo(remote)
    if 'code' in fileinfo:
      return(self.__error)

    rfilesize = fileinfo['size']

    if rfilesize is None:
      rdircontent = self.__client.list(remote)
      if 'code' in rdircontent:
        return(self.__error)
      if len(rdircontent) > 0:
        isdir = True
      else:
        errstr = 'Directory {0} is empty, or the file is corrupted, skip downloading'.format(remote)
        if self.__logtype == 'file':
          self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="warn", msg=errstr)
        else:
          self.sendlog(dst=self.__logtype, level="warn", msg=errstr)
        self.__error = {'code':0,'reason':errstr}
        return(self.__error)

    if fpath.exists(local):
      if not isdir:
        lfilesize = self.file_size(local)
        if int(lfilesize) == int(rfilesize) :
          errmsg = "File {0} already locally exists, skip downloading.".format(local)
          if self.__logtype == 'file':
            self.sendlog(logfpath=self.__logfile, dst=self.__logtype, msg=errmsg)
          else:
            self.sendlog(dst=self.__logtype, msg=errmsg)
          self.__error = {'code':0,'reason':errmsg}
          return(self.__error)
        else:
          errmsg = "File {0} locally exists, but seems to be different, trying to download again.".format(local)
          if self.__logtype == 'file':
            self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="warn", msg=errmsg)
          else:
            self.sendlog(dst=self.__logtype, level="warn", msg=errmsg)

    if not self.__client.check(remote):
      errmsg = "Remote file {0} not found.".format(remote)
      if self.__logtype == 'file':
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="warn", msg=errmsg)
      else:
        self.sendlog(dst=self.__logtype, level="warn", msg=errmsg)
      self.__error = {'code':1,'reason':errmsg}
      return(self.__error)

    if isdir:
      infostr = 'Downloading directory {0}'.format(remote)
      self.make_local_dirs(local)
      if self.__logtype == 'file':
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, msg=infostr)
      else:
        self.sendlog(dst=self.__logtype, msg=infostr)

      for f in rdircontent:
        if f[-1] == "/" :
          f = f[:-1]

        remotefrecurse = "{0}/{1}".format(remote, f)
        localefrecurse = "{0}/{1}".format(local, f)

        self.download(remotefrecurse, localefrecurse)
        if self.__error['code'] == 1:
          return(self.__error)

    else:
      infostr = 'Downloading file {0}'.format(remote)
      if self.__logtype == 'file':
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, msg=infostr)
      else:
        self.sendlog(dst=self.__logtype, msg=infostr)

      localdirdest = fpath.dirname(fpath.abspath(local))
      localdirdest = localdirdest.replace("//","/")
      if not fpath.exists( localdirdest ):
        self.make_local_dirs(localdirdest)

      try:
        self.__client.download(remote_path=remote, local_path=local, progress=self.progress)
        # print console carriage return after progress bar
        #self.sendlog(dst='console', msg='')
        print('')
      except wc.WebDavException as exception:
        if self.__logtype == 'file':
          self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="error", msg=exception)
        else:
          self.sendlog(dst=self.__logtype, level="error", msg=exception)

        self.__error = {'code':1,'reason':exception}
        return(self.__error)

      lfilesize = self.file_size(local)

      if int(lfilesize) == int(rfilesize) :
        if self.__logtype == 'file':
          self.sendlog(logfpath=self.__logfile, dst=self.__logtype, msg='File {0} downloaded correctly'.format(remote))
        else:
          self.sendlog(dst=self.__logtype, msg='File {0} downloaded correctly'.format(remote))

        self.__error = {'code':0}
      else:
        if self.__logtype == 'file':
          self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="warn", msg='Download failed: partially retrieved.')
        else:
          self.sendlog(dst=self.__logtype, level="warn", msg='Download failed: partially retrieved.')

        fremove(local)
        #self.__error = {'code':1,'reason':"Unable to find {0}".format(target)}
        self.__error = {'code':1,'reason':"Download failed: partially retrieved."}

      return(self.__error)

    return(self.__error)

  def upload(self, local, remote): 
    '''
     Uploading file to Webdav
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    try:
      self.__client.upload(remote_path=remote, local_path=local, progress=self.progress)
      # print console carriage return after progress bar
      #self.sendlog(dst='console', msg='')
      print('')
    except wc.WebDavException as exception:
      if self.__logtype == 'file':
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="error", msg=exception)
      else:
        self.sendlog(dst=self.__logtype, level="error", msg=exception)
      self.__error = {'code':1,'reason':exception}
      return(self.__error)

    if not self.__client.check(remote):
      if self.__logtype == 'file':
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="warn", msg="Unable to upload {0}".format(local))
      else:
        self.sendlog(dst=self.__logtype, level="warn", msg="Unable to upload {0}".format(local))
      self.__error = {'code':1,'reason':"Unable to upload {0}".format(local)}
    else:
      self.__error = {'code':0}

      if self.__logtype == 'file':
        self.sendlog(logfpath=self.__logfile, dst=self.__logtype, msg='File {0} uploaded correctly'.format(local))
      else:
        self.sendlog(dst=self.__logtype, msg='File {0} uploaded correctly'.format(local))

    return(self.__error)

  def createdir(self, target):
    '''
     Create directory
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    self.__client.mkdir(target)

  def delete(self, target):
    '''
     Delete resource
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    self.__client.clean(target)

  def duplicate(self, target, twin):
    '''
     Copy resource
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    self.__client.copy(remote_path_from=target, remote_path_to=twin)

  def move(self, target, new):
    '''
     Move resource
    '''
    if self.__error['code'] == 1:
      return(self.__error)

    self.__client.move(remote_path_from=target, remote_path_to=new)

  def search(self, target, path=False, found=False):
    '''
     Search for file or directory recursively
    '''

    if not found:
      found = []

    if path:
      currdir = str(path)
    else:
      currdir = "/"

    remotefiles = self.list(currdir)
    if 'code' in remotefiles:
      return(self.__error)

    if len(remotefiles) > 0:
      for f in remotefiles:
        if f[-1] == "/" :
          f = f[:-1]

        if currdir != '/':
          currfile = "{0}/{1}".format(currdir,f)
        else:
          currfile = "/{0}".format(f)

        if target in f or target == f:
          found.append( "{0}/{1}".format(currdir,f) )
        if self.__client.is_dir(currfile):
          found = self.search(target, currfile, found)

      # Ensure there is no duplicates in list found
      uniqueList=[]
      for i in found:
        if i not in uniqueList:
          uniqueList.append(i)
      found = uniqueList

    return(found)

  def make_local_dirs(self, directory):
    if not fpath.exists(directory):
      try:
          makedirs(directory, 0o750)
      except PermissionError as e:
        errmsg = "Unable to create local directory {0}: {1}".format(directory, e.strerror)
        if self.__logtype == 'file':
          self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="error", msg=errmsg)
        else:
          self.sendlog(dst=self.__logtype, level="error", msg=errmsg)
        self.__error = {'code':1,'reason':errmsg}
        return(self.__error)
      except OSError as exception:
        if exception.errno != errno.EEXIST:
          errmsg = "Unable to create local directory {0}: {1}".format(directory, exception)
          if self.__logtype == 'file':
            self.sendlog(logfpath=self.__logfile, dst=self.__logtype, level="error", msg=errmsg)
          else:
            self.sendlog(dst=self.__logtype, level="error", msg=errmsg)
          self.__error = {'code':1,'reason':errmsg}
          return(self.__error)

  #pkidbDict = property(read_pkidb, None, None, "Get pki db in a dict")

if __name__ == "__main__":
  """
  Main part used if self-executed
  """

  # Webdav global informations part
  rhost = "https://mycloud.maibach.fr:8443"
  rlogin = "kikidood"
  rpass = "pPN6o4whU8ySMCpL"
  webdav_root = "/remote.php/webdav/"
  
  # Webdav target path
  share = "/public"
  
  # local download filesystem path
  lpath = "/home/amaibach/Downloads/pydav-datas"

  # logging information
  logdst = "console" # other values: syslog | file
  logfilepath = '/var/log/{0}.log'.format(curScriptName)

  # init webdav
  pydav = core(host=rhost, login=rlogin, passwd=rpass, root=webdav_root, logtype=logdst, logfile=logfilepath, verbosity=False)

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

  if lpath[-1] == "/" :
    lpath = lapath[:-1]

  '''
  ############################
  # list target path content #
  ############################
  remotefiles = pydav.list(share)
  if 'code' in remotefiles:
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
  '''

  ######################
  ## Uploading a file ##
  ######################

  lfile = '/home/amaibach/Downloads/pydav-datas/public/Music/toto-1/todo.txt'
  lfilename = fpath.basename(lfile)
  rfile = "{0}/{1}".format(share,lfilename)

  pydav.sendlog(msg='Uploading {0}'.format(lfile))
  res = pydav.upload(lfile, rfile)
  if res['code'] == 1:
   del(pydav)
   exit(res['code'])

  # ici
  del(pydav)
  exit(0)

  ###################
  ## Removing file ##
  ###################

  # list remote files ... again...
  remotefiles = pydav.list(share)
  if 'code' in remotefiles:
     del(pydav)
     exit(remotefiles['code'])
  else:
    print(remotefiles)

  file2del = 'todo'
  pydav.delete("{0}/{1}".format(share, file2del))

  remotefiles = pydav.list(share)
  if 'code' in remotefiles:
     del(pydav)
     exit(remotefiles['code'])
  else:
    print(remotefiles)
