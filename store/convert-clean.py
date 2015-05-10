import re
from xml.dom import minidom

r = re.compile(">[\t\r\n]*<")

f = open("convert.xml","r").read()
f = r.sub("><",f)
open("convert.xml","w").write(f)

doc = minidom.parse("convert.xml")
doc.writexml(open("convert.xml","w"),addindent="\t",newl="\r\n")
