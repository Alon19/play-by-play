class ELShot(object):
    """
    Class for shot data from Euroleague
    """

    def __init__(self, item):
        for k, v in item.items():
            setattr(self, k, v)

    @property
    def data(self):
        """
        returns shot data dict
        """
        return self.__dict__