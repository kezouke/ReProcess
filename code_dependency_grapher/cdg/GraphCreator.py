from code_dependency_grapher.cdg.CodeComponent import CodeComponent
from code_dependency_grapher.utils.mappers.FilePathAstMapper import FilePathAstMapper
from code_dependency_grapher.utils.mappers.FilePathAstMapper import FilePathAstMapper
from code_dependency_grapher.utils.mappers.IdComponentMapper import IdComponentMapper
from code_dependency_grapher.utils.mappers.IdFileAnalyzerMapper import IdFileAnalyzerMapper
from code_dependency_grapher.utils.find_components import extract_components_from_files

class GraphCreator:
    def __init__(self,
                 python_files,
                 ) -> None:
        self.python_files = python_files
    
    def create_from_scratch(self):
        ast_manager = FilePathAstMapper(self.python_files)
        file_components_map, _, package_components_names = \
            extract_components_from_files(self.python_files, 
                                          ast_manager.file_path_ast_map)
        id_component_manager = IdComponentMapper(file_components_map)
        id_files_manager = IdFileAnalyzerMapper(self.python_files,
                                                ast_manager)


        code_components = []
        for id in id_component_manager.id_component_map:
            code_components.append(CodeComponent(id,
                                                 id_files_manager,
                                                 ast_manager.file_path_ast_map, 
                                                 id_component_manager.id_component_map,
                                                ))
            
        for cmp in code_components:
            
            all_components = set(package_components_names)
            cmp_imports = set(cmp.extract_imports())
            linked_components = all_components.intersection(cmp_imports)

            for l_cmp in linked_components:
                l_cmp_id = id_component_manager.component_id_map[l_cmp]
                cmp.linked_component_ids.append(l_cmp_id)
        
        return code_components, id_files_manager.id_file_map