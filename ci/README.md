# Nasazení na test a produkci

- Při každém push do repozitáže, dostane Jenkins notifikaci.
- Jenkins naklonuje repozitáře k sobě
- pak se řídí instrukcemi v Jenkinsfile
  - buildne a pushne seeder dockerhub webarchiv/seeder
  -  ansible z šablony v adesáři ci/templates připaví ci/docker-compose-{ env }.yml s testovací nebo produkční konfigurací a nasadí jej.
  - TODO: pokud se jedná o nasazení do produkce, musí se jednat o branch production
  - TODO: před nasazením je potřeba v Jenkins ruční potvrzení
- profit

## Přístup
TODO: Dořešit frontend -> traefik + static files
