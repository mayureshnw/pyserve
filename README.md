# pyserve

A hacky python server uses sockets and multiprocessing library. Average request latency to GET /index.html is <50ms

Run Django app by taking teh following steps

1. Copy the server code in application repo or the other way round
2. Create a file (django_app.py in as an example) to import wsgi from your application
3. set app=wsgi.application
4. run `python3 main.py django_app:app`

djangoapp is a functional django application, you can use the above commend to test it out
