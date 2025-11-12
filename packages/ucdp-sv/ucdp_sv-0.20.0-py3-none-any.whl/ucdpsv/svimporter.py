#
# MIT License
#
# Copyright (c) 2025 nbiotcloud
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""SystemVerilog Importer."""

import re
from pathlib import Path
from typing import Any, TypeAlias

import hdl_parser as hdl
import ucdp as u
from matchor import matchsp

Attrs: TypeAlias = dict[str, dict[str, Any]]

_RE_WIDTH = re.compile(r"\[([^\:]+?)(\-1)?\:([^\]+])\]")
DIRMAP = {
    "input": u.IN,
    "output": u.OUT,
    "inout": u.INOUT,
}


def import_params_ports(
    mod: u.BaseMod,
    filelistname: str = "hdl",
    paramattrs: Attrs | None = None,
    portattrs: Attrs | None = None,
) -> None:
    """Import Parameter and Ports."""
    importer = SvImporter()
    if paramattrs:
        importer.paramattrs.update(paramattrs)
    if portattrs:
        importer.portattrs.update(portattrs)
    importer.import_params_ports(mod, filelistname=filelistname)


class SvImporter(u.Object):
    """Importer."""

    paramattrs: Attrs = u.Field(default_factory=dict)
    portattrs: Attrs = u.Field(default_factory=dict)

    def import_params_ports(self, mod: u.BaseMod, filelistname: str = "hdl", filepath: Path | None = None) -> None:
        """Import Parameter and Ports."""
        filepath = filepath or _find_filepath(mod, filelistname)
        file = hdl.parse_file(filepath)
        for module in file.modules:
            if module.name == mod.modname:
                self._import_params(mod, module.params)
                self._import_ports(mod, module.ports)
                break
        else:
            raise ValueError(f"{filepath} does not contain module {mod.modname}")

    def _import_params(self, mod: u.BaseMod, params: tuple[hdl.Param, ...]) -> None:
        paramdict = {param.name: param for param in params}
        while paramdict:
            # first element
            param = paramdict.get(next(iter(paramdict.keys())))
            name = param.name
            # determine attrs
            attrs = dict(_get_attrs(self.paramattrs, param.name))
            # determine type_
            type_ = attrs.pop("type_", None)
            if type_:
                type_, name, _ = _resolve_type(type_, param.name, paramdict)
            else:
                type_ = _get_type(mod.params, param.ptype or "integer", param.dim, param.dim_unpacked)
                if param.default:
                    type_ = type_.new(default=int(param.default))  # TODO: add parser
                paramdict.pop(name)
            if param.ifdefs:
                attrs.setdefault("ifdef", param.ifdefs[0])
            mod.add_param(type_, name, **attrs)

    def _import_ports(self, mod: u.BaseMod, ports: tuple[hdl.Port, ...]) -> None:
        portdict = {port.name: port for port in ports}
        while portdict:
            # first element
            port = portdict.get(next(iter(portdict.keys())))
            name = port.name
            # determine attrs
            attrs = dict(_get_attrs(self.portattrs, port.name))
            # determine type_
            type_ = attrs.pop("type_", None)
            direction = attrs.pop("direction", DIRMAP[port.direction])
            if type_:
                type_, name, direction = _resolve_type(type_, port.name, portdict, direction=direction)
            else:
                type_ = _get_type(mod.params, port.ptype, port.dim, port.dim_unpacked)
                portdict.pop(name)
            if port.ifdefs:
                attrs.setdefault("ifdef", port.ifdefs[0])
            mod.add_port(type_, name, direction=direction, **attrs)


def _find_filepath(mod: u.BaseMod, filelistname: str) -> Path:
    modfilelist = u.resolve_modfilelist(mod, filelistname, replace_envvars=True)
    if not modfilelist:
        raise ValueError(f"No filelist {filelistname!r} found.")

    try:
        return modfilelist.filepaths[0]
    except IndexError:
        raise ValueError(f"Filelist {filelistname!r} has empty 'filepaths'.") from None


def _get_attrs(attrs: Attrs, name: str) -> dict[str, Any]:
    try:
        return attrs[name]
    except KeyError:
        pass
    key = matchsp(name, attrs)
    if key:
        return attrs[key]
    return {}


def _svfilter(ident: u.Ident) -> bool:
    return not isinstance(ident.type_, u.BaseStructType)


def _resolve_type(type_: u.BaseType, name: str, itemdict: dict[str, Any], direction: u.Direction | None = None) -> None:
    if isinstance(type_, u.BaseStructType):
        if direction is None:
            idents = (u.Param(type_, "n"),)
        else:
            idents = (
                u.Port(type_, "n_i", direction=u.IN),
                u.Port(type_, "n_o", direction=u.OUT),
                u.Port(type_, "n", direction=u.IN),
                u.Port(type_, "n", direction=u.OUT),
            )
        for ident in idents:
            # try to find ident which matches `name`
            submap = {sub.name.removeprefix("n"): sub for sub in ident.iter(filter_=_svfilter)}
            for ending, subident in submap.items():
                if name.endswith(ending) and subident.direction == direction:
                    ident = ident.new(name=f"{name.removesuffix(ending)}{ident.suffix}")  # noqa: PLW2901
                    break
            else:
                continue
            # ensure all struct members have their friend
            subs = tuple(ident.iter(filter_=_svfilter))
            if not all(sub.name in itemdict for sub in subs):
                continue
            # strip
            for sub in subs:
                itemdict.pop(sub.name)
            return ident.type_, ident.name, ident.direction

    itemdict.pop(name)
    return type_, name, direction


def _get_type(namespace: u.Namespace, ptype: str, dim: str, dim_unpacked: str) -> u.BaseType:
    """Determine UCDP Type."""
    if not ptype:
        type_ = u.BitType()
    elif ptype == "integer":
        assert not dim, dim
        assert not dim, dim
        type_ = u.IntegerType()
    elif ptype in ("logic", "wire", "reg"):
        if dim:
            width, right = _get_width(namespace, dim)
            return u.UintType(right=right, width=width)
        return u.BitType()
    else:
        raise ValueError(f"Unknown Type {ptype=} {dim=} {dim_unpacked=}")
    assert not dim_unpacked, f"TODO: {dim_unpacked=}"
    return type_


def _get_width(namespace: u.Namespace, width: str) -> tuple[str, str]:
    m = _RE_WIDTH.match(width)
    if not m:
        raise ValueError(f"Unknown width {width}")
    left, m1, right = m.groups((1, 2))
    # Try to convert string to integer or find symbol in namespace
    try:
        right = int(right)
    except ValueError:
        right = namespace[right]
    # Try to convert string to integer or find symbol in namespace
    try:
        width = int(left)
        if m1:
            width = width + 1
    except ValueError:
        width = namespace[left]
        if m1 and right:
            width = width + 1

    return width, right
