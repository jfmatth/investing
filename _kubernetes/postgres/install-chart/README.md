# Installing the Postgres Operator 5.x

https://access.crunchydata.com/documentation/postgres-operator/5.0.5/installation/helm/

## Installing the operator

```
kubectl create namespace pgo-operator
helm install pgo-operator . -n pgo-operator
```

## Create the DB
Helm chart does that

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
