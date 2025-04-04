### Lumières-Lausanne 2025
---
1. Clone project :
```
git clone git@github.com:unil-lettres/lumieres-lausanne-2025.git
```
2. Start mysql database :
```
docker compose up -d db
```
3. **Copy** ```django_db_dump.sql``` to ```./sql``` folder

5. Restore database from dump :
```
docker exec -i db mysql -uroot -proot_password django_db < ./sql/django_db_dump.sql
```
5. **Copy** ```media``` folder to ```./django/lumieres```
   
6. Start django server :
```
docker compose up -d
```

7. Browse to ```localhost:8000```
8. Django admin user : ```admin```/```admin```