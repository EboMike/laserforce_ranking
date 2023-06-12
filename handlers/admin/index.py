from sanic import Request
from shared import app
from utils import render_template

@app.get("/admin")
async def admin_index(request: Request):
    return await render_template(request,
        "admin/index.html",
    )
