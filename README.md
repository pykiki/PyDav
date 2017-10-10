PyDav
=====

Webdav cli client library.

Based on webdavclient library:*https://github.com/CloudPolis/webdav-client-python*

System Requirement
------------------
<p>
 If you do not use your packager to install python libraries
</p>

 - libcurl4-openssl devel sources
 - libxml2 devel sources
 - libxslt1 devel sources

Python library dependencies
------------------------------

<p>
 - argcomplete>=1.9.2
 - lxml>=3.8.0
 - pycurl>=7.43.0
 - webdavclient>=1.0.8
</p>

Install
-------

<p>
This will install python libraries and pydav-client script.
</p>

```bash

# ArchLinux
$ sudo pacman -Sy --needed libxslt python-lxml python-pycurl python-argcomplete

# Debian
$ sudo apt-get update
$ sudo apt-get install libcurl4-openssl-dev libxml2-dev libxslt1-dev

# Manually build it into specific folder
#$ /usr/bin/env python3 setup.py build --build-base=/path/to/pybuild/foo-1.0

# Install python package
$ /usr/bin/env python3 setup.py install --user --record installed-files.txt
$ export PYTHONPATH="$(echo $HOME/.local/lib/python3.6/site-packages)"
$ export PATH=${HOME}/.local/bin:${PATH}
# or
$ /usr/bin/env python3 setup.py install --home=~ --record installed-files.txt
$ export PYTHONPATH="$(echo $HOME/.local/lib/python3.6/site-packages)"
$ export PATH=${HOME}/.local/bin:${PATH}
# or
$ /usr/bin/env python3 setup.py install --prefix=/usr/local --record installed-files.txt
$ export PYTHONPATH="$(echo /usr/local/lib/python3.6/site-packages)"
$ export PATH=/usr/local/bin:${PATH}
```

<p>
If you use a custom install path, do not forget to setup PYTHONPATH and PYTHONHOME
```bash
# if you used it with --prefix=/usr/local
$ export PYTHONPATH="/usr/local/lib/python3.X"
```
</p>

:notebook: For more installation options, see: https://docs.python.org/3/install/index.html

<p>
Your packages will be installed under:

```bash
echo $(find "$(find "$(/usr/bin/env python3 -c 'import sys; print(sys.prefix)')/lib/" -maxdepth 1 -name 'python3*')/site-packages/" -maxdepth 1 -iname "PyDav*" -type d)
# or
echo $(find "$(find "$(/usr/bin/env python3 -c 'import sys; print(sys.exec_prefix)')/lib/" -maxdepth 1 -name 'python3*')/site-packages/" -maxdepth 1 -iname "PyDav*" -type d)
```

</p>

Uninstall
---------

```bash

$ cat installed-files.txt | xargs sudo rm -rf
# or if you do not have installed-files.txt
$ pip uninstall PyDav --user
$ pip uninstall webdavclient argcomplete --user

```

Script Use
----------

<p>
For a Quick&Easy use, call pydav-client from cli.
</p>

<aside class="warning">
  :notebook: All command launched with this script will impact remote Webdav in the limit of the directory
  defined as the sharing point in **config.ini** section **[webdav]**, option **'share'**.
</aside>

### Help

```bash
pydav-client -h

usage: /home/amaibach/.virtualenvs/pydav/bin/pydav-client -c [/path/to/config.ini] (-l|-s|-u|-d|-i|-m|-r)|(--list|--search|--upload|--download|--duplicate|--move|--delete)

Webdav client

optional arguments:
  -h, --help            show this help message and exit
  -c path/to/config.ini, --config path/to/config.ini
                        PyDav config file path
  -l [(optional value to specify Webdav path in share directory)], --list [(optional value to specify Webdav path in share directory)]
                        Allow to list Webdav share content
  -s [[word] (Webdav/share/searching/path/dir) [[word] (Webdav/share/searching/path/dir) ...]], --search [[word] (Webdav/share/searching/path/dir) [[word] (Webdav/share/searching/path/dir) ...]]
                        Allow to search for a resource containing a word
  -u [[/path/to/local/resource] (Webdav/share/path/dir) [[/path/to/local/resource] (Webdav/share/path/dir) ...]], --upload [[/path/to/local/resource] (Webdav/share/path/dir) [[/path/to/local/resource] (Webdav/share/path/dir) ...]]
                        Upload a resource to your Webdav share directory
  -d [[Webdav/share/resource] (path/to/localdest) [[Webdav/share/resource] (path/to/localdest) ...]], --download [[Webdav/share/resource] (path/to/localdest) [[Webdav/share/resource] (path/to/localdest) ...]]
                        Download a resource from your Webdav share directory
  -i [[webdav/share/src] [webdav/share/dst] [[webdav/share/src] [webdav/share/dst] ...]], --duplicate [[webdav/share/src] [webdav/share/dst] [[webdav/share/src] [webdav/share/dst] ...]]
                        Duplicate a Webdav resource
  -m [[webdav/share/src] [webdav/share/dst] [[webdav/share/src] [webdav/share/dst] ...]], --move [[webdav/share/src] [webdav/share/dst] [[webdav/share/src] [webdav/share/dst] ...]]
                        Move a Webdav resource
  -r webdav/share/resource, --delete webdav/share/resource
                        Remove a Webdav resource

```

