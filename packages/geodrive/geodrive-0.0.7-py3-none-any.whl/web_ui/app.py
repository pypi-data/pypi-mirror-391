from pathlib import Path

from aiohttp import web

from geodrive.logging import get_logger


class WebApp:
    """

    """

    def __init__(self, video):
        self.logger = get_logger("web-app")
        self.app = web.Application()
        self.panel_file = 'control_panel.html'
        self.panel_dir = 'control_panel'
        if video:
            self.panel_file = 'video_control_panel.html'
            self.panel_dir = 'game'

        self.reg_routes()

    def reg_routes(self):
        self.app.router.add_get('/', self.control_panel)
        self.app.router.add_get('/favicon.ico', self.serve_favicon)
        self.app.router.add_get('/static/{source}/{filename}', self.serve_static)

    async def run(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        self.logger.info(f"Панель управления доступна по адресу: http://localhost:8080")


    async def control_panel(self, request):
        script_dir = Path(__file__).parent
        html_file = script_dir / self.panel_dir / self.panel_file
        if html_file.exists():
            try:
                html_content = html_file.read_text(encoding='utf-8')
            except Exception as e:
                return web.Response(
                text=f"<h1>{e}</h1>",
                content_type='text/html',
                status=404
            )
            return web.Response(text=html_content, content_type='text/html')
        else:
            return web.Response(
                text=f"<h1>Файл {self.panel_file} не найден</h1>",
                content_type='text/html',
                status=404
            )

    async def serve_static(self, request):
        source = request.match_info['source']
        if source == 'css':
            return await self.serve_css(request)
        elif source == 'js':
            return await self.serve_js(request)
        return web.Response(status=404)


    async def serve_css(self, request):
        filename = request.match_info['filename']
        script_dir = Path(__file__).parent
        static_file = script_dir / self.panel_dir / 'css' / filename

        if static_file.exists() and static_file.suffix == '.css':
            content_type = 'text/css'
            content = static_file.read_text(encoding='utf-8')
            return web.Response(text=content, content_type=content_type)

        return web.Response(status=404)

    async def serve_js(self, request):
        filename = request.match_info['filename']
        script_dir = Path(__file__).parent
        static_file = script_dir / self.panel_dir / 'js' / filename

        if static_file.exists() and static_file.suffix == '.js':
            content_type = 'application/javascript'
            content = static_file.read_text(encoding='utf-8')
            return web.Response(text=content, content_type=content_type)

        return web.Response(status=404)

    async def serve_favicon(self, request):
        """Обслуживание favicon.ico"""
        script_dir = Path(__file__).parent
        favicon_file = script_dir / 'favicon.ico'

        if favicon_file.exists():
            return web.FileResponse(favicon_file)
        else:
            return web.Response(status=404)
