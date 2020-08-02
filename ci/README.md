# Nasazení na test a produkci

- Při každém push do repozitáže, dostane Jenkins notifikaci.
- Jenkins naklonuje repozitáře k sobě
- pak se řídí instrukcemi v Jenkinsfile
  - buildne a pushne seeder dockerhub webarchiv/seeder
  -  ansible z šablony v adesáři ci/templates připaví ci/docker-compose-{ env }.yml s testovací nebo produkční konfigurací a nasadí jej.
  - TODO: pokud se jedná o nasazení do produkce, musí se jednat o branch production
  - TODO: před nasazením je potřeba v Jenkins ruční potvrzení
- profit

# Dockerhub tags
- webarchiv/seeder:latest - produkční image
- webarchiv/seeder:develop - vývojový image na test
- webarchiv/seeder:{{ git zkrácený commit hash }} - kvůli zachování artefaktu

# Zálohy
- je třeba zálohovat media adresář
- dump databáze

Export databáze
```bash
sudo su - postgres
pg_dump --format c --compress 9 --no-owner seeder > seeder-prod.gz
```
Provedení importu databáze
```bash
sudo docker-compose -f docker-compose-prod.yml -p seeder stop web
Stopping seeder_web_1 ... done

sudo docker cp seeder-prod.gz seeder_seeder_db_1:/
sudo docker exec -u postgres seeder_seeder_db_1 pg_restore -d seeder --clean seeder-prod.gz
sudo docker-compose -f docker-compose-prod.yml -p seeder start web
```
