class InvalidOrder(Exception):
    pass


class NotEnoughBalance(InvalidOrder):
    pass


class NotFoundOrder(InvalidOrder):
    pass


class APIError(Exception):
    pass
