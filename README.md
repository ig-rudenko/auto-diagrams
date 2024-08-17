## Auto Diagrams

Создает диаграмму из сервисов docker-compose.yaml

Картинка создается рядом с указанным файлом `docker-compose` и называется так же,
но формат `.png`


### Простой пример

```shell
python draw_diag.py compose-examples/django-app.yaml
```

![django-app.png](img/django-app.png)


### Добавим связи

Через указание `depends_on` либо `links`

```shell
python draw_diag.py compose-examples/django-app-links.yaml
```

![django-app-links.png](img/django-app-links.png)


### Добавим подсети

```shell
python draw_diag.py compose-examples/django-app-networks.yaml
```
![django-app-networks.png](img/django-app-networks.png)


### Укажем псевдоним для образа контейнера

Иконки для сервисов определяются через названия образов контейнера.

Допустим - `image: nginx` отобразит иконку для nginx.

Чтобы настроить иконку для своего сервиса, надо задать псевдоним для образа контейнера: `my-app=django`

```shell
python draw_diag.py compose-examples/django-app-networks.yaml my-app=django
```

<img height="500px" src="img/django-app-alias.png">


### Вариант с несколькими django контейнерами

```shell
python draw_diag.py compose-examples/django-app-multi.yaml my-app=django my-api=fastapi
```

![django-app-multi.png](img/django-app-multi.png)