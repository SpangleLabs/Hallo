import pickle
from xml.dom import minidom

c = pickle.load(open("convert.p","rb"))


def addUnit(unitName,c,doc,parentElement):
    #Create unit element
    unitElement = doc.createElement("unit")
    #Add first name
    nameElement = doc.createElement("name")
    nameElement.appendChild(doc.createTextNode(unitName))
    unitElement.appendChild(nameElement)
    #Add other names
    for alias in c['alias']:
        if(c['alias'][alias]==unitName):
            nameElement = doc.createElement("name")
            nameElement.appendChild(doc.createTextNode(alias))
            unitElement.appendChild(nameElement)
    #Add value
    valueElement = doc.createElement("value")
    valueElement.appendChild(doc.createTextNode(c['units'][unitName]['value']))
    unitElement.appendChild(valueElement)
    #Add offset
    if('offset' in c['units'][unitName]):
        offsetElement = doc.createElement("offset")
        offsetElement.appendChild(doc.createTextNode(c['units'][unitName]['offset']))
        unitElement.appendChild(offsetElement)
    #Add last update
    if('last_update' in c['units'][unitName]):
        lastUpdateElement = doc.createElement("last_update")
        lastUpdateElement.appendChild(doc.createTextNode(c['units'][unitName]['last_update']))
        unitElement.appendChild(lastUpdateElement)
    #Add to parent element
    parentElement.appendChild(unitElement)
            

#Create document, with DTD
docImp = minidom.DOMImplementation()
docType = docImp.createDocumentType(
    qualifiedName='convert',
    publicId='', 
    systemId='convert.dtd',
)
doc = docImp.createDocument(None, 'convert', docType)
#get root element
root = doc.getElementsByTagName("convert")[0]

for typeName in c['types']:
    #Start type element
    typeElement = doc.createElement("type")
    #Add name element to type element
    nameElement = doc.createElement("name")
    nameElement.appendChild(doc.createTextNode(typeName))
    typeElement.appendChild(nameElement)
    #Add decimals, if exists
    if('decimals' in c['types'][typeName]):
        decimalsElement = doc.createElement("decimals")
        decimalsElement.appendChild(doc.createTextNode(c['types'][typeName]['decimals']))
        typeElement.appendChild(decimalsElement)
    #Add base unit
    baseUnitName = c['types'][typeName]['base_unit']
    baseUnitElement = doc.createElement("base_unit")
    addUnit(baseUnitName,c,doc,baseUnitElement)
    typeElement.appendChild(baseUnitElement)
    #Add other units
    for unitName in c['units']:
        if(c['units'][unitName]['type'] == typeName):
            addUnit(unitName,c,doc,typeElement)
    #Add type to convert
    root.appendChild(typeElement)
    

print("now add <prefix_group> elements manually to <convert>")
print("then add <valid_prefix_group> elements manually to any and all <unit> elements")
