from pathlib import Path
import json

if(__name__=="__main__"):
    parentDirectory=Path(__file__).parent
    outputFile=parentDirectory/"output.json"
    expectedFile=parentDirectory/"expected.json"
    with open(outputFile,mode="r",encoding="utf-8") as f:
        outDict=json.load(f)
    with open(expectedFile,mode="r",encoding="utf-8") as f:
        expDict=json.load(f)
    if(outDict==expDict):
        assert True
    else:
        assert False
