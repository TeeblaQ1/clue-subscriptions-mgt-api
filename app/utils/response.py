from flask import jsonify

def make_response(message=None, data=None, error=None, status_code=200):
    """
    utility function for creating a response object
    this was created to ensure consistent response format across the app
    while ensuring DRYness
    """
    response = {
        "message": message,
        "data": data,
        "error": error
    }
    return jsonify(response), status_code
