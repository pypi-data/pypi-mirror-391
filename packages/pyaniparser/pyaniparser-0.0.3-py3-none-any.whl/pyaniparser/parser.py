from __future__ import annotations

import ctypes
import json
import os
import platform
import sys
from typing import Iterable, Iterator, Optional

from .types import ParseResult, from_json


def _default_libname() -> str :
    system = sys.platform
    arch = platform.machine().lower()

    # 归一化架构名
    if arch in ("x86_64", "amd64") :
        arch = "amd64"
    elif arch in ("arm64", "aarch64") :
        arch = "arm64"
    else :
        raise RuntimeError(f"Unsupported architecture: {arch}")

    if system.startswith("win") :
        filename = f"Banned.AniParser.Native-windows-{arch}.dll"
    elif system == "darwin" :
        filename = f"Banned.AniParser.Native-macos-{arch}.dylib"
    elif system.startswith("linux") :
        filename = f"Banned.AniParser.Native-linux-{arch}.so"
    else :
        raise RuntimeError(f"Unsupported platform: {system}")

    # 拼出完整路径 (lib 目录)
    return os.path.join(os.path.dirname(__file__), "lib", filename)


_GLOBALIZATION = {
    "Simplified"  : 1,  # 简体
    "Traditional" : 2,  # 繁体
    "NotChange"   : 0,  # 不改变
}


class AniParser :
    """
    Native AOT (ctypes) 版本。
    接口与旧版保持一致：
      - parse(title: str) -> Optional[ParseResult]
      - parse_batch(titles: Iterable[str]) -> Iterator[ParseResult]
    """

    def __init__(self, globalization: str = "NotChange", libpath: str | None = None) -> None :
        if globalization not in _GLOBALIZATION :
            raise ValueError(f"Unsupported globalization: {globalization}")

        if libpath is None :
            libpath = os.path.join(os.path.dirname(__file__), _default_libname())

        self._lib = ctypes.CDLL(libpath)

        # 签名
        self._lib.Ani_Init.argtypes = [ctypes.c_int]
        self._lib.Ani_Init.restype = ctypes.c_void_p

        self._lib.Ani_Destroy.argtypes = [ctypes.c_void_p]
        self._lib.Ani_Destroy.restype = None

        self._lib.Ani_Parse.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self._lib.Ani_Parse.restype = ctypes.c_void_p

        self._lib.Ani_ParseBatch.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self._lib.Ani_ParseBatch.restype = ctypes.c_void_p

        self._lib.Ani_Free.argtypes = [ctypes.c_void_p]
        self._lib.Ani_Free.restype = None

        h = self._lib.Ani_Init(_GLOBALIZATION[globalization])
        if not h :
            raise RuntimeError("Ani_Init failed")
        self._handle = ctypes.c_void_p(h)
        self._closed = False

    def close(self) -> None :
        if not self._closed :
            try :
                self._lib.Ani_Destroy(self._handle)
            finally :
                self._closed = True

    def __del__(self) -> None :
        try :
            self.close()
        except Exception :
            pass

    def parse(self, title: str) -> Optional[ParseResult] :
        if self._closed :
            raise RuntimeError("AniParser already closed")

        ptr = self._lib.Ani_Parse(self._handle, title.encode("utf-8"))
        if not ptr :
            return None
        try :
            s = ctypes.string_at(ptr).decode("utf-8")
        finally :
            self._lib.Ani_Free(ptr)

        obj = json.loads(s)
        return from_json(obj) if obj is not None else None

    def parse_batch(self, titles: Iterable[str]) -> Iterator[ParseResult] :
        if self._closed :
            raise RuntimeError("AniParser already closed")

        payload = json.dumps(list(titles), ensure_ascii = False).encode("utf-8")
        ptr = self._lib.Ani_ParseBatch(self._handle, payload)
        if not ptr :
            return
        try :
            s = ctypes.string_at(ptr).decode("utf-8")
        finally :
            self._lib.Ani_Free(ptr)

        arr = json.loads(s) or []
        for item in arr :
            yield from_json(item)

    # 旧接口里有这个方法；如果 AOT 未导出，可选择去掉或抛异常
    def get_translation_parser_list(self) -> list[str] :
        raise NotImplementedError("Not available in Native AOT build.")
