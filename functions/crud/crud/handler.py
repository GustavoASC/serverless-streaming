# --------------------------------------------------------------
# Function handler
# --------------------------------------------------------------
from .httpimpl import HttpImpl

def handle(event, context):
    try:

        method = event.method
        http = HttpImpl(event.path, event.body)
        
        result = ""
        if method == "POST":
            result = http.post()
        elif method == "GET":
            result = http.get()
        elif method == "DELETE":
            result = http.delete()
        else:
            result = "Method: {} not supported".format(method)

        return {
            "statusCode": 200,
            "headers": {
                "Content-type": "text/plain; charset=utf-8",
                "content-length": len(result),
                "access-control-allow-origin": "*"
            },
            "body": result
        }

    except Exception as err:
        return str(err)



if __name__ == "__main__":
    print(handle("", ""))

