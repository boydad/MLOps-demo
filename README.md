# MLOps-demo
Demonstration of two popular MLOps: [Sacred](https://github.com/IDSIA/sacred) and [WandB](https://wandb.ai/home).

## Containers
For testing sacred + omniboard two containers are prepared. Container [mongo](https://hub.docker.com/_/mongo) contains mongo data base. It can be run with 
```
docker run -dp 27017:27017 \
 -v $PWD/mongo:/data/db \
 -v $PWD/mongo:/data/configdb \
 -v $PWD/init-sacred-db.js:/docker-entrypoint-initdb.d/mongo-init.js \
 --enf-file .env \
 --network mongo \
 --network-alias mongo \
 mongo
```
Singularity container can be build with 
```
singularity build mongo.simg docker:mongo
```
and executed with
```
nohup singularity run \
 -B $PWD/mongo:/data/db \
 -B $PWD/mongo:/data/configdb \
 -B $PWD/init-sacred-db.js:/docker-entrypoint-initdb.d/mongo-init.js \
 --env-file .env mongo.simg &
```
When executed this container creates a mongo database listening port 27017. The database stores data and configuration in folder `$PWD/mongo`, if this folder does not exist user have to create it before running the container. Initialization of database happens if folder `$PWD/mongo` is empty. During initialization:
* administrator user `$MONGO_INITDB_ROOT_USERNAME` with password `$MONGO_INITDB_ROOT_PASSWORD` and root priviledges is created;
* database `$MONGO_DATABASE` is created;
* and initialization script `$PWD/init-sacred-db.js` is called. 
 
Initialization script creates a user for database `sacred`. Environmental variables are defined in file `.env` 

When this databse is running Sacred application may use Mongo Observer for logging with user defined in `$PWD/init-sacred-db.js` and database `$MONGO_DATABASE`:
```
MongoObserver.create(
 url=f'mongodb://user:pwd@localhost/sacred',
 db_name='sacred'
)
```
In case when mongo database and sacred scripts are running on different hosts user should change `localhost` to the host of the mongo database. Mongo client could be run with executing mongo container
```
singularity exec  -B $PWD/mongo:/data/db  -B $PWD/mongo:/data/configdb -B $PWD/init-sacred-db.js:/docker-entrypoint-initdb.d/mongo-init.js mongo.simg bash
```
and running a client
```
mongo admin -u mongo_user -p mongo_password
```


Another container [omni](https://hub.docker.com/repository/docker/boyda/omni) launches [omniboard](https://github.com/vivekratnavel/omniboard) dashboard for sacred. It can be run with
```
docker run -dp 9000:9000 --network mongo omni
```
After launching one can acces dashboard at `localhost:9000`.

Singularity container bould be build with 
```
singularity build omni.simg docker://boyda/omni
```


### Docker files
Docker files for containers are available in folder dockerfiles. Building is straghforward (e.g. `docker build -t omni dockerfiles/omni/`).

# Experiments
The first seven experiments are simple and presented in slides. The eits could be runned with
```
WANDB_API_KEY=you_wandb_api python exp8.py -u with batch_size=30000 model_path=models
```

Weights and Biases dashboard with experiments is [here](https://wandb.ai/alcf-datascience/demo).

