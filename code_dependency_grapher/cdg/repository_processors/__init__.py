from .repository_container import RepositoryContainer
from .graph_builder import GraphBuilder
from .graph_updater import GraphUpdater
from .json_converter import JsonConverter
from .json_deconverter import JsonDeconverter
from .compose import Compose
from .regExp_finder import RegExpFinder
from .clone_repository import CloneRepository

if __file__ == "__main__":
    r_c = RepositoryContainer("", "", "")
    GraphBuilder()
    GraphUpdater()
    JsonConverter()
    JsonDeconverter
    Compose(r_c, [])
    CloneRepository("")
    RegExpFinder(".a")