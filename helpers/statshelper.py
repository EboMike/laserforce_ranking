from typing import List, Tuple, Optional, Callable, Any
from sentry_sdk import Hub, start_transaction
from db.models import SM5Game, EntityEnds, SM5Stats, IntRole, LaserballStats, LaserballGame
from tortoise.functions import Sum

# stats helpers

"""

General helpers

"""

def _millis_to_time(milliseconds: Optional[int]) -> str:
    """Converts milliseconds into an MM:SS string."""
    if milliseconds is None:
        return "00:00"

    return "%02d:%02d" % (milliseconds / 60000, milliseconds % 60000 / 1000)

"""

Average score at time

"""

async def get_average_red_score_at_time_sm5(time: int) -> int:
    """
    Gets the average red score at a given time
    by going through all games and finding the
    average red score at the given time
    """

    scores = []

    for game in await SM5Game.all():
        scores.append(await game.get_red_score_at_time(time))

    return sum(scores) // len(scores)

async def get_average_green_score_at_time_sm5(time: int) -> int:
    """
    Gets the average green score at a given time
    by going through all games and finding the
    average green score at the given time
    """

    scores = []

    for game in await SM5Game.all():
        scores.append(await game.get_green_score_at_time(time))

    return sum(scores) // len(scores)

"""

More specific stats

"""

async def count_zaps(game: SM5Game, zapping_entity_id: str, zapped_entity_id: str) -> int:
    """Returns the number of times one entity zapped another."""
    return await (game.events.filter(
        arguments__filter={"0": zapping_entity_id}
    ).filter(
        arguments__filter={"1": " zaps "}
    ).filter(
        arguments__filter={"2": zapped_entity_id}
    ).count())


async def count_blocks(game: LaserballGame, zapping_entity_id: str, zapped_entity_id: str) -> int:
    """Returns the number of times one entity blocked another."""
    return await (game.events.filter(
        arguments__filter={"0": zapping_entity_id}
    ).filter(
        arguments__filter={"1": " blocks "}
    ).filter(
        arguments__filter={"2": zapped_entity_id}
    ).count())


async def count_missiles(game: SM5Game, missiling_entity_id: str, missiled_entity_id: str) -> int:
    """Returns the number of times one entity missiled another."""
    return await (game.events.filter(
        arguments__filter={"0": missiling_entity_id}
    ).filter(
        arguments__filter={"1": " missiles "}
    ).filter(
        arguments__filter={"2": missiled_entity_id}
    ).count())

"""

Very general stats

"""

async def get_points_scored() -> int:
    """
    Gets the total points scored by going through
    all games and adding up the total points scored

    (SM5)
    """

    points = 0

    for entity in await EntityEnds.filter(sm5games__ranked=True, sm5games__mission_name__icontains="space marines").all():
        points += entity.score

    return points

async def get_nukes_launched() -> int:
    """
    Gets the total nukes launched by going through
    all games and adding up the total nukes launched
    """

    nukes = 0

    for stats in await SM5Stats.filter(nukes_detonated__gt=0).all():
        nukes += stats.nukes_detonated

    return nukes

async def get_nukes_cancelled() -> int:
    """
    Gets the total nukes cancelled by going through
    all games and adding up the total nukes cancelled
    """

    nukes = 0

    for stats in await SM5Stats.filter(nuke_cancels__gt=0).all():
        nukes += stats.nuke_cancels

    return nukes

async def get_medic_hits() -> int:
    """
    Gets the total medic hits by going through
    all games and adding up the total medic hits
    """

    hits = 0

    for stats in await SM5Stats.filter(medic_hits__gt=0).all():
        hits += stats.medic_hits

    return hits

async def get_own_medic_hits() -> int:
    """
    Gets the total own medic hits by going through
    all games and adding up the total own medic hits
    """

    hits = 0

    for stats in await SM5Stats.filter(own_medic_hits__gt=0).all():
        hits += stats.own_medic_hits

    return hits

# laserball totals

async def get_goals_scored() -> int:
    """
    Gets the total goals scored by going through
    all games and adding up the total goals scored

    (Laserball)
    """

    return sum(await LaserballStats.filter(laserballgames__ranked=True).annotate(sum=Sum("goals")).values_list("sum", flat=True))

async def get_assists() -> int:
    """
    Gets the total assists by going through
    all games and adding up the total assists

    (Laserball)
    """

    return sum(await LaserballStats.filter(laserballgames__ranked=True).annotate(sum=Sum("assists")).values_list("sum", flat=True))

async def get_passes() -> int:
    """
    Gets the total passes by going through
    all games and adding up the total passes

    (Laserball)
    """

    return sum(await LaserballStats.filter(laserballgames__ranked=True).annotate(sum=Sum("passes")).values_list("sum", flat=True))

async def get_steals() -> int:
    """
    Gets the total steals by going through
    all games and adding up the total steals

    (Laserball)
    """

    return sum(await LaserballStats.filter(laserballgames__ranked=True).annotate(sum=Sum("steals")).values_list("sum", flat=True))

async def get_clears() -> int:
    """
    Gets the total clears by going through
    all games and adding up the total clears

    (Laserball)
    """

    return sum(await LaserballStats.filter(laserballgames__ranked=True).annotate(sum=Sum("clears")).values_list("sum", flat=True))

async def get_blocks() -> int:
    """
    Gets the total blocks by going through
    all games and adding up the total blocks

    (Laserball)
    """

    return sum(await LaserballStats.filter(laserballgames__ranked=True).annotate(sum=Sum("blocks")).values_list("sum", flat=True))

