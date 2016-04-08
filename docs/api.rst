API
===

This document describes how to work with the Seeder APIs


Authentication
--------------

Authentication is based on token sent over the headers. You will need to get
this token to do anything useful on production environment.

::

    $ http POST :8000/api/token username=username password=heslo -vv
    POST /api/token HTTP/1.1
    Accept: application/json
    Accept-Encoding: gzip, deflate
    Connection: keep-alive
    Content-Length: 47
    Content-Type: application/json
    Host: localhost:8000
    User-Agent: HTTPie/0.9.3

    {
        "password": "heslo",
        "username": "username"
    }

    HTTP/1.0 200 OK
    Allow: POST, OPTIONS
    Content-Language: en
    Content-Type: application/json
    Date: Fri, 08 Apr 2016 00:14:39 GMT
    Server: WSGIServer/0.1 Python/2.7.6
    Vary: Accept-Language, Cookie
    X-Frame-Options: SAMEORIGIN

    {
        "token": "b4a3f506347adcdd51bc3c1e95449002384ab260"
    }


