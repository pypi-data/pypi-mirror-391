## 0.1.8
- New recommended import: `import dpgcontainers as dpgc`
- Added `classes` to all container classes
- Added `find_by_class` method to base container

```python
window = dpgc.Window()(
    dpgc.Text('value', classes=['findme'], tag='text_instance',
)

found: list[dpgc.DPGContainersBase] = window.find_by_class('textclass')
```

- Added `find_by_tag` method to base container

```python
found: dpgc.DPGContainersBase = window.find_by_tag('text_instance')
```

- Added a decorator for dpg, `wrap_dpg`, which wraps all dpg functions such
    that any instances of `DPGContainersBase` passed as arguments are
    automatically converted to their IDs.

```python
dpg = dpgc.wrap_dpg(dpg)

window = dpgc.Window().render()
dpg.bind_item_font(window, font)
```

- Bumped required python version to 3.13
