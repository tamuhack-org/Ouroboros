from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class FileSizeValidator(object):

    """Validator to ensure files are of a desired size or less."""

    message = "File size %(filesize)s is too large. Files must be less than: %(max_filesize)s."
    code = "invalid_filesize"

    def __init__(self, max_filesize=None, message=None, code=None):
        """Note: max_filesize will be interpreted as MB (i.e. max_filesize=1.2 -> 1.2 MB)."""
        self.max_filesize = max_filesize
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        size = value.size
        mb_to_bytes = 1e6
        if self.max_filesize is not None and size > (self.max_filesize * mb_to_bytes):
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    "filesize": f"{round(size / mb_to_bytes, 2)} MB",
                    "max_filesize": f"{self.max_filesize} MB",
                },
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.max_filesize == other.max_filesize
            and self.message == other.message
            and self.code == other.code
        )
