# crudini_simple

使用python实现一个工具 curdini.py，实现对ini或conf文件的put、get、update、delete，使用argparse、configparser

类似项目：https://github.com/pixelb/crudini

## usage

```sh
crudini_simple set Database MaxConnections 100 example.ini
crudini_simple get Database host example.ini
crudini_simple update Server port 9090 example.ini
crudini_simple del Server port example.ini
crudini_simple del Server port ip example.ini
crudini_simple merge example2.ini example.ini
```
