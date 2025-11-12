from __future__ import annotations

import abc
from collections.abc import Callable
import contextlib
import functools
import re
import types
from typing import ClassVar

import dearpygui.dearpygui as dpg  # type: ignore
from dpgmagictag.magictag import MagicTag  # type: ignore

from dpgcontainers import exceptions


def dpg_function_decorator(func: types.FunctionType):
    '''Decorator for dearpygui.dearpygui functions
    Any args or kwargs whose values are DPGContainersBase instances are
    converted to instance.id_, as dearpygui expects.
    '''
    @functools.wraps(func)
    def _inner(*args, **kwargs):
        inner_args = [
            arg.id_ if (hasattr(arg, '__class__') and isinstance(arg, DPGContainersBase)) else arg
            for arg in args
        ]
        inner_kwargs = {
            key: value.id_ if isinstance(value, DPGContainersBase) else value
            for key, value in kwargs.items()
        }
        return func(*inner_args, **inner_kwargs)

    return _inner


def wrap_dpg(dpg: types.ModuleType):
    '''Iterate through properties of the dearpygui module and decorate any functions
    with dpg_function_decorator.
    '''
    for name in dir(dpg):
        thing = getattr(dpg, name)
        if isinstance(thing, types.FunctionType):
            if thing.__module__ == 'dearpygui.dearpygui':
                setattr(dpg, name, dpg_function_decorator(thing))
    return dpg



# Make dpg play nice with containers
dpg = wrap_dpg(dpg)


CONFIGURE_ITEM_KEYS = (
    'callback', 'drag_callback', 'drop_callback', 'enabled', 'filter_key',
    'height', 'indent', 'label', 'payload_type', 'show', 'source',
    'track_offset', 'tracked', 'use_internal_label', 'user_data', 'width',
)


def is_rendered(instance: 'DPGContainersBase'):
    '''Simple check that an instance of DPGContainersBase has been rendered'''
    return hasattr(instance, 'id_')


def assert_rendered(method) -> Callable:
    '''Decorator to assert that an instance has been rendered before calling
    the wrapped method.'''
    @functools.wraps(method)
    def _inner(*args, **kwargs):
        if not is_rendered(args[0]):
            raise exceptions.UnrenderedException()
        return method(*args, **kwargs)
    return _inner


''' Bind functions
bind_colormap(item, source)

bind_font(font)
bind_item_font(item, font)

bind_item_handler_registry(item, handler_registry)

bind_item_theme(item, theme)
bind_theme(theme)
'''



