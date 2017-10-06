#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from os import path as fpath
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

curScriptDir = fpath.dirname(fpath.abspath(__file__))
#parentScriptDir = fpath.dirname(fpath.dirname(fpath.abspath(__file__)))
curScriptName = fpath.splitext(fpath.basename(__file__))[0]

def createConf(configpath=False):
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
  config.set('DEFAULT', 'localpath', fpath.normpath('{}/pydav-datas'.format(curScriptDir)))
  config.set('DEFAULT', 'debug', 'False')

  action = False
  try:
    config.add_section('webdav')
  except ConfigParser.DuplicateSectionError:
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
  except ConfigParser.DuplicateSectionError:
    print("INFO: Section 'logging' already exist, nothing to do.")
  else:
    action = True
    config.set('logging', 'logdst', 'console')
    config.set('logging', 'logfilepath', '/var/log/')

  if not action:
    res = {
        "error": False,
        "message": "INFO: Nothing to do for " +
        str(configpath) +
        ".\nIf your sections are empty, please remove your config file and launch me again."}
    return(res)
  else:
    try:
      wfile = open(configpath, 'wt')
    except IOError:
      res = {
          "error": True,
          "message": "ERROR: Unable to open file " +
          str(configpath)}
      return(res)
    except:
      res = {
          "error": True,
          "message": "ERROR: Unable to open file " +
          str(configpath)}
      return(res)
    else:
      try:
        config.write(wfile)
      except IOError:
        res = {
            "error": True,
            "message": "ERROR: Unable to write file " +
            str(wfile)}
        return(res)
      except:
        res = {
            "error": True,
            "message": "ERROR: Unable to write file " +
            str(configpath)}
        return(res)
    wfile.close()

    res = {
      "error": False,
      "message": "INFO: Config file " +
      str(wfile) +
      " written"}

  return(res)

def core(configpath):
  '''
   Allow to easily connect to webdav using config file parser

  param:configpath
  type:str

  return: webdav client connection object
  '''
  config = fpath.normpath(configpath)
  # Creating default setup if it does not exists
  if not fpath.exists(config):
    createRes = createConf(config)
    if createRes['error']:
      result = {'code':1, 'content':createRes['message']}
      return(result)
    msg = 'INFO: Default configuration done! Please edit {} before launching {} again.'.format(config, curScriptName)
    result = {code:1, content:msg}
    return(result)

  # Get param from config file .ini
  configinfos = configparser.ConfigParser()
  try:
    configinfos.read(config)
  except ConfigParser.ParsingError as e:
    result = {'code':1, 'content':e}
    return(result)
  except ConfigParser.Error as e:
    result = {'code':1, 'content':e}
    return(result)

  configinfos.sections()
  for s in ['webdav', 'DEFAULT']:
    if s not in configinfos:
      msg = "ERR: Bad config file format, missing section {} in {}\nINFO: You can regenerate a default config file by removing the current one.".format(s, configpath),
      result = {'code':1, 'content':msg}
      return(result)

  try:
    mainVerbosity = configinfos.getboolean('DEFAULT', 'debug')
  except:
    mainVerbosity = False

  try:
    localPath = configinfos['DEFAULT']['lpath']
  except:
    localPath = fpath.normpath('{}/pydav-datas'.format(curScriptDir))
    print("WARN: No default local filesystem path defined, defaulting to {}.".format(localPath))

  for wv in ['rhost','rlogin','rpass']:
    if wv not in configinfos['webdav']:
      msg = "ERR: Missing {} value in your configuration file {} in section [webdav].".format(wv, configpath)
      result = {'code':1, 'content':msg}
      return(result)
  webdavHost = configinfos['webdav']['rhost']
  wedavLogin = configinfos['webdav']['rlogin']
  wedavPass = configinfos['webdav']['rpass']

  try:
    webdavRoot = configinfos['webdav']['webdav_root']
  except:
    webdavRoot = "/"
    print("WARN: No WebDav root defined, defaulting to {}.".format(webdavRoot))

  try:
    webdavShare = configinfos['webdav']['share']
  except:
    webdavShare = "/"
    print("WARN: No WebDav remote sharing location defined, defaulting to {}.".format(webdavShare))

  logDst = False
  if 'logging' not in configinfos:
    logDst = '/var/log'
    logDst = '{}/{}.log'.format(logDst, curScriptName)
    logType = 'console'
  else:
    try:
      logType = configinfos['logging']['logdst']
    except:
      logType = 'console'
      print('WARN: Unable to define logging type. Defaulting to {}.'.format(logType))
    else:
      if logType == "file":
        try:
          logDst = configinfos['logging']['logfilepath']
        except:
          msg = "ERR: Trying to log to a file but no log file path defined.\nPlease set logfilepath = path/to/file/log in section [logging] of your config file {}".format(configpath)
          result = {'code':1, 'content':msg}
          return(result)

  # init webdav
  webdavClient = client.core(host=webdavHost, login=wedavLogin, passwd=wedavPass, root=webdavRoot, logtype=logType, logfile=logDst, verbosity=mainVerbosity)

  # connection to webdav server
  connected = webdavClient.connect()
  if connected['code'] == 1:
    webdavClient.sendlog(msg=connected['reason'], level='warn')
    del(webdavClient)
    result = {'code':connected['code'], 'content':connected['reason']}
    return(result)

  # checking target path exists
  res = webdavClient.check(webdavShare)
  if res['code'] == 1:
    webdavClient.sendlog(msg=res['reason'], level='warn')
    del(webdavClient)
    result = {'code':res['code'], 'content':res['reason']}
    return(result)

  result = {'code':0, 'content':webdavClient}
  return(result)

if __name__ == "__main__":
  pass
  '''
  configpath = "config.ini"
  configpath = "{}/{}".format(curScriptDir, configpath)

  webdavClient = core(configpath)
  if webdavClient['code'] != 0:
    print(webdavClient['content'])
    exit(1)

  del(webdavClient['content'])
  exit(0)
  '''
