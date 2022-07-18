
'''
Made by Arthur Cury Meirelles
The goal was to make a script that save poses for animation or when you are painting weights.
Contact:
    arthurcurymeirelles@hotmail.com
    https://www.linkedin.com/in/arthurm3d
'''

import maya.cmds as cmds
import os
from functools import partial

#path where the file will be save on the system
def pathposes(*args):
    global exportPath, path
    exportPath = cmds.fileDialog2(fm=3, okc='SelectFolder', cap='Select Export Folder')[0]
    print (exportPath)
    path = exportPath    

class obj(object):
    def __init__(self, name):
        self.name = name
        self.attr = {}#dictionary of keyable attributes
        
    def GetName(self):
        return self.name
        
    def AddAttr(self, attr, value):
        self.attr[attr] = value
    
    def SetAttr(self):
        for attr, value in self.attr.items():#loop over dictionary and save values
            fullAttr = self.name + '.' + attr
            cmds.setAttr(fullAttr, value)
            
    def GetAttrs(self):
        return self.attr

class keyGroup(object):
    def __init__(self, name):
        self.name = name
        self.keys = []
        
    def GetName(self):
        return self.name
        
    def AddKey(self, key):
        self.keys.append(key)
        
    def SetKeys(self):
        for key in self.keys:
            key.SetAttr()
            
    def GetKeys(self):
        return self.keys

keyGroups = []

def ShowGroup(g):
    def set(g, *args):
        g.SetKeys()
    def remove(g, *args):
        for k in g.GetKeys():
            k.GetAttrs().clear()
        g.GetKeys()[:]=[]
        keyGroups.remove(g)
        cmds.deleteUI(setpose)
        cmds.deleteUI(remove)
        cmds.deleteUI(title)

    name = g.GetName()
    title = cmds.frameLayout ( label=name, collapsable = True, parent = "columnLayout01")
    fullPath = path + '/' + name + ".png"
    setpose = cmds.iconTextButton( style='iconOnly', image1=fullPath, label='set pose', command=partial(set,g) )
    remove = cmds.button( label='delete', command=partial(remove,g))
    
def ShowGroups():
    for g in keyGroups:
        ShowGroup(g)

