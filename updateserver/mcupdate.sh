#!/bin/bash

cd /opt/minecraft/1.18server/
python3 updater.py
cd /opt/minecraft/1.18server/plugins/
rm Dynmap-3.*
wget https://dynmap.us/builds/dynmap/Dynmap-3.4-SNAPSHOT-spigot.jar
cd /opt/minecraft/1.18server/
python3 copyworlds.py
