### Lumières-Lausanne 2025
---
- Clone project :
```bash
git clone git@github.com:unil-lettres/lumieres-lausanne-2025.git
```
- Start database :
```bash
docker compose up db
```
- Import SQL dump into database :
```bash
docker exec -i db mysql -uroot -proot_password django_db < ./django_db_dump.sql
```
- Copy 'media' folder to django/lumieres/
- Django admin user : admin/admin
