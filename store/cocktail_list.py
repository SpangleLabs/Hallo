import pickle
from xml.dom import minidom

cocktailList = pickle.load(open("cocktails.p","rb"))

#Create document, with DTD
docimp = minidom.DOMImplementation()
doctype = docimp.createDocumentType(
    qualifiedName='cocktail_list',
    publicId='', 
    systemId='cocktail_list.dtd',
)
doc = docimp.createDocument(None, 'cocktail_list', doctype)
#get root element
root = doc.getElementsByTagName("cocktail_list")[0]

for cocktail in cocktailList:
    cocktailElement = doc.createElement("cocktail")
    nameElement = doc.createElement("name")
    nameElement.appendChild(doc.createTextNode(cocktail['name']))
    cocktailElement.appendChild(nameElement)
    instructionsElement = doc.createElement("instructions")
    instructionsElement.appendChild(doc.createTextNode(cocktail['instructions']))
    cocktailElement.appendChild(instructionsElement)
    for ingredient in cocktail['ingredients']:
        ingredientElement = doc.createElement("ingredient")
        amountElement = doc.createElement("amount")
        amountElement.appendChild(doc.createTextNode(ingredient[0]))
        ingredientElement.appendChild(amountElement)
        nameElement = doc.createElement("name")
        nameElement.appendChild(doc.createTextNode(ingredient[1]))
        ingredientElement.appendChild(nameElement)
        cocktailElement.appendChild(ingredientElement)
    root.appendChild(cocktailElement)


#save XML
doc.writexml(open("cocktail_list.xml","w"),addindent="\t",newl="\r\n")
