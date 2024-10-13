echo Delevelopment Server Starting...
flask --app app run --host=0.0.0.0 --port=8787 

gunicorn --threads 8 app:app