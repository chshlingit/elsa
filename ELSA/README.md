Django 專案下載後請以下列指令啟動

```
$ python3 manage.py migrate
$ python3 manage.py runserver
```

專案中有修改 models.py 後，需執行 
```
python3 manage.py makemigrations
python3 manage.py migrate
```
