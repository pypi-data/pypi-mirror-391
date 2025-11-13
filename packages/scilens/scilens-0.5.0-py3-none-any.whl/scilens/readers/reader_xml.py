import logging
from scilens.readers.reader_interface import ReaderInterface
from scilens.config.models import ReaderXmlConfig
from scilens.components.compare_floats import CompareFloats
from.tree import Tree
from scilens.utils.xml import etree_to_dict
import xml.etree.ElementTree as ET
class ReaderXml(ReaderInterface):
	configuration_type_code='xml';category='datalines';extensions=['XML']
	def read(A,config):C=None;B=config;A.reader_options=B;D=open(A.origin.path,'r',encoding=A.encoding);E=ET.parse(D);F=E.getroot();G=etree_to_dict(F);D.close();A.floats_data=Tree.data_to_numeric_values(G,include_patterns=B.path_include_patterns if B else C,exclude_patterns=B.path_exclude_patterns if B else C);A.metrics=C
	def compare(A,compare_floats,param_reader,param_is_ref=True):C=param_is_ref;B=param_reader;D=A if C else B;E=A if not C else B;Tree.compare(compare_floats,test_floats_data=D.floats_data,ref_floats_data=E.floats_data)
	def class_info(A):return{'metrics':A.metrics}