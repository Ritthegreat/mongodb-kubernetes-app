# MongoDB Kubernetes Application

This application allows you to run basic MongoDB commands within a Kubernetes cluster.

## Components

1. **MongoDB StatefulSet** - Deploys MongoDB with persistent storage
2. **Flask Web Application** - Provides a web interface to interact with MongoDB

## Deployment Instructions

### Step 1: Deploy MongoDB

```bash
kubectl apply -f mongodb-deployment.yaml
```

This will create:
- A MongoDB StatefulSet with 1 replica
- A headless service to access MongoDB
- A PersistentVolumeClaim for data storage

### Step 2: Build and Push the Flask Application

```bash
# Build the Docker image
docker build -t <your-dockerhub-username>/mongo-flask-app:latest .
#docker build -t ritviksinha/mongo-flask-app:latest .

# Push to Docker Hub
docker push <your-dockerhub-username>/mongo-flask-app:latest
#docker push ritviksinha/mongo-flask-app:latest .
```

### Step 3: Update the Application Deployment

Edit `mongo-app-deployment.yaml` and replace:
with:
```yaml
image: <your-dockerhub-username>/mongo-flask-app:latest
#image: ritviksinha/mongo-flask-app:latest
```

### Step 4: Deploy the Flask Application

```bash
kubectl apply -f mongo-app-deployment.yaml
```

### Step 5: Access the Application

```bash
# Port-forward to access the app
kubectl port-forward svc/mongo-app-service 5000:5000
```

Visit [http://localhost:5000](http://localhost:5000) in your browser.

## Using the Application

The web interface allows you to:

1. **Insert documents** into MongoDB collections
2. **Find documents** based on query criteria
3. **Update documents** in collections
4. **Delete documents** based on criteria
5. **List all collections** in the database

## Troubleshooting

If you encounter issues:

1. Check MongoDB pod status:
   ```bash
   kubectl get pods -l app=mongodb
   ```

2. Check application pod status:
   ```bash
   kubectl get pods -l app=mongo-app
   ```

3. View application logs:
   ```bash
   kubectl logs -l app=mongo-app
   ```

4. Check MongoDB service:
   ```bash
   kubectl describe service mongodb-service
   ``` 