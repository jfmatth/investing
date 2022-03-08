# Installing the Postgres Operator 5.x and database

https://access.crunchydata.com/documentation/postgres-operator/5.0.5/installation/helm/

## Installing the operator


```
cd postgres/pgo-install-chart
kubectl create namespace pgo-operator
helm install pgo-operator . -n pgo-operator
```

## Create the DB
Create the DB in the current namespace, or whichever you want, it doesn't (nor should be) the same as the operator
```
cd postgres/postgres/database-chart
helm install sotb-db .
```

## get the URI for the DB in the app

```
spec:
      containers:
      - image: 
        name: keycloak
        env:
        - name: DB_URL
          valueFrom: { secretKeyRef: { name: sotb-pguser-sotb, key: uri } }
```
