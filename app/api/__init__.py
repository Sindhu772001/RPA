from RPA.Browser.Selenium import Selenium 
from tracking_scripts.ocean.base import ContainerFactory
from tracking_scripts.ocean.cmdu import CMDUContainerBuilder
from tracking_scripts.ocean.cosu import COSUContainerBuilder
from tracking_scripts.ocean.hlcu import HLCUContainerBuilder
from tracking_scripts.ocean.maeu import MAEUContainerBuilder
from tracking_scripts.ocean.mscu import MSCUContainerBuilder


container = ContainerFactory()
browser = Selenium()
download_folder = "/home/Sindhuja.Periyasamy/Downloads"
container.register_builder("CMDU", CMDUContainerBuilder(browser, download_folder))
container.register_builder("COSU", COSUContainerBuilder())
container.register_builder("HLCU", HLCUContainerBuilder())
container.register_builder("MAEU", MAEUContainerBuilder(browser))
container.register_builder("MSCU", MSCUContainerBuilder(browser))