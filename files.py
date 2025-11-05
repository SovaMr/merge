from settings import original, dev1, dev2, output, app, recipe, dataflow


## === DO NOT CHANGE THESE VALUES === ###
name = output
waveName = output
app = app
recipe = recipe
dataflow = dataflow

original_xml = ".github/wave/"+original+".xmd-meta.xml"

xml1 = ".github/wave/"+dev1+".xmd-meta.xml"
xml2 = ".github/wave/"+dev2+".xmd-meta.xml" 

original_json = ".github/wave/"+original+".wdash"

json1 = ".github/wave/"+dev1+".wdash"
json2 = ".github/wave/"+dev2+".wdash"

output_xml = "force-app/main/default/wave/"+output+".xmd-meta.xml"
output_json = "force-app/main/default/wave/"+output+".wdash"

meta =  ".github/wave/"+original+".wdash-meta.xml" 
meta_new = "force-app/main/default/wave/"+output+".wdash-meta.xml" 


recipe1 = "./wave/"+output+".wdpr"
recipe2 = "./wave/"+output+".wdpr"

dataflow1 = "./wave/"+output+".wdf"
dataflow2 = "./wave/"+output+".wdf"