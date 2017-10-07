#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from os import path as fpath
import signal
try:
  from PyDav import client
except:
  print('Please Install PyDav library.')
  exit(1)
try:
  import configparser
except:
  print('Please Install configParser python library.')
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

class core():
  '''
  Main class to instanciate
  '''

  def __init__(self, configpath) :
    '''
    Init and connect to webdav.
    :param configpath: filesystem path to webdav client config.ini file.
    :type configpath: String.
    '''

    self.__curConfigDir = fpath.dirname(fpath.abspath(configpath))

    self.__error = {'code':0, 'reason':''}
    self.__config = fpath.normpath(configpath)

    # Creating default setup if it does not exists
    if not fpath.exists(self.__config):
      createRes = self.createConf()
      if createRes['error']:
        print(createRes['message'])
        exit(1)
      else:
        print('INFO: Default configuration done! Please edit {} before going further.'.format(self.__config))
        exit(1)

    # calling signal handler
    signal.signal(signal.SIGINT, self.sigint_handler)

  def __del__(self):
    if hasattr(self, '_core__webdavClient'):
      del(self.__webdavClient)

  def sigint_handler(self, signum, frame):
    '''
    Class sig handler for ctrl+c interrupt
    '''
 
    print("Execution interrupted by pressing [CTRL+C]")

    # Do something more here during cancel action.
    if hasattr(self, '_core__webdavClient'):
      del(self.__webdavClient)
    exit(1)

  def createConf(self):
    '''
    Creates default ini config file. This implementation 
    make it more easier to load config file.

    :returns: Informational result dict {'error': Boolean, 'message': String}
    :rtype: Dict.
    '''
    config = configparser.ConfigParser(
      delimiters='=', comment_prefixes='#')

    # No needs to create DEFAULT section
    #config.add_section('DEFAULT')
    config.set('DEFAULT', 'localpath', fpath.normpath('{}/pydav-datas'.format(self.__curConfigDir)))
    config.set('DEFAULT', 'debug', 'False')

    action = False
    try:
      config.add_section('webdav')
    except configparser.DuplicateSectionError:
      print("INFO: Section 'webdav' already exist, nothing to do.")
    else:
      action = True
      config.set('webdav', 'rhost', 'http://127.0.0.1')
      config.set('webdav', 'rlogin', 'johnDoe')
      config.set('webdav', 'rpass', 'None')
      config.set('webdav', 'webdav_root', '/')
      config.set('webdav', 'share', '/synced')

    try:
      config.add_section('logging')
    except configparser.DuplicateSectionError:
      print("INFO: Section 'logging' already exist, nothing to do.")
    else:
      action = True
      config.set('logging', 'logdst', 'console')
      config.set('logging', 'logfilepath', '/var/log/')

    if not action:
      res = {
          "error": False,
          "message": "INFO: Nothing to do for {}.\nIf your sections are empty, please remove your config file and launch me again.".format(str(self.__config))
          }
      return(res)
    else:
      try:
        wfile = open(self.__config, 'wt')
      except IOError:
        res = {
            "error": True,
            "message": "ERROR: Unable to open file {}".format(str(self.__config))
            }
        return(res)
      except:
        res = {
            "error": True,
            "message": "ERROR: Unable to open file {}".format(str(self.__config))
            }
        return(res)
      else:
        try:
          config.write(wfile)
        except IOError:
          res = {
              "error": True,
              "message": "ERROR: Unable to write file {}".format(str(wfile))
              }
          return(res)
        except:
          res = {
              "error": True,
              "message": "ERROR: Unable to write file {}".format(str(wfile))
              }
          return(res)
      wfile.close()

      res = {
        "error": False,
        "message": "INFO: Config file {} written".format(str(wfile))
        }

    return(res)

  def connect(self):
    '''
     Allow to easily connect to webdav using config file parser

    return: webdav client connection object
    '''

    # Get param from config file .ini
    configinfos = configparser.ConfigParser()
    try:
      configinfos.read(self.__config)
    except configparser.ParsingError as e:
      result = {'code':1, 'content':e}
      return(result)
    except configparser.Error as e:
      result = {'code':1, 'content':e}
      return(result)

    configinfos.sections()
    for s in ['webdav', 'DEFAULT']:
      if s not in configinfos:
        msg = "ERR: Bad config file format, missing section {} in {}\nINFO: You can regenerate a default config file by removing the current one.".format(s, self.__config),
        result = {'code':1, 'content':msg}
        return(result)

    try:
      self.__mainVerbosity = configinfos.getboolean('DEFAULT', 'debug')
    except:
      self.__mainVerbosity = False

    try:
      self.__localPath = configinfos['DEFAULT']['localpath']
    except:
      self.__localPath = fpath.normpath('{}/pydav-datas'.format(self.__curConfigDir))
      print("WARN: No default local filesystem path defined, defaulting to {}.".format(self.__localPath))

    for wv in ['rhost','rlogin','rpass']:
      if wv not in configinfos['webdav']:
        msg = "ERR: Missing {} value in your configuration file {} in section [webdav].".format(wv, self.__config)
        result = {'code':1, 'content':msg}
        return(result)
    self.__webdavHost = configinfos['webdav']['rhost']
    self.__wedavLogin = configinfos['webdav']['rlogin']
    self.__wedavPass = configinfos['webdav']['rpass']

    try:
      self.__webdavRoot = configinfos['webdav']['webdav_root']
    except:
      self.__webdavRoot = "/"
      print("WARN: No WebDav root defined, defaulting to {}.".format(self.__webdavRoot))

    try:
      self.__webdavShare = configinfos['webdav']['share']
    except:
      self.__webdavShare = "/"
      print("WARN: No WebDav remote sharing location defined, defaulting to {}.".format(self.__webdavShare))

    self.__logDst = False
    if 'logging' not in configinfos:
      self.__logDst = '/var/log'
      self.__logDst = '{}/pydav.log'.format(logDst)
      self.__logType = 'console'
    else:
      try:
        self.__logType = configinfos['logging']['logdst']
      except:
        self.__logType = 'console'
        print('WARN: Unable to define logging type. Defaulting to {}.'.format(self.__logType))
      else:
        if self.__logType == "file":
          try:
            self.__logDst = configinfos['logging']['logfilepath']
          except:
            msg = "ERR: Trying to log to a file but no log file path defined.\nPlease set logfilepath = path/to/file/log in section [logging] of your config file {}".format(self.__config)
            result = {'code':1, 'content':msg}
            return(result)

    # init webdav
    self.__webdavClient = client.core(host=self.__webdavHost, login=self.__wedavLogin, passwd=self.__wedavPass, root=self.__webdavRoot, logtype=self.__logType, logfile=self.__logDst, verbosity=self.__mainVerbosity)

    # connection to webdav server
    connected = self.__webdavClient.connect()
    if connected['code'] == 1:
      self.__webdavClient.sendlog(msg=connected['reason'], level='warn')
      del(self.__webdavClient)
      result = {'code':connected['code'], 'content':connected['reason']}
      return(result)

    # checking target path exists
    res = self.__webdavClient.check(self.__webdavShare)
    if res['code'] == 1:
      self.__webdavClient.sendlog(msg=res['reason'], level='warn')
      del(self.__webdavClient)
      result = {'code':res['code'], 'content':res['reason']}
      return(result)

    result = {'code':0}
    return(result)

  def remote_list(self):
    remotefiles = self.__webdavClient.list(self.__webdavShare)
    if 'code' in remotefiles:
      self.__webdavClient.sendlog(msg=remotefiles['reason'], level='warn')
      result = {'code':res['code'], 'content':res['reason']}
    else:
      result = {'code':0, 'content':remotefiles}

    return(result)
      
  def remote_search(self, matchword):
    res_found = self.__webdavClient.search(matchword)
    if 'code' in res_found:
      self.__webdavClient.sendlog(msg=res_found['reason'], level='warn')
      result = {'code':res_found['code'], 'content':res_found['reason']}
    else:
      result = {'code':0, 'content':res_found}
    return(result)

  def download(self, remote, local):
    res = self.__webdavClient.download(remote, local)
    if res['code'] == 1:              
      result = {'code':res['code'], 'content':res['reason']}
    else:
      result = {'code':0, 'content':''}
    return(result)

  def upload(self, local):
    res = self.__webdavClient.upload(local, self.__webdavShare)
    if res['code'] == 1:
      self.__webdavClient.sendlog(msg=res_found['reason'], level='warn')
      result = {'code':res['code'], 'content':res['reason']}
    else:
      result = {'code':0, 'content':''}
    return(result)

  def remote_duplicate(self, src, dst):
    res2cp = "{0}/{1}".format(self.__webdavShare, src)
    dest = "{0}/{1}".format(self.__webdavShare, dst)
    rescp = self.__webdavClient.duplicate(res2cp, dest)
    if rescp['code'] != 0:
      self.__webdavClient.sendlog(msg=rescp['reason'], level='warn')
      result = {'code':rescp['code'], 'content':rescp['reason']}
    else:
      result = {'code':0, 'content':''}
    return(result)

  def remote_move(self, src, dst):
    res2mv = "{0}/{1}".format(self.__webdavShare, src)
    dest = "{0}/{1}".format(self.__webdavShare, dst)
    resmv = self.__webdavClient.move(res2mv, dest)
    if resmv['code'] != 0:
      self.__webdavClient.sendlog(msg=resmv['reason'], level='warn')
      result = {'code':resmv['code'], 'content':resmv['reason']}
    else:
      result = {'code':0, 'content':''}
    return(result)

  def remote_remove(self, resource):
    res2rm = "{0}/{1}".format(self.__webdavShare, resource)
    resrm = self.__webdavClient.delete(res2rm)
    if resrm['code'] != 0:
      self.__webdavClient.sendlog(msg=resrm['reason'], level='warn')
      result = {'code':resrm['code'], 'content':resrm['reason']}
    else:
      result = {'code':0, 'content':''}
    return(result)

  '''
   Properties section: https://infohost.nmt.edu/tcc/help/pubs/python/web/property-function.html
  '''

  def get_localPath(self):
    if hasattr(self, '_core__localPath'):
      return(self.__localPath)
    else:
      return(False)
  def set_localPath(self, path):
    self.__localPath = path
  localPath = property(get_localPath, set_localPath, None, "Allow to interact with local path value")

  def get_webdavShare(self):
    if hasattr(self, '_core__webdavShare'):
      return(self.__webdavShare)
    else:
      return(False)
  def set_webdavShare(self, path):
    self.__webdavShare = path
  webdavShare = property(get_webdavShare, set_webdavShare, None, "Allow to interact with webdav remote path value")

if __name__ == "__main__":
  pass

  '''
  core("./config.ini")
  connected = webdavClient.connect()
  if connected['code'] != 0:
    del(webdavClient)
    exit(0)
  '''
