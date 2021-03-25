class Error(Exception):
    pass


class NotFoundError(Error):
    pass


class NotAuthenticatedError(Error):
    pass


class AccessDeniedError(Error):
    pass


class BadRequest(Error):
    pass


class ServerError(Error):
    pass
