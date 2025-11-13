import json

class CustomJSONError(Exception):
    def __init__(self, error_code, message):
        self.error_code = error_code
        self.message = message
        super().__init__(self.message)

    def to_json(self):
        if hasattr(self, 'error_code'):
            error_dict = {
                "succeeded": False,
                "error": {
                    "error_code": self.error_code,
                    "message": self.message
                }
            }
            return json.dumps(error_dict)
        else:
            result_dict = {
                "succeeded": True,
                "data": self.message
            }
            return json.dumps(result_dict)
