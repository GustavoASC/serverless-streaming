# Serverless Computing for Music Streaming

In order to deploy the Streaming function:

   - faas-cli up -f streaming.yml

In order to deploy the CRUD function:
   - faas-cli up -f crud.yml --build-arg ADDITIONAL_PACKAGE=ffmpeg

The following command is used to start an execution MongoDB container:
   - docker run -d -p 27017:27017 -p 28017:28017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=admin mongo