# Plynulé nasazování webového archivu.
Tento dokument popisuje implementaci plynulého nasazování webových stránek [webarchiv.cz](https://webarchiv.cz/cs/). Plynulé nasazování umožňuje okamžité testování nových verzí webové aplikace Seeder a okamžité nasazení do produkce po schválení vedením webového archivu.

[wa-docker-overview]: img/wa-docker-overview.png "Docker overview"
[jenkins-overview]: img/jenkins-overview.png "Jenkins overview"

# Komponenty
## Github
Veřejně přístupné Github repozitáře obsahují zdrojové kódy k těmto komponentám. 
- [Webové rozhraní Seeder](https://github.com/WebarchivCZ/Seeder)
- [NAKI informační stránka](https://github.com/WebarchivCZ/naki)
- [WA-KAT](https://github.com/WebarchivCZ/WA-KAT)

Automatizační kód pro Jenkins je zpravidla součástí repozitářů. Všechny repozitáře jsou umístěny v Github Organizaci [Web archive of National Library of the Czech Republic | WebarchivCZ](https://github.com/orgs/WebarchivCZ). Seznam všech členů organizace je [zde](https://github.com/orgs/WebarchivCZ/people).

Vlastníci organizace:
- [Zdenko Vozár](https://github.com/orgs/WebarchivCZ/people/JanMeritus)
- [Jaroslav Kvasnica](https://github.com/orgs/WebarchivCZ/people/kvasnicaj)
- [Marie Haškovcová](https://github.com/orgs/WebarchivCZ/people/mariehaskovcova)
- [Rudolf Kreibich](https://github.com/orgs/WebarchivCZ/people/westfood)

## Jenkins
Jenkins zajišťuje automatické spouštění procesů při změnách v repozitářích na Github. Github organizace WebarchivCZ při každé aktivitě kontaktuje Jenkins. Veřejné rozhraní je na adrese [jenkins.webarchiv.cz](https://jenkins.webarchiv.cz/).

Jenkins pravidelně kontroluje repozitáře v organizacei Webarchiv.cz pro soubor Jenkinsfile v repozitářách a větvích. Jakmile objeví branch se souborem v Jenkinsfile v kořeni, přidá repozitář a větev s Jenkins file do složky: [Web archive of National Library of the Czech Republic](https://jenkins.webarchiv.cz/job/webarchiv/)

### Každý Push do Github repozitáře notifikuje Jenkins
- Jenkins naklonuje repozitáře do pracovního adresáře
- Pak se řídí instrukcemi v Jenkinsfile -> Obvyklé kroky
  - build a push aplikace do dockerhub webarchiv/aplikace přímo z Jenkis serveru
  - adresář ./ci v repozitáři obsahuje Ansible konfiguraci, obvykle pro vytváření konfigurace z šablon ale i popis kroků, které se musí realizovat na cílovém serveru.
  - Jenkins se autentifikuje v cílových prostředích pomocí privátního klíče Ansible.
  - Jenkins používá Ansible pro realizaci tasků případně spustí příkaz přímo přes SSH, např. v případě pouštění docker compose.
  - větve develop, feature/* se nasazují do testovacího serveru
  - větev production se nasazuje do produkčního serveru
  - před nasazením do produkce je potřeba v Jenkins ruční potvrzení

Přehledový diagram
![jenkins-overview]
### Instalace a konfigurace
- Přes VPN je aplikace nainstalovaná na serveru wa-dev-docker00, na adrese 10.3.0.110. 
- Jenkins je manuálně nainstalovaný pomocí `sudo yum install jenkins`
```
Nainstalované balíčky:
Jméno        : jenkins
Platforma    : noarch
Verze        : 2.181
Vydání       : 1.1
Velikost     : 74 M
Repozitář    : installed
```
  - Plugin Jenkins Github Organization hledá soubor Jenkinsfile v kořeni repozitářů Github organizace WebarchivCZ
  - Integrace je Github je pomocí Tokenu patřícímu Rudolf Kreibich.
  - Jenkins instaluje jak do testovacího tak do produkčního prostředí

### OAuth konfigurace
Adminstrátorská práva: westfood, JanMeritus -> [Definovávno v Jenkins](https://jenkins.webarchiv.cz/configureSecurity/)


Práva na čtení: všichni členové Github Organizace [WebarchivCZ](https://github.com/WebarchivCZ).

Github aplikace [Jenkins Webarchiv](https://github.com/organizations/WebarchivCZ/settings/applications/778696)
- Jenkins konfigurace OAuth: [https://jenkins.webarchiv.cz/configureSecurity/]https://jenkins.webarchiv.cz/configureSecurity/
- Režim přístup:  
```
Requires the Github Authentication Plugin to be used as the authentication source.
We use the OAuth token for each authenticated github user to interact with the Github API to determine the level of access each user should have.

We grant READ and BUILD job permissions to an authenticated user if they are a member in at least one named organization.

We also support defining a set of Jenkins Admin users and whether or not any authenticated user can have READ access to the jobs.
```
### Návrhy na zlepšení
Přejít na Github nebo Gitlab CI/CD offering umožní úplně se zbavit provozu aplikace Jenkins. Nicméně provoz aplikace Jenkins je bezproblémový.

## Docker
Docker umožňuje izolovat exekuční závislosti aplikace od hostujícho operačního systému. Aplikace je tak přenositelná jako kontejner mezi systémy na kterých běží Docker Engine. Pomocí Docker Compose je navíc možné deklarovat více docker kontejnerů a jejich vzájemné prosíťování. Máme tak možnost si pustit např. celé prostředí pomocí příkazu `docker compose up` přímo z kořene tohoto repozitáře, dříve než novou verzi vystavíme v repozitáři.

Docker je nainstalovaný ručně pomocí [oficiální Docker dokumentace pro instalaci pro Centos](https://docs.docker.com/engine/install/centos/).

### Produkční server
**wa-docker00 - 10.3.0.50**
 - Docker kontejnery
   - aplikace:  webarchiv/seeder:latest
   - databáze: postgres:9.6
   - cache:  memcached:latest
   - katalogizační nástroj: wakat:gehorak
   - naki-www image: naki-nkp/naki-www
   - služba pro generáování screenshotů webů: bobey/manet:latest
   - traefik: routovací služba poslouchají na portu 80 a směřující traffic do kontejnerů

### Testoací server
**wa-dev-docker00 - 10.3.0.110**
 - Docker kontejnery
   - aplikace:  webarchiv/seeder:develop
   - databáze: postgres:9.6
   - cache:  memcached:latest
   - katalogizační nástroj: wakat:gehorak
   - naki-www image: naki-nkp/naki-www
   - traefik: routovací služba poslouchají na portu 80 a směřující traffic do kontejnerů

## Traefik 
Routovací služba pro služby běžící v Docker. [Treafik](https://traefik.io/) je jedním z kontejnerů které jsou deklarovány v Docker Compose. Nahrazuje konfigurace nginx pro směřování k jednotlivým kontejnerům. Namísto statické konfigurace nginx, Traefik umožňuje podle deklarace labels pro jednotlivé služby v Docker Compose určit [pravidla směřování](https://doc.traefik.io/traefik/). Traefik v hostujícím OS poslouchá na portu 80.

Přístup z VPN IPs 172.16.3.65, 172.16.3.66, 172.16.3.67. 172.16.3.137
- **Produkce** [10.3.0.50](http://10.3.0.50) nebo wa-docker00
- **Test** [10.3.0.110](http://10.3.0.110) nebo wa-dev-docker00

Přehledový diagram routování do jednotlivých služeb
![Docker overview][wa-docker-overview]

V Docker Compose se služba jmenuje **reverse-proxy**. Image **traefik:v2.8**.

## Ansible
[Ansible](https://www.ansible.com/) je automatizační nástroj vlastněný Red Hat. V systému je použit hlavně pro deklaraci testovacího a produkčního prostředí a renderování templates. Obsahuje také vault soubory zašifrované pomocí AES-256, které obsahují citlivé informace. Heslo k vaultu je uložení v Jenkins. Ansible je nainstalovaný na stejném serveru jako Jenkins. Ansible vyžaduje jen funkční python na cíly automatizace.

## Dockerhub
Na dockerhub je organizace [webarchiv](https://hub.docker.com/orgs/webarchiv) vlastněná Rudolfem Kreibichem a Jaroslavem Kvasnicou. Jenkins po setavení obrazu posílá obraz do Dockerhub pomocí uživatele **webarchivcze**. Uživatelské heslo je uložené v Jenkins.

## Webové rozhraní Seeder
Slouží jako veřejné webové rozhraní uživateli. Mezi hlavní nabízené služby patří katalog webových stránek, tématické sbírky, vyhledávač uchovaných URL a formulář pro návrhy nových zdrojů k archivace. Služba je dostupná na adrese [webarchiv.cz](https://webarchiv.cz).

Součástí webové aplikace Seeder je nevřejné adminstrátorské rozhraní pro kurátory webového archivu dostupné na adrese [seeder.webarchiv.cz](https://seeder.webarchiv.cz/). Slouží nejen jako nástroj pro správu veřejného webového rozhraní, ale uchovává věškeré informace o webových zdrojích, jejich řazení, webových sklizních a dalších důležitých informací které vytvářejí kurátoři webového archivu. Mj. vytváří seznam URL pro sklízeče webového archivu.

Obě rozhraní jsou implementované ve frameworku [Django](https://www.djangoproject.com/) jako jedna webová aplikace.

### Veřejně přístupné produkční rozhraní
- Služba pro uživatele: [https://webarchiv.cz/](https://webarchiv.cz/)
- Služba pro kurátory webového archivu s heslem: [https://webarchiv.cz/admin](https://webarchiv.cz/admin)

### Veřejně přístupné testovací rozhraní
- Služba pro uživatele: [https://app.webarchiv.cz/](https://app.webarchiv.cz/)
- Služba pro kurátory webového archivu s heslem: [https://app.webarchiv.cz/seeder/](https://app.webarchiv.cz/seeder/)

### Dockerhub tags
Komponenta je definována v [Docker Compose](templates/docker-compose.yaml) jako služba **web**. A používá následující konvenci:
- webarchiv/seeder:latest - produkční image
- webarchiv/seeder:develop - vývojový image na test
- webarchiv/seeder:{{ git zkrácený commit hash }} - kvůli zachování artefaktu
### Přehled
- Zdrojový kód: [Github](https://github.com/webarchivcz/seeder/)
  - Větve:
    - **production**: produkční větev která se nasazuje na produkční prostředí
    - **master**: vývojová větev která nasazuje na testovací prosředí
    - **feature/***: vývojová větve které nasazuje na testovací prosředí
- Dockerhub repozitář [webarchiv/seeder](https://hub.docker.com/repository/docker/webarchiv/seeder)
  - Docker image je veřejný a neobsahuje žádná hesla.
  - Tagy:
    - latest - produkční image
    - develop - vývojový image na test
    - {{ git zkrácený commit hash }} - kvůli zachování artefaktu na dockerhub

V Docker Compose se služba jmenuje **web**. Image: ***webarchiv/seeder:{{ seeder_docker_tag }}**.
### Databáze pro aplikaci Seeder
Aplikace Seeder, přesnějši Django ukládá všechny inforamce krom obrázků v PostgreSQL databázi. Databáze je vedle samotného archivů webů nejcennější komponenta.

V Docker Compose se služba jmenuje **seeder_db**. Image: **postgres:9.6**.
## Statické obrázky
Seeder automaticky generuje snapshoty všech webů v katalogu. Tyto obrázky, spolu se soubory nahranými do Django dynamicky pomocí webového rozhraní nejsou vhodné k hostování skrze Django. Proto se tyto binární soubory hostují skrze kontejner obsahují nginx, který je hostuje.

V Docker Compose se služba jmenuje **static**. Image: **nginx:alpine**.
## Cache
Memcache pro cachovací potřeby Djanga.

V Docker Compose se služba jmenuje **memcached**. Image: **memcached:latest**.
## Statická HTML pro NAKI (vyvoj)
Několik statických HTML, které se časem integrují přímo do aplikace Seeder. Pro zatím jsou hostovány jako image. [NAKI informační stránka](https://github.com/WebarchivCZ/naki). Pokud dojde ke změně, repozitáře pošle image do dockerhub. Pak je potřeb redeploynout patřičné prostředí Seeder aby se nahrála nová verze vývoje. Viz standardní procedury [Nasazení nové verze Vývoj na produkční prostředí](#Nasazení-nové-verze-vývoj-na-produkční-prostředí) a [Nasazení nové verze Vývoj na testovací prostředí](#Nasazení-nové-verze-vývoj-na-testovací-prostředí).

- Testovací prostředí: https://app.webarchiv.cz/vyvoj/
- Produkční prostředí: https://webarchiv.cz/vyvoj/

V Docker Compose se služba jmenuje **vyvoj**. Image **webarchiv/vyvoj:naki**.

## Manet
Nástroj jež používá Seeder aby vytvářer snapshoty webů které má v katalogu.

V Docker Compose se služba jmenuje **manet**. Image **bobey/manet:latest**.

## Katalogizační nástroj WaKat
Polo automatický nástroj na katologizaci webů. Změna [WA-KAT](https://github.com/WebarchivCZ/WA-KAT) automaticky spouští aktualizaci testu nebo produkce. Nástroj je dostupný na adrese: [kat.webarchiv.cz](https://kat.webarchiv.cz/). Nástroj není součástí Docker Compose.

# Standardní procedury
## Nasazení nové verze Seeder na test
1. Vytvořit PR vůči branch master
2. Merge PR do branch master spustí nasazení kódu na testovací prostředí
## Nasazení nové verze Seeder na produkci
1. Vytvořit PR vůči branch production
2. Merge PR do branch production spustí nasazení kódu na testovací prostředí
3. Vedoucí webového archivu nebo vedoucí podpory aplikací schválí konkrétní build v (Jenkins)[https://jenkins.webarchiv.cz/job/webarchiv/job/Seeder/job/production/]

## Nasazení nové verze Vývoj na testovací prostředí
1. Push do větve `main` v repozitáři [https://github.com/WebarchivCZ/naki](https://github.com/WebarchivCZ/naki) spustí nasazení kódu do testovacího prostředí.

## Nasazení nové verze Vývoj na produkkční prostředí
1. Vytvořit Pull Request vůči větvi `production` v repozitáři [https://github.com/WebarchivCZ/naki](https://github.com/WebarchivCZ/naki)
2. Merge Pull Request do větve `main` spustí nasazení nejdříve kódu na testovací prostředí
3. Vedoucí webového archivu nebo vedoucí podpory aplikací schválí konkrétní build v (Jenkins)[https://jenkins.webarchiv.cz/job/webarchiv/job/Seeder/job/production/] a poté je teprve nasazen kód do produkčního prostředí.

## Zálohy produkčního prostředí
### Adresář media
1. Přihlásit se na serveru ```ssh $(whoami)@10.3.0.50```
2. Vykopírovat adresář media z kontejneru do aktuální cesty /home/$(whoami) ```sudo docker cp seeder_web_1:/code/Seeder/media ./media-prod-$(date -Iminutes)```
3. Změnit práva ```chown $(whoami):$(whoami) ./media-[datum vytvoření složky]```
4. Odpojit se ze serveru ```exit```
5. Zkopírovat vzniklý adresář z bezpečného místa ```scp $(whoami)@10.3.0.50:/$(whoami)/media-[datum vytvoření složky] .```
### Záloha databáze z Postgres

Export databáze Seeder
```bash
sudo docker exec -u postgres seeder_seeder_db_1 pg_dump --format c --compress 9 --no-owner seeder > seeder-prod-$(date -Iminutes).gz
```
Záloha celého Postgres
``` bash
sudo docker exec -u postgres seeder_seeder_db_1 pg_dumpall > postgres-prod-$(date -Iminutes).sql
```

### Vykopírování záloh ze severu.
`scp -r wa-docker00:"/home/{{ vlastník_záloh }}/*-prod-[datum-vytvoření-složky]*" .`
### Importu databáze
```bash
sudo docker-compose -f docker-compose-prod.yml -p seeder stop web
Stopping seeder_web_1 ... done

sudo docker cp seeder-prod.gz seeder_seeder_db_1:/
sudo docker exec -u postgres seeder_seeder_db_1 pg_restore -d seeder --clean seeder-prod.gz
sudo docker-compose -f docker-compose-prod.yml -p seeder start web
```

## Souhrný stav dokumentace
- [x] Dokumentace
  - [x] Seznam serverů
  - [x] Seznam kontejnerů
  - [x] Standardní procedury
    - [x] Aktualizace aplikace
    - [x] Záloha databáze
- [ ] Zálohy
  - [ ] Automatická záloha postgres databáze
- [ ] Monitorování
  - [x] Zpracování chyb aplikace https://sentry.webarchiv.cz
  - [ ] Zpracování logů
  - [ ] Alerting dostupnosti služeb
- [x] Automatizace
  - [x] Jenkinsfile
    - [x] Nasazování nových verzí
