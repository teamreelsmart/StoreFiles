from aiohttp import web
from html import escape
from datetime import datetime, timedelta, timezone

routes = web.RouteTableDef()
BOT_CLIENT = None


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    html_page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Snap Lover • Premium File Hub</title>
        <style>
            :root {
                --bg:#070b14;
                --card:#111827;
                --muted:#9ca3af;
                --text:#f8fafc;
                --accent:#22d3ee;
                --accent2:#38bdf8;
                --border:#1f2937;
            }
            * { box-sizing: border-box; }
            body {
                margin:0;
                font-family: Inter, Arial, sans-serif;
                background: radial-gradient(circle at top right, #0f172a 0%, var(--bg) 45%);
                color:var(--text);
            }
            .container { width:min(1100px, 92vw); margin:0 auto; }
            .nav {
                position: sticky; top:0; z-index:5;
                background: rgba(7,11,20,.85); backdrop-filter: blur(10px);
                border-bottom:1px solid var(--border);
            }
            .nav-inner { display:flex; align-items:center; justify-content:space-between; padding:14px 0; }
            .brand { font-weight:800; letter-spacing:.3px; }
            .btn {
                display:inline-block; text-decoration:none; color:#001018;
                background: linear-gradient(90deg, var(--accent), var(--accent2));
                padding:10px 16px; border-radius:10px; font-weight:700;
            }
            .hero { padding:70px 0 48px; display:grid; grid-template-columns:1.2fr .8fr; gap:24px; }
            .card {
                background: linear-gradient(180deg, rgba(17,24,39,.95), rgba(17,24,39,.75));
                border:1px solid var(--border); border-radius:16px; padding:20px;
            }
            .headline { font-size: clamp(32px,5vw,54px); margin:0 0 12px; line-height:1.05; }
            .sub { color:var(--muted); font-size:16px; line-height:1.6; margin-bottom:22px; }
            .chips { display:flex; flex-wrap:wrap; gap:10px; }
            .chip { font-size:12px; border:1px solid #334155; padding:7px 10px; border-radius:999px; color:#cbd5e1; }
            .stats { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:12px; }
            .stat { background:#0b1220; border:1px solid #1e293b; border-radius:10px; padding:12px; }
            .stat b { font-size:20px; }
            h2.section-title { margin:0 0 16px; font-size:24px; }
            .grid-3 { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
            .feature p { color:var(--muted); margin:8px 0 0; line-height:1.55; }
            .faq details { border:1px solid var(--border); border-radius:10px; padding:12px 14px; margin-bottom:10px; }
            .faq summary { cursor:pointer; font-weight:700; }
            .faq p { color:var(--muted); margin:10px 0 0; }
            footer { color:#94a3b8; border-top:1px solid var(--border); margin-top:36px; padding:16px 0 28px; text-align:center; }
            @media (max-width: 900px){
                .hero { grid-template-columns:1fr; }
                .grid-3 { grid-template-columns:1fr; }
            }
        </style>
    </head>
    <body>
        <div class="nav">
            <div class="container nav-inner">
                <div class="brand">⚡ Snap Lover Service</div>
                <a class="btn" href="https://t.me/SnapLoverXBot">Open Bot</a>
            </div>
        </div>

        <main class="container">
            <section class="hero">
                <div>
                    <h1 class="headline">Snap Lover • Fast File Access & Smart Verification</h1>
                    <p class="sub">Welcome to the official Snap Lover service page. Generate secure links, verify quickly, and access content with better anti-abuse protection and modern channel workflows.</p>
                    <div class="chips">
                        <span class="chip">Secure Verify Flow</span>
                        <span class="chip">One-Time Links</span>
                        <span class="chip">Auto-Expiring Invites</span>
                        <span class="chip">Admin Controls</span>
                    </div>
                </div>
                <div class="card">
                    <h2 style="margin-top:0">Official Channels</h2>
                    <p class="sub" style="margin-bottom:12px">Join updates, support, and latest drops.</p>
                    <p><a class="btn" style="width:100%; text-align:center; margin-bottom:10px;" href="https://t.me/tunebots">Join @tunebots</a></p>
                    <p><a class="btn" style="width:100%; text-align:center;" href="https://t.me/Snap_Lover8">Join @Snap_Lover8</a></p>
                    <div class="stats">
                        <div class="stat"><div>Uptime</div><b>24x7</b></div>
                        <div class="stat"><div>Invite TTL</div><b>15m</b></div>
                        <div class="stat"><div>Verify Delay</div><b>5s</b></div>
                        <div class="stat"><div>Mode</div><b>Protected</b></div>
                    </div>
                </div>
            </section>

            <section class="card" style="margin-bottom:18px;">
                <h2 class="section-title">Why Snap Lover?</h2>
                <div class="grid-3">
                    <article class="feature card" style="padding:16px;">
                        <h3 style="margin:0">🔒 Safer Links</h3>
                        <p>Verification tokens are controlled and validated before redirect, preventing direct abuse and improving trust.</p>
                    </article>
                    <article class="feature card" style="padding:16px;">
                        <h3 style="margin:0">⚙️ Admin Friendly</h3>
                        <p>Admins can generate channel join links from forwarded posts and share them instantly with users.</p>
                    </article>
                    <article class="feature card" style="padding:16px;">
                        <h3 style="margin:0">🚀 Smooth Experience</h3>
                        <p>Clean, modern pages with timer and redirects provide fast onboarding and clear user flow.</p>
                    </article>
                </div>
            </section>

            <section class="card faq">
                <h2 class="section-title">Quick FAQ</h2>
                <details>
                    <summary>How do I get files?</summary>
                    <p>Start the bot, open your generated link, complete verification, and access your content directly.</p>
                </details>
                <details>
                    <summary>Why verification is required?</summary>
                    <p>Verification protects links from bypassing and helps keep the system stable for genuine users.</p>
                </details>
                <details>
                    <summary>Need support?</summary>
                    <p>Use our channels above or contact the bot admin team from official Telegram pages.</p>
                </details>
            </section>
        </main>

        <footer>
            © <span id="year"></span> Snap Lover • Powered by TuneBots
        </footer>

        <script>
            document.getElementById('year').textContent = new Date().getFullYear();
        </script>
    </body>
    </html>
    """
    return web.Response(text=html_page, content_type="text/html")


@routes.get("/mini", allow_head=True)
@routes.get("/mini/", allow_head=True)
async def mini_entry_handler(request):
    user_id = (request.query.get("user_id") or "").strip()
    if user_id and user_id.lstrip('-').isdigit():
        raise web.HTTPFound(f"/mini/{user_id}")

    html_page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mini App Loader</title>
        <style>
            body { margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center; background:#0b1220; color:#e5e7eb; font-family:Arial,sans-serif; }
            .card { width:min(92vw,560px); background:#111827; border:1px solid #1f2937; border-radius:14px; padding:22px; text-align:center; }
            .btn { display:inline-block; margin-top:14px; text-decoration:none; color:#001018; background:linear-gradient(90deg,#22d3ee,#38bdf8); padding:10px 14px; border-radius:10px; font-weight:700; }
            .muted { color:#9ca3af; font-size:14px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2 style="margin:0 0 10px;">Opening Mini App...</h2>
            <p class="muted">If this page doesn't auto-open your profile, tap the button below.</p>
            <a id="open" class="btn" href="#">Open My Profile</a>
        </div>

        <script>
            const q = new URLSearchParams(window.location.search);
            let uid = q.get('user_id');

            if (!uid && window.Telegram && Telegram.WebApp && Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user) {
                uid = Telegram.WebApp.initDataUnsafe.user.id;
            }

            const openBtn = document.getElementById('open');
            if (uid) {
                const target = `/mini/${uid}`;
                openBtn.href = target;
                window.location.replace(target);
            } else {
                openBtn.textContent = 'Open Mini with user_id';
                openBtn.href = '/mini/123456?user_id=123456';
            }
        </script>
    </body>
    </html>
    """
    return web.Response(text=html_page, content_type="text/html")


@routes.get("/mini/{user_id}", allow_head=True)
async def mini_profile_handler(request):
    user_id_raw = request.match_info.get("user_id", "").strip()
    if not user_id_raw.lstrip('-').isdigit():
        return web.Response(text="Invalid user id", status=400)

    user_id = int(user_id_raw)
    if BOT_CLIENT is None:
        return web.Response(text="Bot is not ready. Please try again.", status=503)

    try:
        user = await BOT_CLIENT.get_users(user_id)
    except Exception:
        return web.Response(text="User not found", status=404)

    username = f"@{user.username}" if getattr(user, 'username', None) else "N/A"
    full_name = (f"{user.first_name or ''} {user.last_name or ''}").strip() or "Unknown"

    created_at = await BOT_CLIENT.mongodb.get_user_created_at(user_id)
    ist = timezone(timedelta(hours=5, minutes=30))
    if created_at is None:
        started_ist = "Not Available"
    else:
        started_ist = created_at.replace(tzinfo=timezone.utc).astimezone(ist).strftime("%d-%m-%Y %I:%M:%S %p IST")

    links_generated = await BOT_CLIENT.mongodb.get_links_generated(user_id)

    default_dp = BOT_CLIENT.messages.get("DEFAULT_PROFILE_PIC", "https://telegra.ph/file/7a16ef7abae23bd238c82-b8fbdcb05422d71974.jpg")
    if getattr(user, 'username', None):
        profile_pic = f"https://t.me/i/userpic/320/{user.username}.jpg"
    else:
        profile_pic = default_dp

    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mini App • User Profile</title>
        <style>
            body {{margin:0; font-family:Arial,sans-serif; background:#0b1220; color:#e5e7eb;}}
            .wrap {{width:min(900px,92vw); margin:24px auto;}}
            .card {{background:#111827; border:1px solid #1f2937; border-radius:16px; padding:20px;}}
            .head {{display:flex; gap:18px; align-items:center; flex-wrap:wrap;}}
            .avatar {{width:110px; height:110px; border-radius:50%; object-fit:cover; border:3px solid #22d3ee;}}
            .grid {{display:grid; grid-template-columns:repeat(2,1fr); gap:12px; margin-top:16px;}}
            .item {{background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:12px;}}
            .label {{color:#9ca3af; font-size:12px;}}
            .value {{font-weight:700; margin-top:4px;}}
            .btns {{display:flex; gap:10px; flex-wrap:wrap; margin-top:18px;}}
            .btn {{text-decoration:none; color:#001018; background:linear-gradient(90deg,#22d3ee,#38bdf8); padding:10px 14px; border-radius:10px; font-weight:700;}}
            @media(max-width:700px){{ .grid{{grid-template-columns:1fr;}} }}
        </style>
    </head>
    <body>
        <div class="wrap">
            <div class="card">
                <div class="head">
                    <img src="{escape(profile_pic)}" class="avatar" alt="profile" onerror="this.src='{escape(default_dp)}'" />
                    <div>
                        <h2 style="margin:0 0 8px;">Mini App Profile</h2>
                        <div style="color:#93c5fd;">Welcome to TuneBots x Snap_Lover8</div>
                    </div>
                </div>

                <div class="grid">
                    <div class="item"><div class="label">User ID</div><div class="value">{user_id}</div></div>
                    <div class="item"><div class="label">Username</div><div class="value">{escape(username)}</div></div>
                    <div class="item"><div class="label">Name</div><div class="value">{escape(full_name)}</div></div>
                    <div class="item"><div class="label">First Start (IST)</div><div class="value">{escape(started_ist)}</div></div>
                    <div class="item"><div class="label">Links Generated</div><div class="value">{links_generated}</div></div>
                    <div class="item"><div class="label">Status</div><div class="value">Active</div></div>
                </div>

                <div class="btns">
                    <a class="btn" href="https://t.me/tunebots">Join TuneBots</a>
                    <a class="btn" href="https://t.me/Snap_Lover8">Join Snap_Lover8</a>
                    <a class="btn" href="https://t.me/SnapLoverXBot?start=premium">Buy Premium</a>
                </div>
            </div>
        </div>
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

            <div style="margin-bottom:16px; padding:12px; border-radius:10px; background:#0b1220; border:1px solid #334155;">
                <div style="font-weight:700; margin-bottom:8px;">Official Channels</div>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <a href="https://t.me/tunebots" style="text-decoration:none; color:#0f172a; background:#22d3ee; padding:8px 12px; border-radius:999px; font-weight:700;">TuneBots</a>
                    <a href="https://t.me/Snap_Lover8" style="text-decoration:none; color:#0f172a; background:#38bdf8; padding:8px 12px; border-radius:999px; font-weight:700;">Snap_Lover8</a>
                </div>
            </div>

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
