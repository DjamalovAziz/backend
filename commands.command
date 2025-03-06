

pip freeze > requirements.txt

for /d /r %d in (__pycache__) do @if exist "%d" rd /s /q "%d"

pip install --default-timeout=1000 

python manage.py createsuperuser

pip install -r requirements.txt

Remove-Item Env:DEBUG

Get-ChildItem Env:DEBUG
