#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import re
from os import path as fpath, remove as fremove, stat as fstat, listdir, makedirs, walk
from fnmatch import filter as fnfilter
import logging
import logging.handlers
import signal
try:
    import webdav.client as wc
except BaseException:
    packages = "argcomplete>=1.9.2, lxml>=3.8.0, pycurl>=7.43.0, webdavclient>=1.0.8"
    print('Please install python libraries: {0}'.format(packages))
    exit(1)
else:
    from webdav.client import WebDavException

__author__ = "Alain Maibach"
__status__ = "Released"

'''
    PyDav main class which directly interact with webdavclient python library
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

''' Sources
  https://pypi.python.org/pypi/webdavclient/1.0.8
  https://github.com/CloudPolis/webdav-client-python
  https://journeyman-to-zen.blogspot.fr/2014/04/how-to-use-pycurl-to-provide-status-bar.html
'''

python3 = sys.version_info.major == 3

curScriptDir = fpath.dirname(fpath.abspath(__file__))
curScriptName = fpath.splitext(fpath.basename(__file__))[0]


class core():
    '''
     Main class which will allow
     to interact with webdavclient library

     :param host: Webdav host:port part of URI
     :type  host: string

     :param login: Webdav user login
     :type  login: string

     :param passwd: Webdav user password
     :type  passwd: string

     :param root: Webdav root
     :type  root: string

     :param   logtype: Logging destination (console|syslog|file)
     :type    logtype: string
     :default logtype: 'console'

     :param   logfile: Logging file path if logtype is file
     :type    logfile: string
     :default logfile: False

     :param   verbosity: General debug mode (not really used)
     :type    verbosity: boolean
     :default verbosity: False

     :returns: webdavclient library object
     :rtype: obj
    '''

    def __init__(
        self,
        host,
        login,
        passwd,
        root,
        logtype='console',
        logfile=False,
        verbosity=False
    ):
        '''
         Init class
        '''

        self.__error = {'code': 0, 'reason': ''}

        self.__logfile = logfile

        if logtype not in ['console', 'file', 'syslog']:
            self.sendlog(
                msg="Log destination {} incorrect, logging to console".format(
                    logtype),
                dst='console',
                level='warn')
            self.__logtype = 'console'
        else:
            self.__logtype = logtype

        if self.__logtype == 'file' and not logfile:
            self.__logtype = 'console'
            self.sendlog(
                msg="Log destination file not set, logging to console",
                dst='console',
                level='warn')

        self.__verbose = verbosity
        if host != "" and host is not None:
            self.__host = host
        else:
            self.sendlog(
                msg="Host cannot be empty.",
                dst=self.__logtype,
                level='warn')
            self.__error = {'code': 1, 'reason': 'Host cannot be empty.'}

        if login != "" and login is not None:
            self.__login = login
        else:
            self.sendlog(
                msg="Login cannot be empty.",
                dst=self.__logtype,
                level='warn')
            self.__error = {'code': 1, 'reason': 'Login cannot be empty.'}

        if passwd == "" or passwd is None:
            self.sendlog(
                msg="Empty password set.",
                dst=self.__logtype,
                level='warn')

        self.__root = root

        self.__options = {
            'webdav_hostname': host,
            'webdav_login': login,
            'webdav_password': passwd,
            'root': root,
            # 'proxy_hostname':  "http://127.0.0.1:8080",
            # 'proxy_login':     "p_login",
            # 'proxy_password':  "p_password",
            # 'cert_path':       "/etc/ssl/certs/certificate.crt",
            # 'key_path':        "/etc/ssl/private/certificate.key",
            # 'recv_speed' : 3000000,
            # 'send_speed' : 3000000,
            'verbose': verbosity
        }

        signal.signal(signal.SIGINT, self.sigint_handler)

    def __del__(self):
        pass

    def sigint_handler(self, signum, frame):
        '''
         Class sig handler for ctrl+c interrupt
        '''

        if self.__logtype == 'file':
            self.sendlog(
                logfpath=self.__logfile,
                dst=self.__logtype,
                msg="Execution interrupted by pressing [CTRL+C]")
        else:
            self.sendlog(
                msg="Execution interrupted by pressing [CTRL+C]",
                dst=self.__logtype)
        # Do something
        exit(0)

    def progress(
            self,
            total_to_download,
            total_downloaded,
            total_to_upload,
            total_uploaded):
        '''
         Callback function invoked when download/upload has progress
         with pretty print progress and percentage
        '''

        if total_to_upload:
            percent_completed = float(total_uploaded) / total_to_upload
            rate = round(percent_completed * 100, ndigits=2)
            completed = "#" * int(rate)
            spaces = " " * (100 - int(rate))
            status = '[%s%s] %s%%' % (completed, spaces, rate)
            sys.stdout.write('\r' + str(status))
            sys.stdout.flush()

        if total_to_download:
            percent_completed = float(total_downloaded) / total_to_download
            rate = round(percent_completed * 100, ndigits=2)
            completed = "#" * int(rate)
            spaces = " " * (100 - int(rate))
            status = '[%s%s] %s%%' % (completed, spaces, rate)
            sys.stdout.write('\r' + str(status))
            sys.stdout.flush()

    def file_size(self, fname):
        '''
         Method that return the size of a file
         :param fname: filesystem file path
         :type  fname: string

         :returns: file size in bytes
         :rtype: int
        '''
        if self.__error['code'] == 1:
            return(self.__error)

        statinfo = fstat(fname)
        fsize = int(statinfo.st_size)
        return(fsize)

    def sendlog(self, msg, level='INFO', dst=False, logfpath=False):
        '''
         Allow to send log easily to a stream of your choice

         :param msg: logging message to send
         :type  msg: string

         :param level: logging facility level
         :type  level: string

         :param dst: logging destination (console|syslog|file)
         :type  dst: string

         :param logfpath: If dst is file, allow you to specify the file path
         :type  logfpath: string

         :returns: In case of failure only, it will returns error 'code' and 'reason'
         :rtype: dict
        '''

        if self.__error['code'] == 1:
            return(self.__error)

        if not dst:
            dst = self.__logtype

        if not logfpath:
            if self.__logfile:
                logfpath = self.__logfile

        message = str(msg)
        loglvl = str(level)

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - [{0} %(processName)s] %(levelname)s: %(message)s'.format(curScriptName))

        if str(dst) == 'syslog':
            handler = logging.handlers.SysLogHandler(address='/dev/log')
            formatter = logging.Formatter(
                '[{0} %(processName)s] %(levelname)s: %(message)s'.format(curScriptName))
            handler.setFormatter(formatter)
        elif str(dst) == 'file':
            if not logfpath:
                handler = logging.handlers.WatchedFileHandler(
                    r'{0}/pyWebdav.log'.format(curScriptDir))
            else:
                handler = logging.handlers.WatchedFileHandler(
                    r'{0}'.format(logfpath))
            handler.setFormatter(formatter)
        else:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)

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

         :returns: In case of failure only, it will returns error 'code' and 'reason'
         :rtype: dict
        '''
        if self.__error['code'] == 1:
            return(self.__error)

        self.__client = wc.Client(self.__options)
        try:
            self.__client.list()
        except BaseException:
            errmsg = "Unable to connect to server: {0}.".format(self.__host)
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    level='error',
                    msg=errmsg)
            else:
                self.sendlog(msg=errmsg, dst=self.__logtype, level='error')
            self.__error = {'code': 1, 'reason': errmsg}
            return(self.__error)

        if self.__logtype == 'file':
            self.sendlog(
                logfpath=self.__logfile,
                dst=self.__logtype,
                msg="Connected to {0} as {1}".format(
                    self.__host,
                    self.__login))
        else:
            self.sendlog(
                msg="Connected to {0} as {1}".format(
                    self.__host,
                    self.__login),
                dst=self.__logtype)

        self.__error = {'code': 0}

        return(self.__error)

    def check(self, target):
        '''
         Check if target exists on remote Webdav server

         :param target: Webdav target path
         :type  target: string

         :returns: It will returns result 'code' (and 'reason' if it fails)
         :rtype: dict
        '''
        if self.__error['code'] == 1:
            return(self.__error)

        try:
            if not self.__client.check(target):
                if self.__logtype == 'file':
                    self.sendlog(
                        logfpath=self.__logfile,
                        dst=self.__logtype,
                        level="warn",
                        msg="Unable to find {0}".format(target))
                else:
                    self.sendlog(
                        dst=self.__logtype,
                        level="warn",
                        msg="Unable to find {0}".format(target))

                self.__error = {
                    'code': 1, 'reason': "Unable to find {0}".format(target)}
            else:
                self.__error = {'code': 0}
        except WebDavException as exception:
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    level="error",
                    msg=exception)
            else:
                self.sendlog(dst=self.__logtype, level="error", msg=exception)

            self.__error = {
                'code': 1,
                'reason': "Unable to find {0}".format(target)}

        return(self.__error)

    def list(self, target):
        '''
         List share content

         :param target: Webdav target path
         :type  target: string

         :returns: It will returns result 'code' and 'reason' if it fails
         :rtype: dict

         :returns: It will returns list of files found
         :rtype: list
        '''
        if self.__error['code'] == 1:
            return(self.__error)

        try:
            remotefiles = self.__client.list(target)
        except WebDavException as exception:
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    level="warn",
                    msg=exception)
            else:
                self.sendlog(dst=self.__logtype, level="warn", msg=exception)
            self.__error = {'code': 1, 'reason': exception}
            return(self.__error)
        else:
            return(remotefiles)

    def getinfo(self, target):
        '''
         Get infos about file

         :param target: Webdav target path
         :type  target: string

         :returns: It will returns result 'code' and 'reason' if it fails
         :rtype: dict

         :returns: dict of remote file informations
         :rtype: dict
        '''
        if self.__error['code'] == 1:
            return(self.__error)

        try:
            fileinfos = self.__client.info(target)
        except WebDavException as exception:
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    level="warn",
                    msg=exception)
            else:
                self.sendlog(dst=self.__logtype, level="warn", msg=exception)
            self.__error = {'code': 1, 'reason': exception}
            return(self.__error)
        else:
            return(fileinfos)

    def download(self, remote, local):
        '''
         Downloading file from webdav

         :param remote: Webdav remote file path to get
         :type  remote: string

         :param local: local filesystem path where to put downloaded datas
         :type  local: string

         :returns: It will returns result 'code' and 'reason'
         :rtype: dict
        '''
        if self.__error['code'] == 1:
            return(self.__error)

        local = fpath.normpath(local)
        remote = fpath.normpath(remote)

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
                errstr = 'Directory {0} is empty, or the file is corrupted, skip downloading'.format(
                    remote)
                if self.__logtype == 'file':
                    self.sendlog(
                        logfpath=self.__logfile,
                        dst=self.__logtype,
                        level="warn",
                        msg=errstr)
                else:
                    self.sendlog(dst=self.__logtype, level="warn", msg=errstr)
                self.__error = {'code': 0, 'reason': errstr}
                return(self.__error)

        if fpath.exists(local):
            if not isdir:
                lfilesize = self.file_size(local)
                if int(lfilesize) == int(rfilesize):
                    errmsg = "File {0} already exists on local filesystem, skipping download.".format(
                        local)
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            msg=errmsg)
                    else:
                        self.sendlog(dst=self.__logtype, msg=errmsg)
                    self.__error = {'code': 0, 'reason': errmsg}
                    return(self.__error)
                else:
                    errmsg = "File {0} exists on local filesystem, but seems to be different, trying to download again.".format(
                        local)
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            level="warn",
                            msg=errmsg)
                    else:
                        self.sendlog(
                            dst=self.__logtype, level="warn", msg=errmsg)

        if not self.__client.check(remote):
            errmsg = "Remote file {0} not found.".format(remote)
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    level="warn",
                    msg=errmsg)
            else:
                self.sendlog(dst=self.__logtype, level="warn", msg=errmsg)
            self.__error = {'code': 1, 'reason': errmsg}
            return(self.__error)

        if isdir:
            infostr = 'Downloading directory {0}'.format(remote)
            self.make_local_dirs(local)
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    msg=infostr)
            else:
                self.sendlog(dst=self.__logtype, msg=infostr)

            for f in rdircontent:
                if f[-1] == "/":
                    f = f[:-1]

                remotefrecurse = "{0}/{1}".format(remote, f)
                localefrecurse = "{0}/{1}".format(local, f)

                self.download(remotefrecurse, localefrecurse)
                if self.__error['code'] == 1:
                    return(self.__error)

        else:
            infostr = 'Downloading file {0}'.format(remote)
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    msg=infostr)
            else:
                self.sendlog(dst=self.__logtype, msg=infostr)

            localdirdest = fpath.dirname(fpath.abspath(local))
            localdirdest = fpath.normpath(localdirdest)
            if not fpath.exists(localdirdest):
                self.make_local_dirs(localdirdest)

            try:
                self.__client.download(
                    remote_path=remote,
                    local_path=local,
                    progress=self.progress)
                # print console carriage return after progress bar
                # self.sendlog(dst='console', msg='')
                print('')
            except WebDavException as exception:
                if self.__logtype == 'file':
                    self.sendlog(
                        logfpath=self.__logfile,
                        dst=self.__logtype,
                        level="error",
                        msg=exception)
                else:
                    self.sendlog(
                        dst=self.__logtype,
                        level="error",
                        msg=exception)

                self.__error = {'code': 1, 'reason': exception}
                return(self.__error)

            lfilesize = self.file_size(local)

            if int(lfilesize) == int(rfilesize):
                if self.__logtype == 'file':
                    self.sendlog(
                        logfpath=self.__logfile,
                        dst=self.__logtype,
                        msg='File {0} downloaded correctly'.format(remote))
                else:
                    self.sendlog(
                        dst=self.__logtype,
                        msg='File {0} downloaded correctly'.format(remote))

                self.__error = {'code': 0}
            else:
                if self.__logtype == 'file':
                    self.sendlog(
                        logfpath=self.__logfile,
                        dst=self.__logtype,
                        level="warn",
                        msg='Download failed: partially retrieved.')
                else:
                    self.sendlog(
                        dst=self.__logtype,
                        level="warn",
                        msg='Download failed: partially retrieved.')

                fremove(local)
                self.__error = {
                    'code': 1, 'reason': "Download failed: partially retrieved."}

            return(self.__error)

        return(self.__error)

    def upload(self, local, remote, recurse=False):
        '''
         Uploading file to Webdav

         :param local: local resource's filesystem path to upload
         :type  local: string

         :param remote: Webdav remote file path where to put the file
         :type  remote: string

         :param recurse: Internal use only
         :type  recurse: boolean

         :returns: It will returns result 'code' and 'reason'
         :rtype: dict
        '''

        if self.__error['code'] == 1:
            return(self.__error)

        if not fpath.exists(local):
            errstr = 'Unable to find locale file {lfile}. Aborting upload..'.format(
                lfile=local)
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    level="error",
                    msg=errstr)
            else:
                self.sendlog(dst=self.__logtype, level="error", msg=errstr)
            self.__error = {'code': 1, 'reason': errstr}
            return(self.__error)

        local_isdir = fpath.isdir(local)

        rfilename = fpath.basename(fpath.normpath(local))
        if local_isdir:
            rfiledst = "{}/{}".format(remote, rfilename)
        else:
            if not recurse:
                rfiledst = "{}/{}".format(remote, rfilename)
            else:
                rfiledst = str(remote)

        rfiledst = fpath.normpath(rfiledst)

        infostr = 'Uploading {} to {}'.format(local, rfiledst)
        if self.__logtype == 'file':
            self.sendlog(
                logfpath=self.__logfile,
                dst=self.__logtype,
                msg=infostr)
        else:
            self.sendlog(dst=self.__logtype, msg=infostr)

        if not self.__client.check(rfiledst):
            if local_isdir:
                mkdires = self.createdir(rfiledst)
                if mkdires['code'] == 1:
                    errmsg = 'Unable to create remote directory {}'.format(
                        rfiledst)
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            level="warn",
                            msg=errmsg)
                    else:
                        self.sendlog(
                            dst=self.__logtype, level="warn", msg=errmsg)

                    self.__error = {'code': 1, 'reason': errmsg}
                    return(self.__error)

                remote = str(rfiledst)
                for file_ in listdir(local):
                    recursed_local = "{}/{}".format(local, file_)
                    recursed_local = fpath.normpath(recursed_local)

                    if fpath.isdir(recursed_local):
                        recursed_remote = rfiledst
                    else:
                        recursed_remote = "{}/{}".format(rfiledst, file_)
                    recursed_remote = fpath.normpath(recursed_remote)

                    self.upload(
                        local=recursed_local,
                        remote=recursed_remote,
                        recurse=True)
            else:
                try:
                    self.__client.upload(
                        remote_path=rfiledst,
                        local_path=local,
                        progress=self.progress)
                    # print console carriage return after progress bar
                    # self.sendlog(dst='console', msg='')
                    print('')
                except WebDavException as exception:
                    if re.match(
                        'Remote parent for.* not found',
                            str(exception)):
                        parentdir = fpath.dirname(rfiledst)
                        res = self.createdir(parentdir)
                        if res['code'] == 1:
                            errmsg = "Unable to create remote parent directory {}.".format(
                                parentdir)
                            if self.__logtype == 'file':
                                self.sendlog(
                                    logfpath=self.__logfile,
                                    dst=self.__logtype,
                                    level='error',
                                    msg=errmsg)
                            else:
                                self.sendlog(
                                    msg=errmsg, dst=self.__logtype, level='error')
                            self.__error = {'code': 1, 'reason': errmsg}
                            return(self.__error)
                        else:
                            try:
                                self.__client.upload(
                                    remote_path=rfiledst, local_path=local, progress=self.progress)
                                # print console carriage return after progress bar
                                # self.sendlog(dst='console', msg='')
                                print('')
                            except WebDavException as exception:
                                if self.__logtype == 'file':
                                    self.sendlog(
                                        logfpath=self.__logfile,
                                        dst=self.__logtype,
                                        level="error",
                                        msg=exception)
                                else:
                                    self.sendlog(
                                        dst=self.__logtype, level="error", msg=exception)
                                self.__error = {'code': 1, 'reason': exception}
                                return(self.__error)
                    else:
                        if self.__logtype == 'file':
                            self.sendlog(
                                logfpath=self.__logfile,
                                dst=self.__logtype,
                                level="error",
                                msg=exception)
                        else:
                            self.sendlog(
                                dst=self.__logtype, level="error", msg=exception)
                        self.__error = {'code': 1, 'reason': exception}
                        return(self.__error)

                remoteinfo = self.getinfo(rfiledst)
                if 'code' in remoteinfo:
                    errstr = remoteinfo['reason']
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            level="error",
                            msg=errstr)
                    else:
                        self.sendlog(
                            dst=self.__logtype, level="warn", msg=errstr)

                    self.__error = {'code': 1, 'reason': errstr}
                    return(self.__error)

                lfsize = self.file_size(local)
                if lfsize == int(remoteinfo['size']):
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            msg='File {0} uploaded correctly'.format(rfiledst))
                    else:
                        self.sendlog(
                            dst=self.__logtype,
                            msg='File {0} uploaded correctly'.format(rfiledst))

                    self.__error = {'code': 0}
                else:
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            level="warn",
                            msg='Upload failed: partially sent.')
                    else:
                        self.sendlog(
                            dst=self.__logtype,
                            level="warn",
                            msg='Upload failed: partially sent.')

                    self.delete(rfiledst)
                    self.__error = {
                        'code': 1, 'reason': "Upload failed: partially sent."}

                return(self.__error)

            if local_isdir:
                info = "Checking directory {} overall upload state...".format(
                    rfiledst)
                if self.__logtype == 'file':
                    self.sendlog(
                        logfpath=self.__logfile,
                        dst=self.__logtype,
                        msg=info)
                else:
                    self.sendlog(dst=self.__logtype, msg=info)

                remoteflist = self.list_recurse(rfiledst)
                for f in remoteflist:
                    finfo = self.getinfo(f)
                    if 'code' in finfo:
                        return(self.__error)

                    lfilename = fpath.basename(f)
                    lbasepath = fpath.dirname(
                        fpath.abspath(f)).replace(
                        remote, '')
                    lbasepath = "{}/{}".format(local, lbasepath)
                    lbasepath = fpath.normpath(lbasepath)
                    lfile = "{}/{}".format(lbasepath, lfilename)
                    lfile = fpath.normpath(lfile)
                    lfsize = self.file_size(lfile)

                    if not fpath.isdir(lfile):
                        if lfsize != int(finfo['size']):
                            msg = 'Upload failed: file {} partially sent.'.format(
                                f)
                            if self.__logtype == 'file':
                                self.sendlog(
                                    logfpath=self.__logfile,
                                    dst=self.__logtype,
                                    level="warn",
                                    msg=msg)
                            else:
                                self.sendlog(
                                    dst=self.__logtype, level="warn", msg=msg)
                            self.delete(f)
                            self.__error = {'code': 1, 'reason': msg}

                if self.__error['code'] == 0:
                    msg = 'Uploading {} Success.'.format(local)
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            msg=msg)
                    else:
                        self.sendlog(dst=self.__logtype, msg=msg)
                    self.__error = {'code': 0, 'reason': msg}
                else:
                    msg = 'Upload failed: directory {} partially sent.'.format(
                        local)
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            level="warn",
                            msg=msg)
                    else:
                        self.sendlog(dst=self.__logtype, level="warn", msg=msg)

                    self.__error = {'code': 1, 'reason': msg}
        else:
            if self.__client.is_dir(rfiledst):
                remoteflist = self.list_recurse(rfiledst)

                lclfiles = self.list_files_ldir(local)
                for file_ in lclfiles:
                    basepath = fpath.dirname(fpath.abspath(file_))
                    torem = fpath.dirname(fpath.abspath(local))
                    basepath = basepath.replace(torem, '')
                    filename = fpath.basename(file_)
                    rpath = '{}/{}/{}'.format(remote, basepath, filename)
                    rpath = fpath.normpath(rpath)

                    if rpath not in remoteflist:
                        self.upload(local=file_, remote=rpath, recurse=True)
                    else:
                        lfsize = self.file_size(file_)
                        finfo = self.getinfo(rpath)
                        if 'code' in finfo:
                            return(self.__error)

                        if lfsize != int(finfo['size']):
                            msg = 'Remote file {} mismatch local file {} trying to update.'.format(
                                rpath, file_)
                            if self.__logtype == 'file':
                                self.sendlog(
                                    logfpath=self.__logfile,
                                    dst=self.__logtype,
                                    level="warn",
                                    msg=msg)
                            else:
                                self.sendlog(
                                    dst=self.__logtype, level="warn", msg=msg)
                            upres = self.upload(
                                local=file_, remote=rpath, recurse=True)
                            if upres['code'] == 1:
                                msg = 'Upload failed for {}, partially sent.'.format(
                                    file_)
                                if self.__logtype == 'file':
                                    self.sendlog(
                                        logfpath=self.__logfile, dst=self.__logtype, level="warn", msg=msg)
                                else:
                                    self.sendlog(
                                        dst=self.__logtype, level="warn", msg=msg)
                        else:
                            errmsg = "File {0} already exists on remote, skipping upload.".format(
                                file_)
                            if self.__logtype == 'file':
                                self.sendlog(
                                    logfpath=self.__logfile, dst=self.__logtype, msg=errmsg)
                            else:
                                self.sendlog(dst=self.__logtype, msg=errmsg)
                            self.__error = {'code': 0, 'reason': errmsg}
            else:
                lfsize = self.file_size(local)
                finfo = self.getinfo(rfiledst)
                if 'code' in finfo:
                    return(self.__error)

                if lfsize != int(finfo['size']):
                    msg = 'Remote file {} mismatch local file {} trying to update.'.format(
                        rfiledst, local)
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            level="warn",
                            msg=msg)
                    else:
                        self.sendlog(dst=self.__logtype, level="warn", msg=msg)
                    try:
                        self.__client.upload(
                            remote_path=rfiledst,
                            local_path=local,
                            progress=self.progress)
                        # print console carriage return after progress bar
                        # self.sendlog(dst='console', msg='')
                        print('')
                    except WebDavException as exception:
                        if re.match(
                            'Remote parent for.* not found',
                                str(exception)):
                            parentdir = fpath.dirname(fpath.abspath(rfiledst))
                            res = self.createdir(parentdir)
                            if res['code'] == 1:
                                errmsg = "Unable to create remote parent directory {}.".format(
                                    parentdir)
                                if self.__logtype == 'file':
                                    self.sendlog(
                                        logfpath=self.__logfile,
                                        dst=self.__logtype,
                                        level='error',
                                        msg=errmsg)
                                else:
                                    self.sendlog(
                                        msg=errmsg, dst=self.__logtype, level='error')
                                self.__error = {'code': 1, 'reason': errmsg}
                                return(self.__error)
                            else:
                                try:
                                    self.__client.upload(
                                        remote_path=rfiledst, local_path=local, progress=self.progress)
                                    # print console carriage return after progress bar
                                    # self.sendlog(dst='console', msg='')
                                    print('')
                                except WebDavException as exception:
                                    if self.__logtype == 'file':
                                        self.sendlog(
                                            logfpath=self.__logfile, dst=self.__logtype, level="error", msg=exception)
                                    else:
                                        self.sendlog(
                                            dst=self.__logtype, level="error", msg=exception)
                                    self.__error = {
                                        'code': 1, 'reason': exception}
                                    return(self.__error)
                        else:
                            if self.__logtype == 'file':
                                self.sendlog(
                                    logfpath=self.__logfile,
                                    dst=self.__logtype,
                                    level="error",
                                    msg=exception)
                            else:
                                self.sendlog(
                                    dst=self.__logtype, level="error", msg=exception)
                            self.__error = {'code': 1, 'reason': exception}
                            return(self.__error)

                    remoteinfo = self.getinfo(rfiledst)
                    if 'code' in remoteinfo:
                        errstr = remoteinfo['reason']
                        if self.__logtype == 'file':
                            self.sendlog(
                                logfpath=self.__logfile,
                                dst=self.__logtype,
                                level="error",
                                msg=errstr)
                        else:
                            self.sendlog(
                                dst=self.__logtype, level="warn", msg=errstr)

                        self.__error = {'code': 1, 'reason': errstr}
                        return(self.__error)

                    lfsize = self.file_size(local)
                    if lfsize == int(remoteinfo['size']):
                        if self.__logtype == 'file':
                            self.sendlog(
                                logfpath=self.__logfile,
                                dst=self.__logtype,
                                msg='File {0} uploaded correctly'.format(rfiledst))
                        else:
                            self.sendlog(
                                dst=self.__logtype,
                                msg='File {0} uploaded correctly'.format(rfiledst))

                        self.__error = {'code': 0}
                    else:
                        if self.__logtype == 'file':
                            self.sendlog(
                                logfpath=self.__logfile,
                                dst=self.__logtype,
                                level="warn",
                                msg='Upload failed: partially sent.')
                        else:
                            self.sendlog(
                                dst=self.__logtype,
                                level="warn",
                                msg='Upload failed: partially sent.')

                        self.delete(rfiledst)
                        self.__error = {
                            'code': 1, 'reason': "Upload failed: partially sent."}
                else:
                    errmsg = "File {0} already exists on remote, skipping upload.".format(
                        local)
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            msg=errmsg)
                    else:
                        self.sendlog(dst=self.__logtype, msg=errmsg)
                    self.__error = {'code': 0, 'reason': errmsg}

        return(self.__error)

    def createdir(self, target):
        '''
         Create directory on Webdav

         :param target: Webdav target path
         :type  target: string

         :returns: It will returns result 'code' and 'reason'
         :rtype: dict
        '''
        if self.__error['code'] == 1:
            return(self.__error)

        try:
            self.__client.mkdir(target)
        except WebDavException as exception:
            if re.match('Remote parent for.* not found', str(exception)):
                parentdir = fpath.dirname(fpath.abspath(target))
                res = self.createdir(parentdir)
                if res['code'] == 1:
                    errmsg = "Unable to create remote parent directory {}.".format(
                        parentdir)
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            level='error',
                            msg=errmsg)
                    else:
                        self.sendlog(
                            msg=errmsg, dst=self.__logtype, level='error')
                    self.__error = {'code': 1, 'reason': errmsg}
                else:
                    res = self.createdir(target)
                    if res['code'] == 1:
                        errmsg = "Unable to create remote directory {}.".format(
                            target)
                        if self.__logtype == 'file':
                            self.sendlog(
                                logfpath=self.__logfile,
                                dst=self.__logtype,
                                level='error',
                                msg=errmsg)
                        else:
                            self.sendlog(
                                msg=errmsg, dst=self.__logtype, level='error')
                        self.__error = {'code': 1, 'reason': errmsg}
            else:
                errmsg = "Unable to create remote directory {}.".format(target)
                if self.__logtype == 'file':
                    self.sendlog(
                        logfpath=self.__logfile,
                        dst=self.__logtype,
                        level='error',
                        msg=errmsg)
                else:
                    self.sendlog(msg=errmsg, dst=self.__logtype, level='error')
                self.__error = {'code': 1, 'reason': errmsg}
        else:
            msg = "Directory {} created.".format(target)
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    msg=msg)
            else:
                self.sendlog(msg=msg, dst=self.__logtype)

            try:
                self.__client.publish(target)
            except BaseException:
                errmsg = "Unable to publish resource {}.".format(target)
                if self.__logtype == 'file':
                    self.sendlog(
                        logfpath=self.__logfile,
                        dst=self.__logtype,
                        level='error',
                        msg=errmsg)
                else:
                    self.sendlog(msg=errmsg, dst=self.__logtype, level='error')
                self.__error = {'code': 1, 'reason': errmsg}
            else:
                self.__error = {'code': 0, 'reason': msg}

        return(self.__error)

    def delete(self, target):
        '''
         Delete resource on Webdav

         :param target: Webdav target path
         :type  target: string

         :returns: It will returns result 'code' and 'reason'
         :rtype: dict
        '''

        if self.__error['code'] == 1:
            return(self.__error)

        target = fpath.normpath(target)

        msg = "Removing {}.".format(target)
        if self.__logtype == 'file':
            self.sendlog(logfpath=self.__logfile, dst=self.__logtype, msg=msg)
        else:
            self.sendlog(dst=self.__logtype, msg=msg)

        if not self.__client.check(target):
            errmsg = "Remote resource {0} not found.".format(target)
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    level="warn",
                    msg=errmsg)
            else:
                self.sendlog(dst=self.__logtype, msg=errmsg, level="warn")
            self.__error = {'code': 1, 'reason': errmsg}
        else:
            try:
                self.__client.clean(target)
            except BaseException:
                errmsg = "Unable to remove remote resource {}.".format(target)
                if self.__logtype == 'file':
                    self.sendlog(
                        logfpath=self.__logfile,
                        dst=self.__logtype,
                        level='error',
                        msg=errmsg)
                else:
                    self.sendlog(msg=errmsg, dst=self.__logtype, level='error')
                self.__error = {'code': 1, 'reason': errmsg}
            else:
                msg = "Remote resource {} has been removed.".format(target)
                if self.__logtype == 'file':
                    self.sendlog(
                        logfpath=self.__logfile,
                        dst=self.__logtype,
                        msg=msg)
                else:
                    self.sendlog(msg=msg, dst=self.__logtype)
                self.__error = {'code': 0, 'reason': msg}

        return(self.__error)

    def duplicate(self, target, twin):
        '''
         Duplicate a resource on Webdav

         :param target: Webdav source target path
         :type  target: string

         :param twin: Webdav destination target path
         :type  twin: string

         :returns: It will returns result 'code' and 'reason'
         :rtype: dict
        '''

        if self.__error['code'] == 1:
            return(self.__error)

        target = fpath.normpath(target)

        if not self.__client.check(target):
            errmsg = "Remote resource {0} not found.".format(target)
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    level="warn",
                    msg=errmsg)
            else:
                self.sendlog(dst=self.__logtype, level="warn", msg=errmsg)
            self.__error = {'code': 1, 'reason': errmsg}
            return(self.__error)

        msg = "Copying {} to {}.".format(target, twin)
        if self.__logtype == 'file':
            self.sendlog(logfpath=self.__logfile, dst=self.__logtype, msg=msg)
        else:
            self.sendlog(dst=self.__logtype, msg=msg)

        try:
            self.__client.copy(remote_path_from=target, remote_path_to=twin)
        except WebDavException as exception:
            if re.match('Remote parent for.* not found', str(exception)):
                parentdir = fpath.dirname(fpath.abspath(twin))
                res = self.createdir(parentdir)
                if res['code'] == 1:
                    errmsg = "Unable to create remote parent directory {}.".format(
                        parentdir)
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            level='error',
                            msg=errmsg)
                    else:
                        self.sendlog(
                            msg=errmsg, dst=self.__logtype, level='error')
                    self.__error = {'code': 1, 'reason': errmsg}
                    return(self.__error)
                else:
                    try:
                        self.__client.copy(
                            remote_path_from=target, remote_path_to=twin)
                    except WebDavException as exception:
                        errmsg = "Unable to duplicate remote resource {} to {}.".format(
                            target, twin)
                        if self.__logtype == 'file':
                            self.sendlog(
                                logfpath=self.__logfile,
                                dst=self.__logtype,
                                level='error',
                                msg=errmsg)
                        else:
                            self.sendlog(
                                msg=errmsg, dst=self.__logtype, level='error')
                        self.__error = {'code': 1, 'reason': errmsg}
                    else:
                        msg = "Remote resource {} has been copied to remote location {}.".format(
                            target, twin)
                        if self.__logtype == 'file':
                            self.sendlog(
                                logfpath=self.__logfile, dst=self.__logtype, msg=msg)
                        else:
                            self.sendlog(msg=msg, dst=self.__logtype)
                        self.__error = {'code': 0, 'reason': msg}
            else:
                errmsg = "Unable to duplicate remote resource {} to {}.".format(
                    target, twin)
                if self.__logtype == 'file':
                    self.sendlog(
                        logfpath=self.__logfile,
                        dst=self.__logtype,
                        level='error',
                        msg=errmsg)
                else:
                    self.sendlog(msg=errmsg, dst=self.__logtype, level='error')
                self.__error = {'code': 1, 'reason': errmsg}
        else:
            msg = "Remote resource {} has been copied to remote location {}.".format(
                target, twin)
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    msg=msg)
            else:
                self.sendlog(msg=msg, dst=self.__logtype)
            self.__error = {'code': 0, 'reason': msg}

        return(self.__error)

    def move(self, target, new):
        '''
         Move a resource on Webdav

         :param target: Webdav source target path
         :type  target: string

         :param new: Webdav destination target path
         :type  new: string

         :returns: It will returns result 'code' and 'reason'
         :rtype: dict
        '''

        if self.__error['code'] == 1:
            return(self.__error)

        target = fpath.normpath(target)

        if not self.__client.check(target):
            errmsg = "Remote resource {0} not found.".format(target)
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    level="warn",
                    msg=errmsg)
            else:
                self.sendlog(dst=self.__logtype, level="warn", msg=errmsg)
            self.__error = {'code': 1, 'reason': errmsg}
            return(self.__error)

        msg = "Moving {} to {}.".format(target, new)
        if self.__logtype == 'file':
            self.sendlog(logfpath=self.__logfile, dst=self.__logtype, msg=msg)
        else:
            self.sendlog(dst=self.__logtype, msg=msg)

        try:
            self.__client.move(remote_path_from=target, remote_path_to=new)
        except WebDavException as exception:
            if re.match('Remote parent for.* not found', str(exception)):
                parentdir = fpath.dirname(fpath.abspath(new))
                res = self.createdir(parentdir)
                if res['code'] == 1:
                    errmsg = "Unable to create remote parent directory {}.".format(
                        parentdir)
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            level='error',
                            msg=errmsg)
                    else:
                        self.sendlog(
                            msg=errmsg, dst=self.__logtype, level='error')
                    self.__error = {'code': 1, 'reason': errmsg}
                    return(self.__error)
                else:
                    try:
                        self.__client.move(
                            remote_path_from=target, remote_path_to=new)
                    except WebDavException as exception:
                        errmsg = "Unable to move remote resource {} to {}.".format(
                            target, new)
                        if self.__logtype == 'file':
                            self.sendlog(
                                logfpath=self.__logfile,
                                dst=self.__logtype,
                                level='error',
                                msg=errmsg)
                        else:
                            self.sendlog(
                                msg=errmsg, dst=self.__logtype, level='error')
                        self.__error = {'code': 1, 'reason': errmsg}
                    else:
                        msg = "Remote resource {} has been moved to remote location {}.".format(
                            target, new)
                        if self.__logtype == 'file':
                            self.sendlog(
                                logfpath=self.__logfile, dst=self.__logtype, msg=msg)
                        else:
                            self.sendlog(msg=msg, dst=self.__logtype)
                        self.__error = {'code': 0, 'reason': msg}
            else:
                errmsg = "Unable to move remote resource {} to {}.".format(
                    target, new)
                if self.__logtype == 'file':
                    self.sendlog(
                        logfpath=self.__logfile,
                        dst=self.__logtype,
                        level='error',
                        msg=errmsg)
                else:
                    self.sendlog(msg=errmsg, dst=self.__logtype, level='error')
                self.__error = {'code': 1, 'reason': errmsg}
        else:
            msg = "Remote resource {} has been moved to remote location {}.".format(
                target, new)
            if self.__logtype == 'file':
                self.sendlog(
                    logfpath=self.__logfile,
                    dst=self.__logtype,
                    msg=msg)
            else:
                self.sendlog(msg=msg, dst=self.__logtype)
            self.__error = {'code': 0, 'reason': msg}

        return(self.__error)

    def search(self, target, path=False, found=False):
        '''
         Search for file or directory recursively on Webdav

         :param target: Searching word
         :type  target: string

         :param   path: Webdav path where looking for target
         :type    path: string
         :default path: False

         :param found: internal use only
         :type  found: boolean

         :returns: It will returns result 'code' and 'reason' if it fails
         :rtype: dict

         :returns: list of file paths which contains target
         :rtype: list
        '''

        if not found:
            found = []

        if path:
            currdir = str(path)
        else:
            currdir = "/"

        info = "Listing directory {}".format(currdir)
        if self.__logtype == 'file':
            self.sendlog(
                logfpath=self.__logfile,
                dst=self.__logtype,
                msg=info)
        else:
            self.sendlog(dst=self.__logtype, msg=info)

        remotefiles = self.list(currdir)
        if 'code' in remotefiles:
            return(self.__error)

        if len(remotefiles) > 0:
            for f in remotefiles:
                if f[-1] == "/":
                    f = f[:-1]

                if currdir != '/':
                    currfile = "{0}/{1}".format(currdir, f)
                else:
                    currfile = "/{0}".format(f)

                if target in f or target == f:
                    found.append("{0}/{1}".format(currdir, f))
                if self.__client.is_dir(currfile):
                    found = self.search(target, currfile, found)

            uniqueList = []
            for i in found:
                if i not in uniqueList:
                    i = fpath.normpath(i)
                    uniqueList.append(i)
            found = uniqueList

        return(found)

    def list_recurse(self, path, found=False):
        '''
         List Webdav path recursively

         :param path: Webdav path to list files
         :type  path: string

         :param found: internal use only
         :type  found: boolean

         :returns: It will returns result 'code' and 'reason' if it fails
         :rtype: dict

         :returns: list of file paths which contains target
         :rtype: list
        '''

        if not found:
            found = []

        currdir = str(path)

        remotefiles = self.list(currdir)
        if 'code' in remotefiles:
            return(self.__error)

        if len(remotefiles) > 0:
            for f in remotefiles:
                if f[-1] == "/":
                    f = f[:-1]

                if currdir != '/':
                    currfile = "{0}/{1}".format(currdir, f)
                else:
                    currfile = "/{0}".format(f)

                if self.__client.is_dir(currfile):
                    found = self.list_recurse(currfile, found)

                found.append("{0}/{1}".format(currdir, f))

            uniqueList = []
            for i in found:
                if i not in uniqueList:
                    i = fpath.normpath(i)
                    uniqueList.append(i)
            found = uniqueList

        return(found)

    def list_files_ldir(self, directory_path, pattern="*"):
        '''
         Pattern can be used to look for specific files like .mp3 etc.

         :param directory_path: local filesystem directory path
         :type  directory_path: string

         :param pattern: pattern filter to use for the search
         :type  pattern: string

         :returns: list of absolute file paths found
         :rtype: list
        '''

        files = []
        for dirpath, dirnames, filenames in walk(directory_path):
            for file_name in fnfilter(filenames, pattern):
                filepath = yield fpath.join(dirpath, file_name)
                files.append(filepath)
        return(files)

    def make_local_dirs(self, directory):
        '''
         Creates local filsystem directories recursively

         :param directory: local filesystem directory path
         :type  directory: string

         :returns: It will returns result 'code' and 'reason'
         :rtype: dict
        '''
        if not fpath.exists(directory):
            try:
                makedirs(directory, 0o750)
            except PermissionError as e:
                errmsg = "Unable to create local directory {0}: {1}".format(
                    directory, e.strerror)
                if self.__logtype == 'file':
                    self.sendlog(
                        logfpath=self.__logfile,
                        dst=self.__logtype,
                        level="error",
                        msg=errmsg)
                else:
                    self.sendlog(dst=self.__logtype, level="error", msg=errmsg)
                self.__error = {'code': 1, 'reason': errmsg}
                return(self.__error)
            except OSError as exception:
                if exception.errno != exception.errno.EEXIST:
                    errmsg = "Unable to create local directory {0}: {1}".format(
                        directory, exception)
                    if self.__logtype == 'file':
                        self.sendlog(
                            logfpath=self.__logfile,
                            dst=self.__logtype,
                            level="error",
                            msg=errmsg)
                    else:
                        self.sendlog(
                            dst=self.__logtype, level="error", msg=errmsg)
                    self.__error = {'code': 1, 'reason': errmsg}
                    return(self.__error)


if __name__ == "__main__":
    """
    Main part used if self-executed
    """
