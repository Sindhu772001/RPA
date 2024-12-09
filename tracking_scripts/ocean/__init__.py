from .base import ContainerFactory
from RPA.Browser.Selenium import Selenium 

# from .anrm import ANRMContainerBuilder
# from .aplu import APLUContainerBuilder
from .cmdu import CMDUContainerBuilder
from .cosu import COSUContainerBuilder
from .hlcu import HLCUContainerBuilder
from .maeu import MAEUContainerBuilder
from .mscu import MSCUContainerBuilder
# from .oney import ONEYContainerBuilder
# from .sudu import SUDUContainerBuilder

container = ContainerFactory()
browser = Selenium()
download_folder = "/home/Sindhuja.Periyasamy/Downloads"
# container.register_builder("ANRM", ANRMContainerBuilder())
# container.register_builder("APLU", APLUContainerBuilder())
container.register_builder("CMDU", CMDUContainerBuilder(browser, download_folder))
container.register_builder("COSU", COSUContainerBuilder())
container.register_builder("HLCU", HLCUContainerBuilder())
container.register_builder("MAEU", MAEUContainerBuilder(browser))
container.register_builder("MSCU", MSCUContainerBuilder(browser))
# container.register_builder("ONEY", ONEYContainerBuilder())
# container.register_builder("SUDU", SUDUContainerBuilder())


# to use:
# ocean.container.create(<key>, <container_number>)
# e.g. ocean.container.create("MSCU", "MSCU3270270")
