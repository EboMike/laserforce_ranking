from sanic import Request
from sanic.exceptions import NotFound, ServerError, BadRequest

from shared import app
from utils import render_template
import traceback


@app.exception(NotFound)
async def notfound(request: Request, exception: Exception) -> str:
    description = exception.args[0] if exception.args else "The page you are looking for does not exist."

    return await render_template(request, "errors/404.html", description=description)


@app.exception(ServerError, Exception)
async def servererror(request: Request, exception: Exception) -> str:

    description = "The server encountered an internal error and was unable to complete your request.<br><br> Please contact the administrator if the problem persists."

    if app.debug:
        description = f"{description}<br><br>{traceback.format_exc()}"

    traceback.print_exc()

    return await render_template(request, "errors/500.html", description=description)


@app.exception(BadRequest)
async def badrequest(request: Request, exception: Exception) -> str:
    description = exception.args[0] if exception.args else "The server could not understand your request."

    return await render_template(request, "errors/400.html", description=description)
