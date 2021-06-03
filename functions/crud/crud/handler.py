# --------------------------------------------------------------
# Para ver a senha: sudo cat /var/lib/faasd/secrets/basic-auth-password
#
# Para iniciar o container do mongodb: docker run -d -p 27017:27017 -p 28017:28017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=admin mongo
#
# Para tratar esses parâmetros deve manipular como JSON.
# Exemplo com curl: curl -X POST --header "Content-Type: application/json" --data '{"name":"Teste", "author":"Alok"}' http://192.168.10.165:8080/function/crud
# O que vem em 'req' fica {"name":"Teste", "author":"Alok"}
#
# Para fazer o deploy desta função é necessário instalar o ffmpeg no Linux.
# Não é a biblioteca do Python, é no Linux mesmo.
#
# Para isso usar a command-line abaixo:
#
# faas-cli up -f crud.yml --build-arg ADDITIONAL_PACKAGE=ffmpeg
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