def Keyposes():
    if cmds.window('windowR', exists=True):
        cmds.deleteUI('windowR')
        
    windowR = cmds.window('windowR', title="Key Poses",s=False, widthHeight=(300, 400))
    cmds.scrollLayout( )
    cmds.columnLayout("columnLayout01", adjustableColumn=True, columnAttach=("both", 5), rowSpacing=5, columnAlign="left")
    
    def AddKeyGroup(value1):
        #this will save the transforms of each control selected
        keyList = []
        keys = cmds.ls(sl=True, type='transform')
        print (keys)
        for k in keys:
            o = obj(k)
            attributes = cmds.listAttr(k, k=True)
            for a in attributes:
                attr = k + '.' + a
                value = cmds.getAttr(attr)
                if type(value) is float:
                    o.AddAttr(a, cmds.getAttr(attr))
            keyList.append(o)
        
        #name group
        if cmds.window('winName', exists=True):
            cmds.deleteUI('winName')
        winName = cmds.window('winName', title="name group", widthHeight=(400, 20))
        cmds.columnLayout("columnLayout02", adjustableColumn=True, columnAttach=("both", 5), rowSpacing=5, columnAlign="left")
        
        def closeWindow(value1):
            name = cmds.textFieldGrp( nameVal, query=True, text=True)
            gr = keyGroup(name)
            for k in keyList:
                gr.AddKey(k)
            keyGroups.append(gr)
            cmds.deleteUI('winName')
            
            #screenshot from viewport
            oldFormat = cmds.getAttr("defaultRenderGlobals.imageFormat")
            cmds.setAttr("defaultRenderGlobals.imageFormat", 32)
            fullPath = path+ '/' + name + ".png"
            cmds.playblast(completeFilename=fullPath,frame=cmds.currentTime(query=True),format="image", widthHeight = (512,256), quality=100, showOrnaments=False)
            cmds.setAttr("defaultRenderGlobals.imageFormat", oldFormat)
            
            ShowGroup(gr)
        
        nameVal = cmds.textFieldGrp(adjustableColumn=True, changeCommand=closeWindow, label='name')
        
        cmds.showWindow( winName )
    
    
    def LoadSetup(filename):
        #load previous saved setup from file   
        counter = 0
        SampleDataFile=cmds.fileDialog2(cap="Importing Sound Data File:", ff="*.txt",fm=1)
        print (SampleDataFile[0])        
        readFile = open(SampleDataFile[0],"r")
        if readFile.readline() != "KEYPOSES\n":
            print ("error expected KEYPOSES")
            return
        nrOfGroups = int(float(readFile.readline()))
        print (nrOfGroups)
        groupCounter = 0
        while groupCounter < nrOfGroups:
            groupname = readFile.readline().strip('\n')
            nrOfKeys = int(float(readFile.readline()))
            keyList = []
            
            keyCounter = 0
            while keyCounter < nrOfKeys:
                keyname = readFile.readline().strip('\n')
                print (keyname)
                nrOfAttrs = int(float(readFile.readline()))
                o = obj(keyname)
                
                attrCounter = 0
                while attrCounter < nrOfAttrs:
                    attrString = readFile.readline()
                    attrList = attrString.split(' ', 1 )
                    o.AddAttr(attrList[0], float(attrList[1]))
                    attrCounter += 1
                    
                keyList.append(o)
                keyCounter +=1
                
            gr = keyGroup(groupname)
            for k in keyList:
                gr.AddKey(k)
            keyGroups.append(gr)
            groupCounter += 1
        ShowGroups()

    
#here we save the name of controls, attributes saved and there lenth    
    def SaveSetup(filename):
        #write current setup to file
        savefile = open(path + '/' + filename + '.txt', 'w')
        savefile.write('KEYPOSES\n')
        savefile.write(str(len(keyGroups)) + '\n')#nrofgroups
        for kGroup in keyGroups:
            savefile.write(kGroup.GetName() + '\n')#groupname
            keys = kGroup.GetKeys()
            savefile.write(str(len(keys)) + '\n')#nrofkeys
            for k in keys:
                savefile.write(k.GetName() + '\n')#keyname
                attrs = k.GetAttrs()
                savefile.write(str(len(attrs)) + '\n')#nrofattrs
                for attr, value in attrs.items():
                    savefile.write(attr + ' ' + str(value) + '\n')#attr value
                
        savefile.close()
        
    def CreateSetupPrompt(value1):
        if cmds.window('winName', exists=True):
            cmds.deleteUI('winName')
        winName = cmds.window('winName', title="name group", widthHeight=(400, 50))
        cmds.columnLayout("columnLayout02", adjustableColumn=True, columnAttach=("both", 5), rowSpacing=5, columnAlign="left")
        
        def closeWindow(value1):
            filename = cmds.textFieldGrp( nameVal, query=True, text=True)
            cmds.deleteUI('winName')
            SaveSetup(filename)
        expl = cmds.text(label="enter the filename to save the setup to eg: handposes")
        nameVal = cmds.textFieldGrp(adjustableColumn=True, changeCommand=closeWindow, label='name')
        cmds.showWindow( winName )
    cmds.rowLayout (cw3 = (50, 280, 40), nc = 4)
    cmds.button( label='file path', command=pathposes)
    cmds.button( label='add pose', command=AddKeyGroup)
    cmds.button( label='save setup', command=CreateSetupPrompt)
    cmds.button( label='load setup', command=LoadSetup)
    cmds.setParent( '..' )
    
    ShowGroups()
    
    cmds.showWindow( windowR )
    
    
    
Keyposes()
