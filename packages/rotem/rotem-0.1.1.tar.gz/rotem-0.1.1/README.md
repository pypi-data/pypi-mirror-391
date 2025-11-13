# About Rotom

rotom is a simple tui library used to draw tilemap and some informations on terminal.

## Fast Usage

```python
from rotem import *

tilemap = Tilemap()       # default size is (5, 5)
print(tilemap)
```

this will output 

```
· · · · ·
· · · · ·
· · · · ·
· · · · ·
· · · · ·
```
and you can set character for each point

```python
tilemap = Tilemap()
tilemap.set_char(0, 0, '@')
print(tilemap)
```
and you will get something like below:

```
@ · · · · 
· · · · · 
· · · · · 
· · · · · 
· · · · · 
```

you can set color, background color, bold and underline to style the char like this:

```python
tilemap = Tilemap(10, 10)
tilemap.set_char(0, 0, '@', color="#942c4b", bold=True, underline=True)
print(tilemap)
```

you will get something like this (the result in markdown file should be the same because this only work in terminal):
```
@ · · · ·
· · · · ·
· · · · ·
· · · · ·
· · · · ·
```

and you can add a border for it 

```python
tilemap = Tilemap(5, 5)
print(add_border(tilemap()))
```

you will get something like this:

```
┌───────────┐
│ · · · · · │
│ · · · · · │
│ · · · · · │
│ · · · · · │
│ · · · · · │
└───────────┘
```

except the game map, rotom provide tool to render informations. 

```python
tilemap = Tilemap(8, 8)
tilemap.set_char(5, 5, '@')

infos = InfoBoard()
infos.set_info("title", "content")

result = horizontal_combine(tilemap(), infos(), sep='   ')
print(result)
```

this will output:

```
· · · · · · · ·   +--------------------------------+
· · · · · · · ·   | title: content                 |
· · · · · · · ·   +--------------------------------+
· · · · · · · ·   
· · · · · · · ·   
· · · · · @ · ·   
· · · · · · · ·   
· · · · · · · ·   
```

I use `horizontal_combine` to combine two string, but also can be combined as vertical.

```python
result = vertical_combine(tilemap(), infos(), sep='/')
print(result)
```

```
· · · · · · · ·
· · · · · · · ·
· · · · · · · ·
· · · · · · · ·
· · · · · · · ·
· · · · · @ · ·
· · · · · · · ·
· · · · · · · ·
//////////////////////////////////
+--------------------------------+
| title: content                 |
+--------------------------------+
```