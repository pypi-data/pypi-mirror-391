import sys
from pathlib import Path
import argparse
import yaml
import json

VERSION="v1.0.0"

def mainCLI():
    """
    Smry: CLIを処理する関数。

    Returns:
        Type: dict
        Smry: {directory名(str):[i(int):i番目の子directory名(str)]}という木構造。
    """
    parser=argparse.ArgumentParser(prog="PROG")
    parser.add_argument("dirName",type=str,default=None,help="put in directory name. Both absolute and relative is OK.")
    parser.add_argument("-v","--version",action="version",version=f"treejson {VERSION}")
    parser.add_argument("-y","--yaml",action="store_true",help="output as a YAML format.")
    parser.add_argument("-a","--all",action="store_true",help="visit hidden file.")
    parser.add_argument("-f","--file",type=str,help="output as a file.")
    parser.add_argument("-d","--depth",type=int,help="specify maximum depth.")
    args=parser.parse_args()
    dirname=Path(args.dirName)
    outDict=directoryBFS(dirname.resolve(),maxDepth=args.depth,isAll=args.all)
    if(args.yaml):
        if(args.file is None):
            yaml.safe_dump(outDict,sys.stdout)
        else:
            with open(args.file,mode="w",encoding="utf-8") as f:
                yaml.safe_dump(outDict,f)
    else:
        if(args.file is None):
            print(outDict)
        else:
            with open(args.file,mode="w",encoding="utf-8") as f:
                json.dump(outDict,f)

def directoryBFS(startDir:Path,maxDepth:int=None,isAll:bool=None):
    """
    Smry: directory構造を幅優先探索する関数。

    Args:
      startDir:
        Type: Path.
        Smry: 探索を開始するdirectory名。
      maxDepth:
        Type: Int.
        Smry: 探索の最大の深さ。
        Expl:
        - current directoryは深さ0。
        - 「maxDepth<現在の深さ」の時に探索打ち切り。
        Default: 255.
      isAll:
        Type: Bool.
        Smry: {True⇒隠しfileも探索, False⇒隠しfileを通過。}
        Default: false.
    Returns:
      Type: dict
      Smry: {directory名(str):[i(int):i番目の子directory名(str)]}という木構造。
      Expl:
      - {directory名(str):[i(int):i番目の子directory名|file名(str)]}。
      - file名の時は、終端nodeになる。
    """
    if(maxDepth is None):
        maxDepth=255
    if(isAll is None):
        isAll=False
    outDict={startDir.name:[]}
    visitQueue=[startDir]  #訪れるdirectory(Path型)を格納する。
    listQueue=[outDict[startDir.name]]  #訪れるdirectoryの子要素のlist型を格納する。
    depthQueue=[0]  #訪れるdiectoryの深さ(int型)を格納する。
    while(True):
        if(visitQueue==[]):
            break
        curDir=visitQueue.pop(0)
        curList=listQueue.pop(0)
        curDepth=depthQueue.pop(0)
        nextDepth=curDepth+1
        if(maxDepth<nextDepth):
            continue
        for childPath in curDir.iterdir():
            childName=childPath.name
            firstChr=childName[0]
            if((not isAll) and firstChr=='.'):
                continue
            if(childPath.is_file()):
                curList.append(childName)
            else:
                childDict={childName:[]}
                curList.append(childDict)
                visitQueue.append(childPath)
                listQueue.append(childDict[childName])
                depthQueue.append(nextDepth)
    return outDict


if(__name__=="__main__"):
    mainCLI()