# top roles
# could be improved by accounting for the amount of games played
# could be combined into one function

async def get_top_commanders(amount=5) -> List[Tuple[str, int]]:
    """
    Gets the top commanders by going through
    all games and getting the average score
    for each player
    """

    data = {}

    async for entity_end in EntityEnds.filter(sm5games__ranked=True, sm5games__mission_name__icontains="space marines", entity__role=IntRole.COMMANDER).prefetch_related("entity"):
        codename = entity_end.entity.name
        if data.get(codename):
            data[codename] = (data[codename][0]+entity_end.score, data[codename][1]+1)
        else:
            data[codename] = (entity_end.score, 1)

    # get the average score for each player

    commanders = []

    for key, value in data.items():
        commanders.append((key, value[0]//value[1], value[1]))
    
    # sort the list by score

    commanders.sort(key=lambda x: x[1], reverse=True)

    return commanders[:amount]
    

async def get_top_heavies(amount=5) -> List[Tuple[str, int]]:
    """
    Gets the top heavies by going through
    all games and getting the average score
    for each player
    """

    data = {}

    async for entity_end in EntityEnds.filter(sm5games__ranked=True, sm5games__mission_name__icontains="space marines", entity__role=IntRole.HEAVY).prefetch_related("entity"):
        codename = entity_end.entity.name
        if data.get(codename):
            data[codename] = (data[codename][0]+entity_end.score, data[codename][1]+1)
        else:
            data[codename] = (entity_end.score, 1)

    # get the average score for each player

    heavies = []

    for key, value in data.items():
        heavies.append((key, value[0]//value[1], value[1]))
    
    # sort the list by score

    heavies.sort(key=lambda x: x[1], reverse=True)

    return heavies[:amount]

async def get_top_scouts(amount=5) -> List[Tuple[str, int]]:
    """
    Gets the top scouts by going through
    all games and getting the average score
    for each player
    """

    data = {}

    async for entity_end in EntityEnds.filter(sm5games__ranked=True, sm5games__mission_name__icontains="space marines", entity__role=IntRole.SCOUT).prefetch_related("entity"):
        codename = entity_end.entity.name
        if data.get(codename):
            data[codename] = (data[codename][0]+entity_end.score, data[codename][1]+1)
        else:
            data[codename] = (entity_end.score, 1)

    # get the average score for each player

    scouts = []

    for key, value in data.items():
        scouts.append((key, value[0]//value[1], value[1]))
    
    # sort the list by score

    scouts.sort(key=lambda x: x[1], reverse=True)

    return scouts[:amount]

async def get_top_ammos(amount=5) -> List[Tuple[str, int]]:
    """
    Gets the top ammos by going through
    all games and getting the average score
    for each player
    """

    data = {}

    async for entity_end in EntityEnds.filter(sm5games__ranked=True, sm5games__mission_name__icontains="space marines", entity__role=IntRole.AMMO).prefetch_related("entity"):
        codename = entity_end.entity.name
        if data.get(codename):
            data[codename] = (data[codename][0]+entity_end.score, data[codename][1]+1)
        else:
            data[codename] = (entity_end.score, 1)

    # get the average score for each player

    ammos = []

    for key, value in data.items():
        ammos.append((key, value[0]//value[1], value[1]))
    
    # sort the list by score

    ammos.sort(key=lambda x: x[1], reverse=True)

    return ammos[:amount]

async def get_top_medics(amount=5) -> List[Tuple[str, int]]:
    """
    Gets the top medics by going through
    all games and getting the average score
    for each player
    """

    data = {}

    async for entity_end in EntityEnds.filter(sm5games__ranked=True, sm5games__mission_name__icontains="space marines", entity__role=IntRole.MEDIC).prefetch_related("entity"):
        codename = entity_end.entity.name
        
        if data.get(codename):
            data[codename] = (data[codename][0]+entity_end.score, data[codename][1]+1)
        else:
            data[codename] = (entity_end.score, 1)

    # get the average score for each player

    medics = []

    for key, value in data.items():
        medics.append((key, value[0]//value[1], value[1]))
    
    # sort the list by score

    medics.sort(key=lambda x: x[1], reverse=True)

    return medics[:amount]

# get ranking accuracy

async def get_ranking_accuracy() -> float:
    """
    Ranks how accurate the ranking system is
    at predicting the winner of a game

    returns a float between 0 and 1
    """

    correct = 0
    total = 0

    for game in await SM5Game.filter(ranked=True).all():
        red_chance, green_chance = await game.get_win_chance_before_game()
        red_score, green_score = await game.get_red_score(), await game.get_green_score()

        # see if scores are close enough
        if int(red_chance) == int(green_chance) and abs(red_score - green_score) <= 3000:
            # if so, add 2 to correct
            # it means we did a phoenomenal job at predicting the winner
            # technically this means our rating could be higher than 100%
            # but let's treat it like extra credit :)
            correct += 2
        elif red_chance >= green_chance and red_score > green_score:
            correct += 1
        elif green_chance >= red_chance and green_score > red_score:
            correct += 1
        total += 1

    return correct / total if total != 0 else 0

# performance helpers

def sentry_trace(func) -> Callable:
    """
    Async sentry tracing decorator
    """
    async def wrapper(*args, **kwargs) -> Any:
        transaction = Hub.current.scope.transaction
        if transaction:
            with transaction.start_child(op=func.__name__):
                return await func(*args, **kwargs)
        else:
            with start_transaction(op=func.__name__, name=func.__name__):
                return await func(*args, **kwargs)

    return wrapper