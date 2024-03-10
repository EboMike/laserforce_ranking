from sanic import Request
from shared import app
from helpers import ratinghelper
from utils import render_template, get_post
from objects import GameType
from db.models import Player
from sanic.log import logger
from helpers.statshelper import sentry_trace
from openskill.models import PlackettLuceRating as Rating

class FakePlayer:
    def __init__(self, codename: str) -> None:
        self.codename = codename
        self.sm5_rating = Rating(ratinghelper.MU, ratinghelper.SIGMA)
        self.laserball_rating = Rating(ratinghelper.MU, ratinghelper.SIGMA)
        self.sm5_rating_mu = ratinghelper.MU
        self.sm5_rating_sigma = ratinghelper.SIGMA
        self.laserball_rating_mu = ratinghelper.MU
        self.laserball_rating_sigma = ratinghelper.SIGMA

    def __str__(self) -> str:
        return f"{self.codename} (non member)"
    
    def __repr__(self) -> str:
        return f"{self.codename} (non member)"

@app.get("/matchmaking")
async def matchmaking(request: Request) -> str:
    players = await Player.filter()

    # all_players = {codename: (sm5_rating, lb_rating)
    all_players = {player.codename: (player.sm5_rating.ordinal(), player.laserball_rating.ordinal()) for player in players}

    return await render_template(
        request,
        "matchmaking.html",
        players=players,
        all_players=all_players,
        mode="sm5",
        team1=[],
        team2=[],
    )

@app.post("/matchmaking")
async def matchmaking_post(request: Request) -> str:
    # TODO: logging here

    data = request.form

    team1 = []
    team2 = []

    mode = data.get("mode", "sm5")
    if mode == "": mode = "sm5"
    mode = GameType(mode)

    for i in range(16):
        codename = data.get(f"1player{i}")
        if not codename:
            continue
        codename = codename.strip()
        p = await Player.filter(codename=codename).first()
        team1.append(p.codename)

    for i in range(16):
        codename = data.get(f"2player{i}")
        if not codename:
            continue
        codename = codename.strip()
        p = await Player.filter(codename=codename).first()
        team2.append(p.codename)

    players = await Player.filter()

    # all_players = {codename: (sm5_rating, lb_rating)
    all_players = {player.codename: (player.sm5_rating.ordinal(), player.laserball_rating.ordinal()) for player in players}

    return await render_template(
        request,
        "matchmaking.html",
        players=players,
        all_players=all_players,
        mode=mode,
        team1=team1,
        team2=team2,
    )