# MongoDB Customer Management App on Kubernetes

This project demonstrates a Flask web application that performs CRUD operations on a MongoDB database, deployed on Kubernetes.

## Project Structure

- `mongodb_kub/` - MongoDB application with Flask frontend
  - `app.py` - Flask application for customer management
  - `Dockerfile` - Container definition for the Flask app
  - `mongo-app-deployment.yaml` - Kubernetes deployment for the Flask app
  - `mongodb-deployment.yaml` - Kubernetes StatefulSet for MongoDB
  - `storageclass.yaml` - Storage class definition for MongoDB persistence
  - `load-test.js` - k6 load testing script
  - `cleanup-test-data.js` - Script to clean up test data after load testing

- `mysql_kub/` - MySQL related Kubernetes configurations

## Features

- Customer management web interface
- Create, Read, Update, Delete (CRUD) operations
- Persistent MongoDB storage using Kubernetes PVCs
- Kubernetes deployments for both the application and database
- Load testing capability with k6
- Test data cleanup utilities

## Deployment Instructions

1. Create the storage class:
   ```
   kubectl apply -f mongodb_kub/storageclass.yaml
   ```

2. Deploy MongoDB:
   ```
   kubectl apply -f mongodb_kub/mongodb-deployment.yaml
   ```

3. Deploy the Flask application:
   ```
   kubectl apply -f mongodb_kub/mongo-app-deployment.yaml
   ```

4. Access the application:
   ```
   kubectl port-forward service/mongo-app-service 5000:5000
   ```
   Then open http://localhost:5000 in your browser.

## Load Testing

Use k6 to perform load testing:

```
k6 run mongodb_kub/load-test.js
```

## Cleaning Up Test Data

After running load tests, you can clean up the test data using:

```
k6 run mongodb_kub/cleanup-test-data.js
```

This script will identify and remove all test customers created during load testing.

## Architecture

The application uses a two-tier architecture:
- MongoDB StatefulSet with persistent volume for data storage
- Flask web application for the user interface and business logic

## License

MIT 