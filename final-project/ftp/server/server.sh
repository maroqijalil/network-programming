#!/usr/bin/expect

eval spawn su - netpro
set prompt "Password:"
interact -o -nobuffer -re $prompt return
send "123\r"
set prompt "netpro"
interact -o -nobuffer -re $prompt return
send "cd ./server && python3 main.py\r"
interact
