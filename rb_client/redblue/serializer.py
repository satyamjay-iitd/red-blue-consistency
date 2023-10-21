class PythonRespSerializer:
    def __init__(self, encode) -> None:
        self.encode = encode

    def pack(self, *args):
        """Pack a series of arguments into the RedBlue protocol"""
        return b" ".join(map(self.encode, args))
