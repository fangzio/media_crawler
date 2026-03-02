# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/xhs/auth_http.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#
# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

from __future__ import annotations

import asyncio
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from tools import utils


class XhsAuthHttpServer:
    def __init__(self, crawler: "XiaoHongShuCrawler") -> None:
        self.crawler = crawler
        self.app = FastAPI(
            title="MediaCrawler XHS Auth Server",
            description="Auth status and QR code for Xiaohongshu crawler",
            version="1.0.0",
        )
        self._server: Optional[uvicorn.Server] = None
        self._task: Optional[asyncio.Task] = None
        self._register_routes()

    def _register_routes(self) -> None:
        @self.app.get("/auth/status")
        async def auth_status():
            return await self.crawler.get_login_status()

        @self.app.get("/auth/qrcode")
        async def auth_qrcode():
            qrcode = await self.crawler.get_login_qrcode()
            if not qrcode:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "message": "qrcode not found"},
                )
            return {"success": True, "qrcode": qrcode}

        @self.app.post("/auth/expire")
        async def auth_expire(force_captcha: bool = True):
            await self.crawler.expire_login(force_captcha=force_captcha)
            return {"success": True, "message": "cookies cleared"}

        @self.app.get("/health")
        async def health():
            return {"status": "ok"}

    async def start(self, host: str, port: int) -> None:
        if self._task and not self._task.done():
            return
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level="warning",
            loop="asyncio",
            lifespan="off",
        )
        self._server = uvicorn.Server(config)
        self._task = asyncio.create_task(self._server.serve())
        utils.logger.info(f"[XhsAuthHttpServer] Started at http://{host}:{port}")

    async def stop(self) -> None:
        if self._server:
            self._server.should_exit = True
        if self._task:
            try:
                await self._task
            except Exception:
                pass
            self._task = None
