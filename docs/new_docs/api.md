### Base API URL: /seeder/api/

By default, all API endpoints required the user to be authenticated either in Session (using a cookie) or by an API Token.

## TODO

- [ ] Get rid of deprecated Harvest URLs both in API and in Harvest catalogue.
- [ ] https://github.com/WebarchivCZ/Seeder/issues/593 : Better endpoints for Harvests/Collections by date, should replace the current ones.
- [ ] Rewrite the rest of the Harvest URLs and perhaps Dumps to REST ViewSets so REST Framework authentication can be enforced.

---

# Authentication

### `/seeder/api/token/ [POST]`

Get a REST Framework token by logging in.

`POST {username: str, password: str}`: returns `{token: str}`

### `/seeder/api/auth/login/ [GET, POST]`

Classic HTML login page. Can also submit {username, password} with POST but a CSRF token is needed.

### `/seeder/api/auth/logout/ [GET, POST]`

Simple logout page, any request to it will log out the current user.

# HarvestConfig

**API is only accessible using Session authentication, not using a Token.**

### `/seeder/api/harvest_config/ [GET]`

- `GET`: List all available Harvest Configurations

```
[
    {
        "harvest_type": "serials",
        "duration": 259200,
        "budget": 10000,
        "dataLimit": 10000000000,
        "documentLimit": 0,
        "deduplication": "PATH"
    },
    ...
]
```

- `GET ?harvest_type={type}`: \
  Retrieve only configurations with the specified `{type}`, still in a list. \
  `{harvest_type}` is a unique property (only one can exist) but if none exist, returns an empty list.

### `/seeder/api/harvest_config/{id}/ [GET]`

- `GET $id`: Retrieve a Harvest Configuration by its ID – **not used**

# Blacklists

### `/seeder/api/blacklist/ [GET]`

- `GET`: List all available Blacklists

```
[
    {
        "id": 1,
        "active": true,
        "created": "2019-07-03T10:18:30.490837Z",
        "last_changed": "2019-07-08T09:56:21.955846Z",
        "title": "2. uroven Whitelist Svet",
        "blacklist_type": 1,
        "url_list": "1229.webnode.cz\r\n14-15.cz\r\n147.228.94.30\r\n147.231.53.91\r\n..."
    },
    ...
]
```

### `/seeder/api/blacklist/{id}/ [GET]`

- `GET $id`: Retrieve a specific Blacklist by its ID and all its fields.

### `/seeder/api/blacklist/lastchanged/ [GET]`

- `GET`: Retrieve the ISO timestamp of the last change across all Blacklists.

```
{ "lastChanged": "2022-05-05T12:00:46.944898Z" }
```

# Data Retrieval & Updating

### `/seeder/api/category/{id}/ [GET]`

- `GET $id`: Retrieve a specific Category by its ID and all its fields.

### `/seeder/api/source/{id}/ [GET, PATCH]`

- `GET $id`: Retrieve a specific Source by its ID and all its fields.
- `PATCH $id {partial_fields}`: Update selected Source's fields using partial update.

### `/seeder/api/seed/{id}/ [GET, PATCH, PUT]`

- `GET $id`: Retrieve a specific Seed by its ID and all its fields.
- `PATCH $id {partial_fields}`: Update selected Seed's fields using partial update.
- `PUT $id {fields}`: Update selected Seed's fields in full.

# Harvest URLs

At the moment, these are all Django views rather than REST Framework ViewSets, since originally, these were meant to return plaintext rather than JSON.

Dates are in the format `{YYYY-MM-DD}`, e.g. "2022-05-05".

Most of these endpoints are now deprecated or should become such.

### `/seeder/harvests/{date}/harvests [GET]`

Retrieve a plaintext list of `/seeder/harvest/{id}/urls` endpoints for the Harvests scheduled on the specified date. \
Each URL is on a separate line.

### `/seeder/harvests/{id}/urls [GET]`

Retrieve a plaintext list of all the Seeds (URLs) for a specific Harvest by its ID. \
Each Seed is on a separate line.

### `/seeder/harvests/{id}/json [GET]`

Retrieve a more robust set of information about a specific Harvest by its ID.

The information includes relevant dates, Harvest's metadata, and all its Seeds split into their relevant collections.

```
{
    "idHarvest": 32,
    "dateGenerated": "2022-05-05T09:01:56.748312+00:00",
    "dateFrozen": null,
    "plannedStart": "2021-12-23T11:26:00+00:00",
    "type": "serials",
    "combined": false,
    "name": "Serials_2021-12-23_M0-OneShot",
    "anotation": "Serials sklizeň s frekvencí 0x ročně ~ Serials sklizen pro OneShot+Custom seminka",
    "hash": "ef9a1bef68e24d9ab5481c5f685fc7b6",
    "seedsNo": 94,
    "duration": 259200,
    "budget": 10000,
    "dataLimit": 10000000000,
    "documentLimit": 0,
    "deduplication": "PATH",
    "collections": [
        {
            "name": "Serials_M0_2021-12-23",
            "collectionAlias": "M0",
            "annotation": "Serials sklizeň s frekvencí 0x ročně",
            "nameCurator": null,
            "idCollection": null,
            "aggregationWithSameType": true,
            "hash": "fd2c9e4e61377fb93b5ffee86d815f55",
            "seedsNo": 48,
            "seeds": [
                "http://casodej.cz/analyza17.htm",
                "http://dejepis.pajka.info",
                "http://dieceze.misto.cz",
                ...
            ]
        },
        ...
    ]
}
```

### `/seeder/harvests/{date}/shortcut_urls [GET]`

Retrieve a list of `/seeder/harvests/{date}/seeds-{date}-{shortcut}.txt [GET]` endpoints for the Harvests scheduled on the specified date. \
Each URL is on a separate line.

### `/seeder/harvests/{date}/seeds-{date}-{shortcut}.txt [GET]`

Retrieve a list of Seeds for a particular date and for a particular "shortcut", e.g. "V1", "OneShot", "ArchiveIt", ...

This endpoint is now deprecated, and while it can still be accessed, it shouldn't be used as it doesn't return sensible data.

# Dumps

### `/seeder/source/dump [GET]`

Retrieve a dump of all public Seeds, one per line. \
**Accessible publicly, without authentication.**

### `/seeder/blacklists/dump [GET]`

Retrieve a dup of all URLs on all Blacklists, one per line. \
**Accessible publicly, without authentication.**
