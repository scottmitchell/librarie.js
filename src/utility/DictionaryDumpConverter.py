import json
import xml.etree.cElementTree as ET

def dive(element, xmlPath, xmlBranch):
    newPath = list(xmlPath)
    newPath.append(element['text'])

    print(str(".".join(newPath)))
    newBranch = ET.SubElement(xmlBranch, "Category", Name=element['text'])
    if (len(element['childElements']) == 0):
        for e in element['include']:
            newerPath = list(newPath)
            newerPath.append(e['path'].split(".")[-1])
            print ("    " + ".".join(newerPath))

            newerBranch = ET.SubElement(newBranch, "Category", Name=e['path'].split(".")[-1])
            getEntries(e['path'], newerBranch, newerPath[-1])
    else:
        for c in element['childElements']:
            dive(c, newPath, newBranch)


def getEntries(nodeName, branch, path):
    with open('librarieDump.json') as f:
        data = json.load(f)

        for node in data:
            if (node["fullCategoryName"].startswith(nodeName)):
                addEntry(node, branch, path)



def addEntry(node, branch, path):
    entry = ET.SubElement(branch, "Dynamo.Search.SearchElements.ZeroTouchSearchElement")
    address = '.'.join(node['folderPath'].split('/')[0:-1])
    #address += "."
    #address += node['Name']
    ET.SubElement(entry, "FullCategoryName").text = address
    ET.SubElement(entry, "Name").text = node['Name']
    ET.SubElement(entry, "Group").text = node['folderPath'].split('/')[-1]
    ET.SubElement(entry, "Description").text = node['description']
    ET.SubElement(entry, "SearchTags").text = ",".join(node['keywords'])

    inputs = ET.SubElement(entry, "Inputs")
    for inputName, inputType in zip(node['inputs'], node['inputTypes']):
        ET.SubElement(inputs, "InputParameter", Name=inputName, Type=inputType)
    
    outputs = ET.SubElement(entry, "Outputs")
    for output in node['outputs']:
        ET.SubElement(outputs, "OutputParameter", Name=output)
    
    ET.SubElement(entry, "SmallIcon").text = node['smallIcon']
    ET.SubElement(entry, "LargeIcon").text = node['largeIcon']




def addToTree(node, currentBranch, depth):
    if (depth >= len(node['folderPath'].split('/'))-1):
        addEntry(node, currentBranch, node['folderPath'])
        return

    childNames = [str(child.attrib['Name']) for child in currentBranch]
    newBranchName = node['folderPath'].split('/')[depth]
    nextBranchIndex = -1

    for i in range(len(childNames)):
        if (childNames[i] == newBranchName):
            addToTree(node, currentBranch[i], depth + 1)
            return

    if (nextBranchIndex == -1):
        newBranch = ET.SubElement(currentBranch, "Category", Name=newBranchName)
        addToTree(node, newBranch, depth+1)

        
        

documentation = []

with open('librarieDump.json') as f:
    data = json.load(f)
    for node in data:
        documentation.append({
            'name': node['Name'],
            'imageFile': node['imageFile'],
            'dynFile': node['dynFile'],
            'folderPath': node['folderPath'],
            'inDepth': node['inDepth'],
        })

with open('Dynamo_Nodes_Documentation.json', 'w') as outfile:  
    json.dump(documentation, outfile)



library2 = ET.Element("LibraryTree")

with open('layoutSpecs.json') as f:
    sections = json.load(f)['sections'][0]
    for s in sections['childElements']:
        dive(s, [], library2)


with open('librarieDump.json') as f:
    data = json.load(f)
    for node in data:
        if (node['folderPath'].split("/")[0] == "Revit"):
            #print (node['folderPath'])
            addToTree(node, library2, 0)
            #print ([child.attrib['Name'] for child in library2])



tree2 = ET.ElementTree(library2)
tree2.write("Revit_Library.xml")