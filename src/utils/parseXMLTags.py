import xml.etree.ElementTree as ET
from loguru import logger

####
# XML Tags:
#     <prompt_id> 
#     <sample_dataframe_init_code>
#     <list_merged_dataframes>
#     <dataframe_relationship_code>
#     <matplotlib_code>
####

class ParseXMLTags:
    def __init__(self, _xml_tags):
        self.xml_tags = _xml_tags
    ###
    # Parse simple XML tags as keys, and values.
    # Return Dictionary of Tags as Keys, and Code as Values
    ###
    def parse_xmltree(self, root):
        kv = {}
        # Loop through each child (item) of the root
        for child in root:
            tag = child.tag
            value = child.text
            #logger.info("child element:", tag, "Value:", value)
            if(tag in self.xml_tags):
                kv[tag] = value
        return kv

    ###
    # Parse simple XML tags contained in a file
    ###
    def parse_xml_file(self, xmlfile):
        # Parse the XML file
        tree = ET.parse(xmlfile)
        return self.parse_xmltree(tree.getroot())

    ###
    # Parse simple XML tags embedded in a string
    ###
    @logger.catch
    def parse_xml_response(self, xmlstring):
        logger.debug(xmlstring)
        root = ET.fromstring(xmlstring)
        return self.parse_xmltree(root)
