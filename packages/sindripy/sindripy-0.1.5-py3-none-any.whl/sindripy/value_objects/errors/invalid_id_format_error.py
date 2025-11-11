from sindripy.value_objects.errors.sindri_validation_error import SindriValidationError


class InvalidIdFormatError(SindriValidationError):
    def __init__(self) -> None:
        super().__init__(
            message="Id must be a valid UUID",
        )
