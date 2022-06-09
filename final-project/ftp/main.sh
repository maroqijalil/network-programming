#!/bin/bash

sudo apt install expect -y

sudo rm -rf /home/netpro/server

sudo cp -r ./server /home/netpro
sudo chown -R netpro:netpro /home/netpro/server

sudo chown $USER:$USER /home/netpro/server/server.sh
sudo chmod 777 /home/netpro/server/server.sh

cd /home/netpro/server

./server.sh
