# Seeder

[![Code Health](https://landscape.io/github/WebarchivCZ/Seeder/master/landscape.svg?style=flat)](https://landscape.io/github/WebarchivCZ/Seeder/master)
[![Build Status](https://travis-ci.org/WebArchivCZ/Seeder.svg?branch=master)](https://travis-ci.org/WebArchivCZ/Seeder)
[![Coverage Status](https://coveralls.io/repos/github/WebArchivCZ/Seeder/badge.svg?branch=master)](https://coveralls.io/github/WebArchivCZ/Seeder?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/2304c3d9dce54c099c149d3ef7991be1)](https://www.codacy.com/app/visgean/Seeder)
[![Documentation Status](https://readthedocs.org/projects/seeder/badge/?version=latest)](https://seeder.readthedocs.org/en/latest/)
[![Requirements Status](https://requires.io/github/WebArchivCZ/Seeder/requirements.svg?branch=master)](https://requires.io/github/WebArchivCZ/Seeder/requirements/?branch=master)


Web archivists tool for moderating what parts of Czech Internet will be
archived and what parts should die in the shadows of unarchived wasteland.

Documentation is available at [Read the docs](http://seeder.readthedocs.org/en/latest/).

## Production like environment
Docker compose should work out of box after cloning. Run: ```docker-compose up```. Docker-compose mimics production deployment. So important note is you should ```docker volume rm static``` otherwise static_root volume persists and both nginx and django will not show latest output from collectstatic. Or just run ```./local``` which will always delete nginx and django container and static is corectly deployed.

Check [http://localhost](http://localhost) for Seeder, and [http://localhost:8080](http://localhost:8080) for Traefik.

[Webarchiv.cz deployment instructions](ci/README.md)

## Important branches

- master - development branch
- production - production-ready branch
