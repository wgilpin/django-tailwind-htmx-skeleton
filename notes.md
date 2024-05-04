## Run tailwind
```
npm run tw
```

or

```
npx tailwindcss -i ./static/src/input.css -o ./doofer/static/src/styles.css --watch
```

## Run Django

```
python manage.py runserver
```

## Migrations

Use the app name

```
python manage.py makemigrations doofer
python manage.py migrate 
```

## Cached CSS

Works ok in external browser. Click on the url that runserver makes (http://127.0.0.1:8000/)