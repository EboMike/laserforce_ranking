from helpers.statshelper import barplot, img_to_b64
from helpers import gamehelper, userhelper
from utils import render_template
from objects import GameType, Team
from shared import routes
from aiohttp import web

@routes.get("/admin")
async def admin(request: web.Request):
    total_players = await userhelper.get_total_players()
    total_games = await gamehelper.get_total_games()
    total_games_played = await gamehelper.get_total_games_played()
    
    role_plot = await userhelper.get_avg_role_score_plot()

    return await render_template(
        request,
        "admin/admin.html",
        total_players=total_players,
        total_games=total_games,
        total_games_played=total_games_played,
        sm5_red_wins=await gamehelper.get_wins(GameType.SM5, Team.RED),
        sm5_green_wins=await gamehelper.get_wins(GameType.SM5, Team.GREEN),
        laserball_red_wins=await gamehelper.get_wins(GameType.LASERBALL, Team.RED),
        laserball_blue_wins=await gamehelper.get_wins(GameType.SM5, Team.BLUE),
        role_plot=img_to_b64(role_plot)
    )