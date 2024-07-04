from .repository_container import ReContainer
from .graph_builder import GraphBuilder
from .graph_updater import GraphUpdater
from .json_converter import JsonConverter
from .json_deconverter import JsonDeconverter
from .compose import Compose
from .regexp_finder import RegExpFinder
from .clone_repository import CloneRepository

if __file__ == "__main__":
    r_c = ReContainer("", "", "")
    GraphBuilder()
    GraphUpdater()
    JsonConverter()
    JsonDeconverter
    Compose(r_c, [])
    CloneRepository("")
    RegExpFinder(".a")