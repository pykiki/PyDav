#!/usr/bin/env bash
# Copyright (c) 2017 by Alain Maibach
# Licensed under the terms of the GPL v3

set -eu -o pipefail

config=" ~/Downloads/pydav/configs/config-lan.ini"

cmd="pydav-client -c $config"

set -x
$cmd -h
$cmd -l
$cmd --list torrents
$cmd -s Queens Music/Vrac
$cmd --upload ~/Downloads/photos/
$cmd -u ~/Downloads/class-example.py scripts/
$cmd -d 'torrents/[ Torrent9.ws ] soprano-Everest-2016.mp3'
$cmd --download Music/poussin ~/Downloads/music-vrac
$cmd -i Music/Vrac /vrac
$cmd --move /vrac Music/torem
$cmd -r Music/torem
$cmd --delete /photos
$cmd --delete scripts/class-example.py
$cmd --delete scripts
rm -r ~/Downloads/pydav/data/videos/ ~/Downloads/music-vrac
