actual_al = None

def get_attribute_linker():
    global actual_al
    if actual_al:
        return actual_al
    else:
        actual_al = AttributeLinker()
        return actual_al
    
class AttributeLinker:
    def __init__(self):
        self.cls_to_attrs = dict()
        self.attrs_to_class = dict()
        self.registered_cls = set()

    def __call__(self, cls_name, attr_list):
        # update register of some class
        if cls_name in self.registered_cls:
            related_attrs = self.cls_to_attrs[cls_name]
            for attr_name in related_attrs:
                self.attrs_to_class[attr_name].pop(cls_name)

        # after we deleted old records
        self.cls_to_attrs[cls_name] = attr_list
        for attr_name in attr_list:
            if not attr_name in self.attrs_to_class.keys():
                self.attrs_to_class[attr_name] = []
            self.attrs_to_class[attr_name].append(cls_name)
            


    def get_classes_by_attrs(self, attr_list):
        assert all([attr_name in self.attrs_to_class.keys() for attr_name in attr_list]), "Attribute is not registered for any RepositoryProcessor"

        class_dict = dict()
        for attr_name in attr_list:
            class_dict[attr_name] = self.attrs_to_class[attr_name]
        return class_dict