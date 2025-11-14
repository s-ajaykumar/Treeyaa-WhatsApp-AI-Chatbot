class MyAppError(Exception):
    def __init__(self, error_type, data):
        super().__init__(f"{error_type}: {data}")
        self.error_type = error_type
        self.data = data
        
    def to_dict(self):
        data =  f"{self.error_type}:\n{type(self.data).__name__}: {self.data}"
        return {"type" : "error", "data" : data}