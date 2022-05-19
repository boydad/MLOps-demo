# syntax=docker/dockerfile:1
FROM mongo
ENV MONGO_INITDB_ROOT_USERNAME=mongo_user
ENV MONGO_INITDB_ROOT_PASSWORD=mongo_password
EXPOSE 27017
celsloaner@CSI0357291 docker % cat omni/Dockerfile 
# syntax=docker/dockerfile:1
FROM vivekratnavel/omniboard
CMD ["--mu", "mongodb://mongo_user:mongo_password@mongo:27017/sacred?authSource=admin"]
EXPOSE 9000
