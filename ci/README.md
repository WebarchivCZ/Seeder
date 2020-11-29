# Nasazení na test a produkci

- Při každém push do repozitáže, dostane Jenkins notifikaci.
- Jenkins naklonuje repozitáře k sobě
- pak se řídí instrukcemi v Jenkinsfile
  - buildne a pushne seeder dockerhub webarchiv/seeder
  -  ansible z šablony v adesáři ci/templates připaví ci/docker-compose-{ env }.yml s testovací nebo produkční konfigurací a nasadí jej.
  - Pokud se jedná o nasazení do produkce, musí se jednat o branch production
  - Produkce se nejdříve nasadí do testovací prostředí https://app.webarchiv.cz
  - Pak je potřeba v Jenkins ruční potvrzení

# Dockerhub tags
- webarchiv/seeder:latest - produkční image
- webarchiv/seeder:develop - vývojový image na test
- webarchiv/seeder:{{ git zkrácený commit hash }} - kvůli zachování artefaktu