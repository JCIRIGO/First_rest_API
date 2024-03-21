# CONTRIBUTING
## How to run the Dockerfile locally 
# Remember we made changes to the dockerfile to use gunicorn instead of flask development server and flask debugger
# use this code to create the container 
```
docker run -dp 5000:5000 -w /app -v "$(pwd):/app" <IMAGE_NAME> sh -c "flask run --host 0.0.0.0"
```