class ReContainer:

    def __init__(self) -> None:
        pass

    def __eq__(self, other) -> bool:
        if isinstance(other, ReContainer):
            self_attrs = vars(self)
            other_attrs = vars(other)

            if self_attrs.keys() != other_attrs.keys():
                return False

            for key in self_attrs.keys():
                if key not in other_attrs or self_attrs[key] != other_attrs[
                        key]:
                    return False
            return True
        else:
            return False