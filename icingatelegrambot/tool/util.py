
class Util:
    @staticmethod
    def safe_list_access(li, index, default_value=None):
        try:
            return li[index]
        except IndexError:
            return default_value