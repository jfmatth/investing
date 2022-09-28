# Start at the Crunchy Deverloper site
https://www.crunchydata.com/developers/download-postgres/containers/postgres-operator-5x  

We are currently running 5. 

# Installing the Postgres Operator 5.x and database

https://access.crunchydata.com/documentation/postgres-operator/5.1.0/installation/helm/


## Installing the CrunchyData Postgres operator (v5.10)

Take note that the operator is in it's own namespace

```
cd postgres/pgo-install-chart
kubectl create namespace postgres-operator
helm install pgo . -n postgres-operator
```

## Create the Database for sotb

Create the DB in the current namespace, or whichever you want, it doesn't (nor should be) the same as the operator
```
cd postgres/postgres/sotb-database-chart
helm install sotb-db .
```


## Connect to the DB via PSQL
Adapting https://access.crunchydata.com/documentation/postgres-operator/v5/quickstart/#connect-using-a-port-forward to what we need

### (optional) setup port forward
**You'll need to account for the namespace and add it to the command below**

```
PG_CLUSTER_PRIMARY_POD=$(kubectl get pod -o name -l postgres-operator.crunchydata.com/cluster=sotb,postgres-operator.crunchydata.com/role=master)
kubectl  port-forward "${PG_CLUSTER_PRIMARY_POD}" 5432:5432
```
### PSQL access

We have a user ```adminsyymgnc``` defined in the values file, so that will be the user created for this DB

```
PG_CLUSTER_USER_SECRET_NAME=sotb-pguser-adminsyymgnc
PGPASSWORD=$(kubectl get secrets  "${PG_CLUSTER_USER_SECRET_NAME}" -o go-template='{{.data.password | base64decode}}') \
PGUSER=$(kubectl get secrets  "${PG_CLUSTER_USER_SECRET_NAME}" -o go-template='{{.data.user | base64decode}}') \
PGDATABASE=$(kubectl get secrets  "${PG_CLUSTER_USER_SECRET_NAME}" -o go-template='{{.data.dbname | base64decode}}') \
psql -h localhost
```




# notes

## restart the DB
from https://access.crunchydata.com/documentation/postgres-operator/5.0.5/tutorial/administrative-tasks/  

```
kubectl patch postgrescluster/sotb-qa -n postgres-operator --type merge --patch '{"spec":{"metadata":{"annotations":{"restarted":"'"$(date)"'"}}}}'
```