### List resources

<p>
To list webdav path resources you can use -l or --list option.

If you invoke -l without value behind, you will list recursively all your Webdav
share path defined in config.ini

If you want to only list a specific path **in** your Webdav share path you can
add the path (which will be add after your Webdav root share path defined in **config.ini**
section *[webdav]*, option *'share'*) after the -l/--list option.
</p>

```bash
config="~/Downloads/pydav/configs/config-lan.ini"
cmd="pydav-client -c $config"

$cmd -l
$cmd --list documents
```

### Search for resources

<p>
</p>

```bash
config="~/Downloads/pydav/configs/config-lan.ini"
cmd="pydav-client -c $config"

$cmd -s .txt documents
$cmd --search .txt documents/
```

### Uploading resources

<p>
</p>

```bash
config="~/Downloads/pydav/configs/config-lan.ini"
cmd="pydav-client -c $config"

$cmd --upload ~/Downloads/photos/
$cmd -u ~/Downloads/class-example.py scripts/
```

### Downloading resources

<p>
</p>

```bash
config="~/Downloads/pydav/configs/config-lan.ini"
cmd="pydav-client -c $config"

$cmd -d 'documents/test.mp3'
$cmd --download Music/ ~/Downloads/music-vrac
```

### Moving resources

<p>
</p>

```bash
config="~/Downloads/pydav/configs/config-lan.ini"
cmd="pydav-client -c $config"

$cmd -i Music/music-vrac /vrac
$cmd --move /vrac Music/torem
```

### Erasing resources

<p>
</p>

```bash
config="~/Downloads/pydav/configs/config-lan.ini"
cmd="pydav-client -c $config"

$cmd -r Music/torem
$cmd --delete /photos
$cmd --delete scripts/class-example.py
$cmd --delete scripts
```

Python Use
----------

<p>
To start using it, first import it.
</p>

```python
  from PyDav import tools
```

### Instanciate

<p>
During the init, you will be required to specify a config.ini file.

If you do not give it, a default ini file will be generated at the same place where is executed your python script.
</p>

Here is an example of config file:

```bash
cat > "./config.ini" << EOF
[DEFAULT]
# Local filesystem path where download will be done.
localpath = /home/amaibach/pydav-datas

# Webdav global informations part
[webdav]
# Your webdav URI
rhost = http://127.0.0.1
# Webdav login
rlogin = johnDoe
# Webdav password
rpass = None
# Webdav root location (for nextcloud for example you will need to
# set it to /remote.php/webdav/
webdav_root = /
# Webdav target path where to put uploads
share = /synced

[logging]
# Define here your logging destination
# This can be to console, or to syslog into user facility or directly to a file
logdst = console
# If you specified file for logdst, this item will be requested
logfilepath = /var/log/
EOF
```

<p>
Now that you have set up your config file, you can call webdav tools.
</p>

```python
  webdavClient = tools.core("/path/to/your/config.ini")
```

<p>
All method calls will return a dict with 'code' and 'content':

  - Code can be **0** or **1** (for **success** of **fail**).
  - Content will give you error string in case of failure and result (*if there is something to return*) in case of success.
</p>

### Connect to your webdav

<p>
You are ready to connect to your Webdav, to do so, just invoke connect() method:
</p>

