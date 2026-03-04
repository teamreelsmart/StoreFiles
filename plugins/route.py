from aiohttp import web
import markdown
import os
from html import escape
from datetime import datetime

routes = web.RouteTableDef()
BOT_CLIENT = None


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    readme_path = os.path.join(project_root, "README.md")
    if not os.path.exists(readme_path):
        return web.Response(text="Bot is running", status=200)

    with open(readme_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    html = markdown.markdown(md_text, extensions=["fenced_code", "codehilite", "tables"])

    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Yugen FileStore - README</title>
        <style>
            body {{
                font-family: sans-serif;
                max-width: 900px;
                margin: auto;
                padding: 2rem;
                background: #f9f9f9;
                color: #333;
            }}
            pre {{
                background: #282c34;
                color: #f8f8f2;
                padding: 1em;
                overflow-x: auto;
                border-radius: 8px;
                font-size: 14px;
                line-height: 1.5;
                white-space: pre;
            }}
            code {{
                font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 0.5rem;
                text-align: left;
            }}
            h1, h2, h3 {{
                border-bottom: 1px solid #ddd;
                padding-bottom: 0.3em;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    return web.Response(text=html_page, content_type="text/html")


@routes.get("/verify/{token}", allow_head=True)
async def verify_route_handler(request):
    token = request.match_info.get("token", "").strip()
    if not token:
        return web.Response(text="Invalid verify link.", status=400)

    if BOT_CLIENT is None:
        return web.Response(text="Bot is not ready. Please try again.", status=503)

    data = await BOT_CLIENT.mongodb.get_verify_link(token)
    if not data:
        return web.Response(text="This verify link is invalid or expired.", status=404)

    if data.get("used"):
        return web.Response(text="This verify link has already been used.", status=410)

    if data.get("expires_at") and data["expires_at"] <= datetime.now():
        await BOT_CLIENT.mongodb.remove_verify_link(token)
        return web.Response(text="This verify link has expired.", status=410)

    delay = max(int(getattr(BOT_CLIENT, "verify_redirect_delay", 5)), 1)
    short_link = escape(data.get("short_link", ""))

    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verification Link Generator</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #0f172a;
                color: #e2e8f0;
                font-family: Arial, sans-serif;
            }}
            .card {{
                width: min(90vw, 520px);
                background: #1e293b;
                border-radius: 14px;
                padding: 28px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.35);
            }}
            h2 {{
                margin-top: 0;
                margin-bottom: 8px;
            }}
            .muted {{
                color: #94a3b8;
                margin-bottom: 22px;
            }}
            .timer {{
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 14px;
            }}
            .bar {{
                width: 100%;
                height: 10px;
                border-radius: 999px;
                background: #334155;
                overflow: hidden;
            }}
            .bar > span {{
                display: block;
                height: 100%;
                width: 0%;
                background: linear-gradient(90deg, #22d3ee, #38bdf8);
                transition: width 1s linear;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Your link is generating, please wait...</h2>
            <div class="muted">You will be redirected automatically.</div>
            <div class="timer"><span id="seconds">{delay}</span>s</div>
            <div class="bar"><span id="progress"></span></div>
        </div>
        <script>
            let seconds = {delay};
            const total = seconds;
            const secEl = document.getElementById('seconds');
            const progressEl = document.getElementById('progress');
            const t = setInterval(() => {{
                seconds -= 1;
                secEl.innerText = Math.max(seconds, 0);
                const done = ((total - Math.max(seconds, 0)) / total) * 100;
                progressEl.style.width = done + '%';
                if (seconds <= 0) {{
                    clearInterval(t);
                    window.location.href = "{short_link}";
                }}
            }}, 1000);
            progressEl.style.width = '0%';
        </script>
    </body>
    </html>
    """
    return web.Response(text=html_page, content_type="text/html")


@routes.get("/health", allow_head=True)
async def health_route_handler(request):
    return web.Response(text="ok", status=200)


app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, port=8080)
