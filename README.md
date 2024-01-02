# Connect Pay: A Payment service that handles multiple payment gateways.

Welcome to connect pay project! This project is built on FastAPI, a modern, fast (high-performance), web framework for
building APIs with Python 3.7+ based on standard Python type hints. It uses APIFort as an identity service. It's
designed to help developers for reducing the time of integrating with a payment gateway and it keeps track of logs and
the status of the payments.

Connect Pay includes multiple components and this guide will help you to walk through the process of setting up the
project on your machine.

## Prerequisites

Before you begin make sure that you have the following installed :

1. **Docker**
2. **APIFort**

## Getting Started:

1. **APIFort :**
    1. Follow API Fort's [Documentation](https://apitfort.developerhub.io/api-fort/apifort-getting-started) to setup
       APIfort.
    2. Then you can follow this [Documentation](https://apitfort.developerhub.io/api-fort/kc-setup-and-configuration) to
       setup Key cloak.

2. **Connect Pay:**

    1. Clone the main repository: git clone `https://github.com/abdawwa1/connect-pay`
    2. Enter the directory of connect pay and build docker image : `cd connect-pay-project make image`
    3. After the image build finishes, Go to docker engine-> Settings -> Resources -> File sharing -> Add the path of
       `connect-pay-project` then you can , Run the following command to start PSQL : `make services` or `make services-d`
    4. Create .env file in connect-pay-project directory and add the following variable `DATABASE_URL=postgresql:
       //postgres@postgres/connect-pay` && `connect_pay_key=-----BEGIN PUBLIC KEY-----\n<REPLACE WITH KC REALM PUBLIC KEY>
       \n-----END PUBLIC KEY-----`
    5. After we have successfully started PSQL and gave docker access to mount a volume for the DB, we cant start the
       project
       by running the following command: `make dev-run`
    6. Hooray ! Now the project is running and we can start testing the service. 🎉