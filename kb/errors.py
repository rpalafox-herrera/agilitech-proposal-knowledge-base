class KBError(ValueError):
    """A problem safe to explain to the user."""


class DuplicateDocument(KBError):
    def __init__(self, document_id):
        self.document_id = document_id
        super().__init__(f"This exact file is already stored as document #{document_id}.")
