import sys, os, json
from pymongo import MongoClient
from bson.objectid import ObjectId
from urllib.parse import quote_plus

##
## Para ver a senha: sudo cat /var/lib/faasd/secrets/basic-auth-password
## Para iniciar o container do mongodb: docker run -d -p 27017:27017 -p 28017:28017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=admin mongo
##

## Database connection utilities
DB_NAME = 'openfaas'

def get_uri():
    host = "192.168.10.165:27017"
    password = "admin"
    username = "admin"
    return "mongodb://%s:%s@%s" % (quote_plus(username), quote_plus(password), host)

def get_mongo_client():
    uri = get_uri()
    return MongoClient(uri)

def get_db_collection():
    client =  get_mongo_client()
    db = client[DB_NAME]
    return db.musics


## Crud methods impl

def insert_update(name, author, binary_content):
    collection = get_db_collection()
    music = { "name" : name, "author": author, "binary_content": binary_content}
    res = collection.insert_one(music)
    return "Record inserted: {}".format(res.inserted_id)


def list():
    collection = get_db_collection()
    ret = []
    for music in collection.find():
        ret.append({"id": str(music[u'_id']), "name": music[u'name'], "author": music[u'author']})

    return json.dumps(ret)

def delete(id):
    collection = get_db_collection()
    res = collection.delete_one( {"_id": ObjectId(id)} )
    return "Total records deleted: {}".format(res.deleted_count)


## Main method for handling requests

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    method = os.getenv("Http_Method")
    sys.stderr.write("Method: {}\n".format(method))

    if method in ["POST", "PUT"]:
        # Para tratar esses parâmetros deve manipular como JSON. 
        # Exemplo com curl: curl -X POST --header "Content-Type: application/json" --data '{"name":"Teste", "author":"Alok"}' http://192.168.10.247:8080/function/crud
        # O que vem em 'req' fica {"name":"Teste", "author":"Alok"}
        name = "Star"
        author = "Erasure"
        binary_content = []
        return insert_update(name, author, binary_content)
    elif method == "GET":
        return list()
    elif method == "DELETE":
        id = "609dd9e88281bfe7aa6fcfbe"
        return delete(id)
    else:
        return "Method: {} not supported".format(method)


if __name__== "__main__":
    handle("teste")

