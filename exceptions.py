class UnauthorizedException(Exception):
    pass


class DataNotFoundException(Exception):
    pass


class NoWorksheet(Exception):
    pass


class InvalidCompanyCreds(Exception):
    pass


class NoASINInSellerCentral(Exception):
    pass


class InvalidSellerCentralAuth(Exception):
    pass


class NoAccountInSellerBoard(Exception):
    pass


class NoCSRFToken(Exception):
    pass
