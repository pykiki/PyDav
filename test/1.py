#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from sys import version_info
from os import path as fpath
import signal
import argparse
from sys import argv
try:
    from PyDav import tools
except BaseException:
    print('Please Install PyDav library.')
    exit(1)

__author__ = "Alain Maibach"
__status__ = "Tests purpose only"

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
    if len(argv) <= 1:
        pass

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

    # connecting to webdav
    webdavClient = tools.core(configpath)
    connected = webdavClient.connect()
    if connected['code'] != 0:
        del(webdavClient)
        exit(0)

    # print local files destination
    print(webdavClient.localPath)

    # print remote files destination
    print(webdavClient.webdavShare)

    # change local files destination
    # webdavClient.localPath = "toto"

    # close connection
    # del(webdavClient)
    # exit(0)

    # ############################
    # # list target path content #
    # ############################
    remotefiles = webdavClient.remote_list()
    if remotefiles['code'] != 0:
        del(webdavClient)
        exit(remotefiles['code'])
    else:
        remotefiles = remotefiles['content']
    print(remotefiles)

    '''
    ###################################################################
    # List a different target than default path defined in config.ini #
    ###################################################################
    webdavClient.webdavShare = '{}/Medias'.format(webdavClient.webdavShare)
    remotefiles = webdavClient.remote_list()
     if remotefiles['code'] != 0:
      del(webdavClient)
      exit(remotefiles['code'])
     else:
      remotefiles = remotefiles['content']
     print(remotefiles)
    '''

    if len(remotefiles) > 0:
        '''
         We will look for a matching expr
        '''
        word = 'Vrac'
        res_found = webdavClient.remote_search(word)
        err = False
        if res_found['code'] == 0:
            for rfilename in res_found['content']:
                fileloc = "{0}/{1}".format(webdavClient.localPath,
                                           rfilename)
                ######################
                # Downloading a file #
                ######################
                res = webdavClient.download(rfilename, fileloc)
                if res['code'] == 1:
                    err = True
            if err:
                print(
                    "Some errors occured during download.")
    else:
        print("No remote files or directories found")

    #####################
    # Uploading a file ##
    #####################
    resources = [
                 '/home/amaibach/Downloads/mp3/',
                 '/home/amaibach/Downloads/class-example.py',
                 '/home/amaibach/Downloads/mp3/'
                ]
    for resource in resources:
      res = webdavClient.upload(resource)
      if res['code'] == 1:
          del(webdavClient)
          exit(1)

    ################
    # Copying file #
    ################
    file2cp = 'mp3'
    dst = 'toto-1/zigzag/zizi/mp3'
    rescp = webdavClient.remote_duplicate(file2cp, dst)
    if rescp['code'] != 0:
        del(webdavClient)
        exit(1)

    #################
    #  Moving  file #
    #################
    file2mv = 'toto-1/zigzag/zizi/mp3'
    dst = 'toto-2/zigzag/mp3'
    resmv = webdavClient.remote_move(file2mv, dst)
    if resmv['code'] != 0:
        del(webdavClient)
        exit(1)

    ######################
    # Downloading a file #
    ######################
    file2dl = 'toto-2/zigzag/mp3'
    remotefile = "{}/{}".format(webdavClient.webdavShare, file2dl)
    localfile = "{0}/{1}".format(webdavClient.localPath, remotefile)
    if webdavClient.download(remotefile, localfile)['code'] == 1:
        del(webdavClient)
        exit(1)

    #################
    # Removing file #
    #################

    err = False
    file2del = ['toto-1/', 'toto-2/', 'mp3', 'class-example.py']

    for f in file2del:
        resdel = webdavClient.remote_remove(f)
        if resdel['code'] != 0:
            err = True

    if not err:
        remotefiles = webdavClient.remote_list()
        if remotefiles['code'] != 0:
            del(webdavClient)
            exit(remotefiles['code'])
        else:
            remotefiles = remotefiles['content']
        print(remotefiles)
    else:
        print("WARN: Some errors occured during remove.")
        exit(1)