class DPGContainersBase(abc.ABC):
    dpg_function_name: ClassVar[str]
    dpg_arguments: ClassVar[tuple[str, ...]]
    dpg_function_cache: ClassVar[Callable | None] = None
    dpg_value_cast: ClassVar[type | None] = None
    rendered_by_id: ClassVar[dict[int, 'DPGContainersBase']] = dict()
    dpg_bind_function_name: ClassVar[str | None] = None
    dpg_bind_function_cache: ClassVar[Callable | None] = None
    dpg_bind_item_function_name: ClassVar[str | None] = None
    dpg_bind_item_function_cache: ClassVar[Callable | None] = None

    classes: list[str]


    @property
    def dpg_function(self):
        if self.dpg_function_cache is None:
            self.dpg_function_cache = getattr(dpg, self.dpg_function_name)
        return self.dpg_function_cache

    @property
    def dpg_bind_function(self):
        if self.dpg_bind_function_cache is None:
            if self.dpg_bind_function_name is None:
                raise exceptions.UnbindableException()
            self.dpg_bind_function_cache = getattr(dpg, self.dpg_bind_function_name)
        return self.dpg_bind_function_cache

    @property
    def dpg_bind_item_function(self):
        if self.dpg_bind_item_function_cache is None:
            if self.dpg_bind_item_function_name is None:
                raise exceptions.UnbindableException()
            self.dpg_bind_item_function_cache = getattr(dpg, self.dpg_bind_item_function_name)
        return self.dpg_bind_item_function_cache

    @property
    def children(self) -> list['DPGContainersBase']:
        if not hasattr(self, '_children'):
            self._children: list['DPGContainersBase'] = []
        return list(self._children)

    @children.setter
    def children(self, value: list['DPGContainersBase']):
        self._children = value

    @property
    def parent(self) -> 'DPGContainersBase'|None:
        if not hasattr(self, '_parent'):
            self._parent: 'DPGContainersBase'|None = None
        return self._parent

    @parent.setter
    def parent(self, value: 'DPGContainersBase'):
        self._parent = value

    @property
    def tagged_entities(self) -> dict[str, 'DPGContainersBase']:
        if not hasattr(self, '_tagged_entities'):
            self._tagged_entities: dict[str, 'DPGContainersBase'] = {}
            if hasattr(self, 'tag') and self.tag:
                self._tagged_entities[self.tag] = self
        return self._tagged_entities

    @property
    def named_child_indexes(self) -> dict[str, int]:
        if not hasattr(self, '_named_child_indexes'):
            self._named_child_indexes: dict[str, int] = {}
        return self._named_child_indexes

    def find_all(self, name: str) -> list['DPGContainersBase']:
        found = []
        if name in self.named_child_indexes:
            index = self.named_child_indexes[name]
            found.append(self.children[index])
        for child in self.children:
            try:
                named = child.find_all(name)
            except exceptions.NamedChildNotFound:
                pass
            else:
                found.extend(named)
        if found:
            return found
        raise exceptions.NamedChildNotFound(name)

    def find(self, name: str) -> 'DPGContainersBase':
        if name in self.named_child_indexes:
            index = self.named_child_indexes[name]
            return self.children[index]
        for child in self.children:
            try:
                named = child.find(name)
            except exceptions.NamedChildNotFound:
                pass
            else:
                return named
        raise exceptions.NamedChildNotFound(name)

    def find_by_class(self, class_: str) -> list['DPGContainersBase']:
        results = []
        if class_ in self.classes:
            results.append(self)
        for child in self.children:
            results.extend(child.find_by_class(class_))
        return results

    def find_by_tag(self, tag: str) -> 'DPGContainersBase':
        if hasattr(self, 'tag') and self.tag == tag:
            return self
        for child in self.children:
            try:
                return child.find_by_tag(tag)
            except exceptions.TaggedNotFound:
                pass
        raise exceptions.TaggedNotFound(tag)

    def search(self, pattern: str) -> 'DPGContainersBase':
        matcher = re.compile(pattern)
        for name in self.named_child_indexes:
            if matcher.search(name):
                index = self.named_child_indexes[name]
                return self.children[index]
        for child in self.children:
            try:
                found = child.search(pattern)
            except exceptions.NamedChildNotFound:
                pass
            else:
                return found
        raise exceptions.NamedChildNotFound(pattern)

    def search_all(self, pattern: str) -> list['DPGContainersBase']:
        results = []
        matcher = re.compile(pattern)
        for name in self.named_child_indexes:
            if matcher.search(name):
                index = self.named_child_indexes[name]
                results.append(self.children[index])
        for child in self.children:
            found = child.search_all(pattern)
            results.extend(found)
        return results

    def search_named_children(self, name: str) -> 'DPGContainersBase':
        '''Deprecated'''
        return self.find(name)


    def __call__(self, *children: 'DPGContainersBase', **named_children: 'DPGContainersBase'):
        for child in children:
            self.add_child(child)

        for name, child in named_children.items():
            self.add_child(child, name=name)

        return self

    def render(self, parent: int|str|'DPGContainersBase'|None = None, tag_prefix: MagicTag | None = None):
        if not hasattr(self, 'id_'):
            dpg_kwargs = {
                arg: getattr(self, arg)
                for arg in self.dpg_arguments
            }
            if parent is None:
                parent = self.parent
            if parent is not None:
                if isinstance(parent, DPGContainersBase):
                    parent_id: int|str = parent.id_
                else:
                    parent_id = parent
                dpg_kwargs['parent'] = parent_id
            if tag_prefix is not None:
                if dpg_kwargs['tag'] != 0:
                    dpg_kwargs['tag'] = tag_prefix / dpg_kwargs['tag']
            id_ = self.dpg_function(**dpg_kwargs)

            # Hack for popups - There is only dpg.popup, not dpg.add_popup, so
            # we use the contextmanager as the dpg_function and enter it to
            # get the id
            if isinstance(id_, contextlib._GeneratorContextManager):
                with id_ as id_:
                    pass

            self.id_: int = id_
            self.rendered_by_id[id_] = self

        for child in self.children:
            child.render(tag_prefix=tag_prefix)

        if hasattr(self, 'post_render'):
            self.post_render()

        return self

    def remove_child(self, child: 'DPGContainersBase'):
        if child not in self.children:
            raise ValueError(f'{child} not in self.children')

        child_index = self._children.index(child)
        for name, index in list(self.named_child_indexes.items()):
            if child_index == index:
                del self.named_child_indexes[name]
            elif index > child_index:
                self.named_child_indexes[name] -= 1

        del self._children[child_index]

    def add_child(
        self,
        child: 'DPGContainersBase',
        prepend: bool=False,
        before: 'DPGContainersBase'|None = None,
        after: 'DPGContainersBase'|None = None,
        name: str|None = None
    ) -> 'DPGContainersBase':
        children = self.children
        index = len(children)
        if prepend:
            index = 0
        elif before is not None:
            index = children.index(before)
        elif after is not None:
            index = children.index(after) + 1

        children.insert(index, child)
        for named_name, named_index in list(self.named_child_indexes.items()):
            if named_index >= index:
                self.named_child_indexes[named_name] += 1
        if name:
            self.named_child_indexes[name] = index

        self.children = children
        child.parent = self
        return self

    def move(
            self,
            parent: 'DPGContainersBase',
            prepend: bool = False,
            before: 'DPGContainersBase'|None = None,
    ):
        # assert is_rendered(parent), 'Parent must be rendered'
        if self.parent is not None:
            self.parent.remove_child(self)

        parent.add_child(self, prepend=prepend, before=before)
        if prepend:
            assert before is None, 'prepend and before are mutually exclusive'
            children = dpg.get_item_children(parent.id_, 1)
            if children:
                before = self.rendered_by_id[children[0]]

        if is_rendered(self):
            if before is not None:
                dpg.move_item(self.id_, parent=parent.id_, before=before.id_)
            else:
                dpg.move_item(self.id_, parent=parent.id_)


    @assert_rendered
    def delete(self):
        if self.parent is not None:
            self.parent.remove_child(self)
        dpg.delete_item(self.id_)
        del self.rendered_by_id[self.id_]
        del self.id_

    @assert_rendered
    def clear(self):
        for child in self.children:
            child.delete()

    @property
    @assert_rendered
    def configuration(self):
        return dpg.get_item_configuration(self.id_)

    @property
    def value(self):
        return dpg.get_value(self.id_)

    @value.setter
    def value(self, value):
        if self.dpg_value_cast is not None:
            value = self.dpg_value_cast(value)
        dpg.set_value(self.id_, value)

    @assert_rendered
    def set_value(self, value):
        self.value = value

    @assert_rendered
    def configure(self, **kwargs):
        dpg.configure_item(self.id_, **kwargs)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if is_rendered(self):
            if key in CONFIGURE_ITEM_KEYS:
                kwargs = {key: value}
                dpg.configure_item(self.id_, **kwargs)

    @assert_rendered
    def bind(self, item: 'DPGContainersBase' | int | str | None = None):
        if item is None:
            self.dpg_bind_function(self)
        else:
            self.dpg_bind_item_function(item, self)
        return self

    @assert_rendered
    def __enter__(self):
        dpg.push_container_stack(self.id_)

    def __exit__(self, exc_type, exc_value, traceback):
        dpg.pop_container_stack()
