# MLOps-demo
Demonstration of two popular MLOps: [Sacred](https://github.com/IDSIA/sacred) and [WandB](https://wandb.ai/home).

## Containers
For testing sacred + omniboard two containers are prepared. Container [mongo](https://hub.docker.com/repository/docker/boyda/mongo) contains mongo data base. It can be run with 
```
docker run -dp 27017:27017 \
 -v $PWD/mongo:/data/db \
 -v $PWD/mongo:data/configdb \
 --network mongo \
 --network-alias boyda/mongo \
 mongo
```
Singularity container can be build with 
```
singularity build omni.simg docker://boyda/omni
```
and executed with
```
nohub singularity run \
 -B $PWD/mongo:data/db \
 -B $PWD/mongo:data/configdb \
 --hostname mongo mongo.simg &
```
After execution this container launches mongo database instance and binds it to port 27017. Sacred application may use `mongo:27017` host for logging.

Another container [omni](https://hub.docker.com/repository/docker/boyda/omni) launches [omniboard](https://github.com/vivekratnavel/omniboard) dashboard for sacred. It can be run with
```
docker run -dp 9000:9000 --network mongo omni
```
After launching one can acces dashboard at `localhost:9000`.

### Docker files
Docker files for containers are available in folder dockerfiles. Building is straghforward (e.g. `docker build -t omni dockerfiles/omni/`).

# Experiments
The first seven experiments are simple and presented in slides. The eits could be runned with
```
WANDB_API_KEY=you_wandb_api python exp8.py -u with batch_size=30000 model_path=models
```

Weights and Biases dashboard with experiments is [here](https://wandb.ai/alcf-datascience/demo).

