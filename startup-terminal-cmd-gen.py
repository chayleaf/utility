#!/usr/bin/python3
import sys, shlex

#gnome-terminal -- bash -c "gnome-terminal --tab -- bash -c \"cd ~/code/py/old/pythonn && echo theproject.py ^Ctheproject.py\" && cd ~/code/py/old/pythonn && ./instaFox.py"

cmdList = []
cmd = None

while cmd != '':
    if cmd is not None:
        cmdList.append(cmd)
    cmd = input('Enter new bash command (enter to end): ')

if len(cmdList) == 0:
    print('Empty command list, exiting...')

callCmdList = []
for cmd in cmdList[1:]:
    callCmdList.append(f'gnome-terminal --tab -- bash -c {shlex.quote(cmd)}')

callCmdList.append(f'bash -c {shlex.quote(cmdList[0])}')

outCmd = f'gnometerminal -- bash -c {shlex.quote(" && ".join(callCmdList))}'

print(outCmd)
