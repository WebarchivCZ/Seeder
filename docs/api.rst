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



Source endpoint
---------------

The most useful API is the source endpoint. This can be used to retrieve and
update the source data.

The source url is on ``/api/source/<id>``

[GET]
-----


The get request will return document with following structure:

.. code-block:: json

        {
            "active": true,
            "aleph_id": "2121",
            "annotation": "document annotation",
            "category": 12,
            "comment": "internal comment",
            "created": "2016-02-06T00:41:45.453995Z",
            "frequency": 12,
            "id": 1,
            "issn": "1212-50125",
            "last_changed": "2016-04-07T22:45:41.873747Z",
            "mdt": "02",
            "name": "Source name",
            "publisher": {
                "active": true,
                "contacts": [
                    {
                        "active": true,
                        "address": "Praha",
                        "created": "2016-02-06T00:40:39.625087Z",
                        "email": "redakce@example.com",
                        "id": 1,
                        "last_changed": "2016-02-06T00:40:39.625110Z",
                        "name": "Petra",
                        "phone": null,
                        "position": null,
                        "publisher": 1
                    }
                ],
                "created": "2016-02-06T00:40:06.532276Z",
                "id": 1,
                "last_changed": "2016-02-06T00:40:06.532302Z",
                "name": "Example publisher"
            },
            "publisher_contact": 1,
            "screenshot": "http://localhost:8000/media/screenshots/1_04042016.png",
            "screenshot_date": "2016-04-04T00:37:20.388037Z",
            "seed": {
                "active": true,
                "budget": null,
                "calendars": false,
                "comment": "",
                "created": "2016-02-06T00:52:32.701084Z",
                "from_time": null,
                "gentle_fetch": "",
                "global_reject": false,
                "id": 322,
                "javascript": false,
                "last_changed": "2016-03-16T23:40:57.124311Z",
                "local_traps": false,
                "redirect": false,
                "robots": false,
                "state": "exc",
                "to_time": null,
                "url": "http://www.example.com",
                "youtube": false
            },
            "state": "success",
            "sub_category": 235,
            "suggested_by": null
        }


For source and state values / meaning see ``Seeder/source/constants.py`` file.

[PATCH]
-------


You can update the source document with the same structure as displayed in GET.
You should only list the fields that you wish to update.

Following example shows partial update of the source document.

.. code-block:: json

    {
       "seed":{

          "url": "http://www.example.com",
          "global_reject": true
       },
       "name": "New source name",
       "sub_category": 231
    }

