import json

def generate_output(succeeded, data=None, error_code=None, message=None):
    output = {"succeeded": succeeded}

    if succeeded:
        output["data"] = data
    else:
        output["error"] = {"error_code": error_code, "message": message}

    return json.dumps(output)
