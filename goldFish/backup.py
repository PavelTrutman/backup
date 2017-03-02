#!/usr/bin/python3

import os
import shutil
import time
import math
import sys
import re
import argparse
from .io import *
from .config import Config


def main():

  # command line arguments parser
  parser = argparse.ArgumentParser(add_help=False)
  parser.prog = 'goldFish';
  
  parser.add_argument('--help', '-h', action='help', help='show this help message and exit')
  parser.add_argument('configFile', type=str, help='path to the config file')
  args = parser.parse_args()


  config = Config(args.configFile)

  prevBackups = os.listdir(config.backupDirTo)
  prevBackups.sort(reverse=True)
  
  today = time.strftime('%Y%m%d_%H%M')
  dirToday = os.path.join(config.backupDirTo, today)
  os.mkdir(dirToday)
  
  printHeadline()
  
  print('Creating new backup: ' + today)
  
  for dirFrom in config.backupDirFrom:
    backupDir = os.path.basename(dirFrom)
    dirTo = os.path.join(dirToday, backupDir)
    os.mkdir(dirTo)
  
    #find prev backup
    dirPrev = None
    datePrev = None
    for prev in prevBackups:
      dirPrevTmp = os.path.join(config.backupDirTo, prev, backupDir)
      if os.path.isdir(dirPrevTmp):
        dirPrev = dirPrevTmp
        datePrev = prev
        break
    
    print()
    print(backupDir)
    print('  From: ' + dirFrom)
    print('  To:   ' + dirTo)
    if datePrev is None:
      print('  No previous backup found.')
    else:
      print('  Previous backup found from: ' + datePrev)
    
    sizeCopied = 0
    sizeLinked = 0
   
    for root, dirs, files in os.walk(dirFrom):
      relPath = os.path.relpath(root, dirFrom)
      curDirTo = os.path.join(dirTo, relPath)
      for dir in dirs:
        os.mkdir(os.path.join(curDirTo, dir))
      for file in files:
        fileFrom = os.path.join(root, file)
        fileTo = os.path.join(curDirTo, file)
        printToTerminalSize(os.path.join(relPath, file))
        sys.stdout.flush()
        copied = False
        if not (dirPrev is None):
          filePrev = os.path.join(dirPrev, relPath, file)
          if os.path.isfile(filePrev):
            statFrom = os.stat(fileFrom)
            statPrev = os.stat(filePrev)
            if (statFrom.st_size == statPrev.st_size) and (round(statFrom.st_mtime) == round(statPrev.st_mtime)):
              os.link(filePrev, fileTo)
              copied = True
              sizeLinked += statFrom.st_size
        if not copied:
          sys.stdout.write('\r')
          sys.stdout.flush()
          printToTerminalSize(' ')
          sys.stdout.write('\r')
          sys.stdout.flush()
          print('    ' + os.path.join(relPath, file))
          shutil.copy2(fileFrom, fileTo)
          sizeCopied += os.stat(fileFrom).st_size
        else:
          sys.stdout.write('\r')
          sys.stdout.flush()
          printToTerminalSize(' ')
          sys.stdout.write('\r')
          sys.stdout.flush()
  
    print('  Copied: ' + readableSize(sizeCopied))
    print('  Linked: ' + readableSize(sizeLinked))

if __name__ == "__main__":
  main()
