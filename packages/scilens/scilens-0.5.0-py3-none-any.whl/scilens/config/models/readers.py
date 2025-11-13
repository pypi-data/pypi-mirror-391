_B=None
_A='forbid'
from typing import Literal,Optional
from pydantic import BaseModel,Field
from scilens.config.models.reader_format_txt import ReaderTxtConfig
from scilens.config.models.reader_format_csv import ReaderCsvConfig
from scilens.config.models.reader_format_txt_fixed_cols import ReaderTxtFixedColsConfig
from scilens.config.models.reader_format_trees import ReaderJsonConfig,ReaderXmlConfig,ReaderYamlConfig
from scilens.config.models.reader_format_netcdf import ReaderNetcdfConfig
class BaseCatalogItem(BaseModel,extra=_A):type:str
class ReaderTxtConfigItem(BaseCatalogItem,extra=_A):type:Literal['txt'];parameters:ReaderTxtConfig
class ReaderCsvConfigItem(BaseCatalogItem,extra=_A):type:Literal['csv'];parameters:ReaderCsvConfig
class ReaderTxtFixedColsConfigItem(BaseCatalogItem,extra=_A):type:Literal['txt_fixed_cols'];parameters:ReaderTxtFixedColsConfig
class ReaderJsonFixedColsConfigItem(BaseCatalogItem,extra=_A):type:Literal['json_fixed_cols'];parameters:ReaderTxtFixedColsConfig
class ReaderXmlFixedColsConfigItem(BaseCatalogItem,extra=_A):type:Literal['xml_fixed_cols'];parameters:ReaderTxtFixedColsConfig
class ReaderYamlFixedColsConfigItem(BaseCatalogItem,extra=_A):type:Literal['yaml_fixed_cols'];parameters:ReaderTxtFixedColsConfig
class ReaderNetcdfConfigItem(BaseCatalogItem,extra=_A):type:Literal['netcdf'];parameters:ReaderNetcdfConfig
CATALOG_ITEM_TYPE=ReaderTxtConfigItem|ReaderCsvConfigItem|ReaderTxtFixedColsConfigItem|ReaderJsonFixedColsConfigItem|ReaderXmlFixedColsConfigItem|ReaderYamlFixedColsConfigItem|ReaderNetcdfConfigItem
class ReadersConfig(BaseModel,extra=_A):txt:ReaderTxtConfig=Field(default=ReaderTxtConfig(),description='Configuration des readers txt.');csv:ReaderCsvConfig=Field(default=ReaderCsvConfig(),description='Configuration des readers csv.');txt_fixed_cols:ReaderTxtFixedColsConfig=Field(default=ReaderTxtFixedColsConfig(),description='Configuration des readers txt avec colonnes fixes.');json:ReaderJsonConfig|_B=Field(default=_B,description='Configuration des readers json.');xml:ReaderXmlConfig|_B=Field(default=_B,description='Configuration des readers xml.');yaml:ReaderYamlConfig|_B=Field(default=_B,description='Configuration des readers yaml.');netcdf:ReaderNetcdfConfig=Field(default=ReaderNetcdfConfig(),description='Configuration des readers netcdf.');catalog:dict[str,CATALOG_ITEM_TYPE]|_B=Field(default=_B,description="Catalogue de configuration de readers par clé. Ex: `{'csv_comma': {'type': 'csv', 'parameters': {'delimiter': ','}}, 'csv_semicolon': {'type': 'csv', 'parameters': {'delimiter': ';'}}}`")