```python
  connected = webdavClient.connect()
  if connected['code'] != 0:
    del(webdavClient)
    exit(0)
```

<p>
As previously said, the *connect()* call has returned a dict which we have exploited in this
sample.
</p>

### Manipulate locations

<p>
PyDav' tools will use your configuration file to set local and remote locations
but if you need it, you can manipulate them like this:
</p>

```python
  print( webdavClient.localPath )
  # Set it to a new location
  webdavClient.localPath = "other/local/location"

  print( webdavClient.webdavShare )
  webdavClient.webdavShare = "other/remote/location"
```

<p>
Be aware that changing these variables means updating them for all next part of your code,
until you set it again or close the connection
</p>

### Closing

<p>
To cleanly close your webdav connection, just do this:
</p>

```python
  del(webdavClient)
  exit(0)
```

### List target path content

<p>
Use the **remote_list()** method and play with returned content
</p>

```python
  remotefiles = webdavClient.remote_list()
  if remotefiles['code'] != 0:
    del(webdavClient)
    exit(remotefiles['code'])
  else:
    remotefiles = remotefiles['content']
  print(remotefiles)
```

### Search for something

<aside class="warning">
:warning: 1. It can be very very slow on directories with many files.

:warning: 2. It is not really efficient but it can help sometimes .. maybe ...
</aside>

<p>
You can look for a **word** in your webdav and the **remote_search(matchword=str)** method will return
any files path matching found.
</p>

```python
import os
word = 'vrac'

woriginalpath = webdavClient.webdavShare
newloc = "/public/vrac"
wcurrpath = "{}/{}".format(webdavClient.webdavShare, newloc)
wcurrpath = os.path.normpath(wcurrpath)
webdavClient.webdavShare = wcurrpath

resfound = webdavClient.remote_search(word)
if resfound['code'] == 0 :
  for rfilename in resfound['content']:
    fileloc = "{0}/{1}".format(webdavClient.localPath, rfilename)
    print(fileloc)

webdavClient.webdavShare = woriginalpath
```

### Upload resources

<p>
Here how to use **upload(local=str)** method
</p>

```python
  # upload a local directory
  resource = '/path/to/local/dir'

  res = webdavClient.upload(resource)
  if res['code'] == 1:
    del(webdavClient)
    exit(1)

  # upload a local single file
  resource = '/path/to/local/file.txt'

  res = webdavClient.upload(resource)
  if res['code'] == 1:
    del(webdavClient)
    exit(1)
```

### Download resources

<p>
Here how to use **download(remote=str, local=str)** method
</p>

```python
  # remote resource (located on webdav) to retrieve
  file2dl = 'toto-2/zigzag/mp3'

  # Formatting local destination
  remoteres = "{}/{}".format(webdavClient.webdavShare, file2dl)
  localres = "{0}/{1}".format(webdavClient.localPath, remoteres)

  if webdavClient.download(remotefile, localres)['code'] == 1:
    del(webdavClient)
    exit(1)
```

### Copy resources

<p>
Here how to use **remote_duplicate(src=str, dst=str)** method
</p>

```python
  # remote resource (located on webdav) to duplicate
  file2cp = 'mp3'
  # remote resource (located on webdav) duplication destination
  dst = 'toto-1/zigzag/zizi/mp3'

  rescp = webdavClient.remote_duplicate(file2cp, dst)
  if rescp['code'] != 0:
    del(webdavClient)
    exit(1)
```

### Move resources

<p>
Here how to use **remote_move(src=str, dst=str)** method
</p>

```python
  # remote resource (located on webdav) to move
  file2mv = 'toto-1/zigzag/zizi/mp3'
  # remote resource (located on webdav) destination
  dst = 'toto-2/zigzag/mp3'

  resmv = webdavClient.remote_move(file2mv, dst)
  if resmv['code'] != 0:
    del(webdavClient)
    exit(1)
```

### Remove resources

<p>
Here how to use **remote_remove(resource=str)** method
</p>

```python
  err = False
  # list of resources to remove
  res2del = ['toto-1/', 'toto-2/', 'mp3','class-example.py']

  for r in res2del:
    resdel = webdavClient.remote_remove(r)
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
    print("WARN: Some errors occured during remove see logs for more informations.")
```
