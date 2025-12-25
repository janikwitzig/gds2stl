class Layer:

    def __init__(self, layer_no, datatype=0, name=""):
        self.layer_no = layer_no
        self.datatype = datatype
        self.name = name
        self._zstart = 0.0
        self._zheight = 0.5
        self.color = (255, 255, 255)
        self._subtract_layers = []
