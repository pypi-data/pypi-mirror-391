
"""We use that class for TypeError"""
class RelativeTypeError(Exception):
    def __init__(self, message="You possible give wrong arguments type not a Rectangle"):
        super().__init__(message=message)

    

"""That class use for prohibition action of client who use that Engine with bad target"""
class ProhibitionError(Exception):
    def __init__(self, message="You use imports [sys, os] in your config with bad target. Please without negative"):
        super().__init__(message)


"""We use that class for bonus"""
class AdminStateError(Exception):
    def __init__(self, *args):
        super().__init__(*args)



class OperationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class SmallResolutionError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


"""That Exception was created for reason to kill program if attribute created before other main attribute and etc"""
class BeforeCreatedError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

