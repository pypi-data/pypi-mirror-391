La forma de hacer upload de este paquete se realiza mediante Hatchling siguiendo el [tutorial de python](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

para pruebas

```bash
$ python3 -m pip install -e .
```


esta librería recibe el nombre de aceti_maps

asegurarse de tener pip actualizado a la última versión
```bash
$ python3 -m pip install --upgrade pip
```
construir el repositorio
```bash
$ python3 -m build
```

subirlo al repositorio deseado
```bash
$ python3 -m twine upload --repository testpypi dist/*
$ python3 -m twine upload dist/*
```
el token lo tiene acasado4@us.es



instalar mediante
```bash
$ python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps aceti_maps
$ pip install aceti_maps
```

la guía de uso está disponible en [README_LEG](./README_LEG.md)
