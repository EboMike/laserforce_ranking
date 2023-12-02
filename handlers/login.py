from sanic import Request, exceptions, response
from shared import app
from utils import render_template
from db.models import Player
from sanic.log import logger

@app.get("/login")
async def login(request: Request) -> str:
    logger.info("Loading login page, rendering template")

    return await render_template(request, "login.html")

@app.post("/login")
async def login_post(request: Request) -> str:
    logger.info("Logging in user")

    codename = request.form.get("codename")
    password = request.form.get("password")

    logger.debug(f"Logging in user {codename}")

    if not codename or not password:
        # TODO: better error message
        raise exceptions.BadRequest("Missing codename or password")
    
    logger.debug("Checking if user exists")
    
    player = await Player.filter(codename=codename).first()

    if not player:
        raise exceptions.BadRequest("Invalid codename or password")
    
    if not player.check_password(password):
        raise exceptions.BadRequest("Invalid codename or password")
    
    logger.debug("Logging in user")
    
    request.ctx.session["codename"] = player.codename
    request.ctx.session["player_id"] = player.player_id
    request.ctx.session["permissions"] = player.permissions

    logger.debug("Redirecting to previous page")

    # redirect to previous page
    return response.redirect(request.ctx.session.get("previous_page", "/"))