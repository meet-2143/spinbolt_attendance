import uuid


class DuplicateAttendanceError(Exception):
    def __init__(self, existing_id: uuid.UUID):
        self.existing_id = existing_id
        super().__init__(f"Duplicate attendance for existing record {existing_id}")


class BulkValidationError(Exception):
    def __init__(self, errors: list[dict]):
        self.errors = errors
        super().__init__("Bulk attendance validation failed")
