class JamError(Exception):
    pass


class ReferenceNotExistError(JamError):
    def __init__(self, ref_path, parent_path, resolved_to=None):
        super().__init__(f"Referenced path does not exist {ref_path}")
        self.ref_path = ref_path
        self.parent_path = parent_path
        self.resolved_to = resolved_to


class ReferenceResolutionError(JamError):
    def __init__(self, ref_path, parent_path):
        super().__init__(f"Referenced path  can not be resolved {ref_path}")
        self.ref_path = ref_path
        self.parent_path = parent_path


class ReferenceTypeMismatch(JamError):
    def __init__(self, ref_path, parent_path, expected, got):
        super().__init__(f"Reference resolved to {got}, expected {expected}")
        self.ref_path = ref_path
        self.parent_path = parent_path
        self.expected_type = expected
        self.got_type = got
