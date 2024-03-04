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
        self.sm5_rating = Rating(ratinghelper.ASSUMED_SKILL_MU, ratinghelper.ASSUMED_SKILL_SIGMA)
        self.laserball_rating = Rating(ratinghelper.ASSUMED_SKILL_MU, ratinghelper.ASSUMED_SKILL_SIGMA)
        self.sm5_rating_mu = ratinghelper.ASSUMED_SKILL_MU
        self.sm5_rating_sigma = ratinghelper.ASSUMED_SKILL_SIGMA
        self.laserball_rating_mu = ratinghelper.ASSUMED_SKILL_MU
        self.laserball_rating_sigma = ratinghelper.ASSUMED_SKILL_SIGMA

    def __str__(self) -> str:
        return f"{self.codename} (non member)"
    
    def __repr__(self) -> str:
        return f"{self.codename} (non member)"

@app.get("/tools")
async def tools(request: Request) -> str:
    players = await Player.filter(sm5_mu__not=25, laserball_mu__not=25)

    # all_players = {codename: (sm5_rating, lb_rating)
    all_players = {player.codename: (player.sm5_rating.ordinal(), player.laserball_rating.ordinal()) for player in players}

    return await render_template(request, "tools.html", players=players, all_players=all_players)

@app.post("/matchmake")
@sentry_trace
async def matchmake_post(request: Request) -> str:
    logger.info("Matchmaking players")

    data = request.form

    players = []

    mode = data.get("mode", "sm5")
    if mode == "": mode = "sm5"
    mode = GameType(mode)

    for i in range(16):
        try:
            codename = data[f"player{i}"][0]
        except KeyError:
            continue
        if codename == "":
            continue

        if codename == "DUMMY":
            p = None
        else:
            p = await Player.filter(codename=codename).first()
        
        if p is None:
            p = FakePlayer(codename)
        players.append(p)

        logger.debug(f"Added dummy player Rating(25, 8.333) for {codename}")

    logger.debug(f"Players: {players}")

    match = ratinghelper.matchmake(players, mode)

    team1 = match[0]
    team2 = match[1]

    team1_ratings = []
    team2_ratings = []

    logger.debug(f"Team 1: {team1}")
    logger.debug(f"Team 2: {team2}")

    for player in team1:
        p = await Player.filter(codename=player.codename).first()
        if p:
            team1_ratings.append(p.sm5_rating.ordinal())
        else:
            team1_ratings.append(0)
    
    for player in team2:
        p = await Player.filter(codename=player.codename).first()
        if p:
            team2_ratings.append(p.sm5_rating.ordinal())
        else:
            team2_ratings.append(0)

    win_chance = ratinghelper.get_win_chance(*match)
    
    # format match
    
    def key(obj):
        game = []
        for i in range(len(obj)):
            game.append(getattr(obj[i], "codename"))
        return game
    
    match = list(map(key, list(match)))

    win_chance[0] = round(win_chance[0], 2)
    win_chance[1] = round(win_chance[1], 2)

    logger.info(f"Match created with win chance: {win_chance}")

    return await render_template(
        request,
        "matchmake_results.html",
        team1=team1,
        team2=team2,
        team1_ratings=team1_ratings,
        team2_ratings=team2_ratings,
        win_chance=win_chance,
        zip=zip,
    )

@app.post("/win_chance")
async def win_chance_post(request: Request) -> str:
    logger.info("Calculating win chance")

    data = request.form

    team1 = []
    team2 = []

    mode = data.get("mode")
    if not mode: mode = "sm5"
    mode = GameType(mode)

    for i in range(8):
        codename = data.get(f"1player{i}")
        if not codename:
            continue
        p = await Player.filter(codename=codename).first()
        team1.append(p)

    for i in range(8):
        codename = data.get(f"2player{i}")
        if not codename:
            continue
        p = await Player.filter(codename=codename).first()
        team2.append(p)

    logger.debug(f"Team 1: {team1}")
    logger.debug(f"Team 2: {team2}")

    win_chance = ratinghelper.get_win_chance(team1, team2)
    
    # format match

    for i in range(len(team1)):
        team1[i] = team1[i].codename

    for i in range(len(team2)):
        team2[i] = team2[i].codename

    win_chance[0] = round(win_chance[0], 2)
    win_chance[1] = round(win_chance[1], 2)

    logger.info(f"Win chance calculated: {win_chance}")

    return await render_template(request, "win_calculator_results.html", team1=team1, team2=team2, win_chance=win_chance)