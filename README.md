## Introduction

A starter CRUD backend App (Skeleton) and REST APIs using Python FastAPI, HANA-ML library, and SAP HANA Cloud as the database.
This code is deployable to SAP BTP Cloud Foundry environment and demonstrates integration with SAP HANA Cloud.

## Instructions

Do `git clone` this repository, you should have `cf-fastapi-hanaml` folder.

Import this [sap.common-Countries.csv](https://github.com/SAP-samples/cloud-cap-samples/blob/main/common/data/sap.common-Countries.csv) into HANA Cloud DB too.

#### # Cloud Foundry Deployment

Login to your SAP BTP Cloud Foundry account and ensure you have a SAP HANA Cloud instance created.

Create a `hana` service instance named `MyHANAApp-dev` with service plan `hdi-shared`:

```
$ cf create-service hana hdi-shared MyHANAApp-dev
```

Wait for the service instance creation to complete, to check run:

```
$ cf services
```

Deploy App to Cloud Foundry runtime:

```
$ cd cf-fastapi-hanaml
$ cf push
```

Navigate to `CF AppRoute URL` to access this backend App and `CF AppRoute URL/api/*` to access the REST APIs.

See [api\route.py](api/route.py) for example supported REST APIs operation.

> Additional notes:
>
> - Above deployment approach is using Cloud Foundry CLI to deploy an application in the Cloud Foundry environment.
>   You can find out how to get and use the Cloud Foundry command line interface [here](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/2f1d4abd0f9f4760a301f43513d2efa6.html), or [here](https://docs.cloudfoundry.org/cf-cli/).
> - For using SAP BTP cockpit to deploy application in the Cloud Foundry environment, please refer to this guide [here](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/09fdb9bdc6804c479d634297f1d07e09.html).

#### # Run on Local Machine

Do `git clone` this repository, you should have `cf-fastapi-hanaml` folder.

```
$ cd cf-fastapi-hanaml
$ python -m venv venv
$ source venv/bin/activate
# On Windows use: venv\Scripts\activate
$ pip install -r requirements.txt
```

Create a `.env` file in the root directory with the following content:

```
HANA_ADDRESS=<address>
HANA_PORT=443
HANA_USER=<user>
HANA_PASSWORD=<password>
HANA_SCHEMA=<schema>
HANA_ENCRYPT=True
HANA_SSL_VALIDATE_CERT=True
```

Then run the application:

```
$ python main.py
```

Navigate to `http://localhost:8080/` to access the Web App frontend and `http://localhost:8080/api/*` to access the REST APIs.

See [app\apis.py](app/apis.py) for complete supported REST APIs operation.

Example of REST API endpoints:

```
http://localhost:8080/api/health -- health check

http://localhost:8080/api/test_connection -- test HANA Cloud DB connection

http://localhost:8080/api//hana_version  -- get HANA Cloud instance version

http://localhost:8080/api/countries  -- get all countries (ISO standard)

http://localhost:8080/api/add/country  -- add new country with JSON data payload:
{
    "NAME": "TestCountry00",
    "DESCR": "Test Description0000",
    "CODE": "ZY"
}

http://localhost:8080/api/update/country/<code>  -- update country by code (case-sensitive) with JSON data payload:
{
    "NAME": "TestCountry11",
    "DESCR": "Test Description1111"
}

http://localhost:8080/api/delete/country/<code>  -- delete country by code (case-sensitive)
```
