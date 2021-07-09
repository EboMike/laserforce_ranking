import mysql # type: ignore
import asyncio
from typing import List, Union, Tuple
from dataclasses import dataclass
from config import config # type: ignore

sql = None

@dataclass
class Game:
    id: int
    player_id: str
    won: bool
    role: str
    score: int
    
@dataclass
class Player:
    id: int
    player_id: str
    codename: str

def average(to_average: Union[List, Tuple]):
    return sum(to_average) / len(to_average)

def format_sql(to_format):
    final = []
    for i in to_format:
        final.append(i[0])
    return final

async def get_top_100(role):
    q = await sql.fetchall(f"SELECT player_id FROM players ORDER BY ranking_{role} DESC LIMIT 100")
    return format_sql(q)

async def get_all_players():
    q = await sql.fetchall("SELECT player_id FROM players")
    return format_sql(q)
    
async def ranking_cron():
    roles = ["scout", "heavy", "commander", "medic", "ammo"]
    for player_id in await get_all_players():
        for role in roles:
            try:
                score = await calculate_total_score(player_id, role)
            except ZeroDivisionError: # no games
                score = 0
            await sql.execute(f"UPDATE players SET ranking_{role} = %s WHERE player_id = %s", (score, player_id))

async def fetch_player(id: int) -> Game:
    q = await sql.fetchall("SELECT * FROM `players` WHERE `id` = %s", (id))
    return Player(*q[0])

async def fetch_player_by_name(codename: int) -> Game:
    q = await sql.fetchall("SELECT * FROM `players` WHERE `codename` = %s", (codename))
    return Player(*q[0])

async def database_player(player_id: str, codename: str) -> None:
    # clean codename
    codename = codename.replace(" ☺", "").replace("☺", "")
    await sql.execute("""INSERT INTO `players` (player_id, codename, ranking)
                        VALUES (%s, %s, %s)""", (player_id, codename, 0.0))

async def log_game(player_id: str, won: bool, role: str, score: int) -> None:
    await sql.execute("""INSERT INTO `games` (player_id, won, role, score)
                        VALUES (%s, %s, %s, %s)""", (player_id, int(won), role, score))
    
async def fetch_game(id: int) -> Game:
    q = await sql.fetchall("SELECT * FROM `games` WHERE `id` = %s", (id))
    return Game(*q[0])

async def get_average_score(role: str, player_id: str) -> int:
    q = await sql.fetchall("SELECT `score` FROM `games` WHERE `role` = %s AND NOT `player_id` = %s", (role, player_id))
    return average(format_sql(q))

async def get_my_average_score(role: str, player_id: str):
    q = await sql.fetchall("SELECT `score` FROM `games` WHERE `role` = %s AND `player_id` = %s", (role, player_id))
    return average(format_sql(q))
    
async def calculate_total_score(player_id: int, role: str) -> float:
    world_average = await get_average_score(role, player_id)
    my_average = await get_my_average_score(role, player_id)
    return round(world_average / my_average, 2)

async def init_sql():
    global sql
    if not sql:
        sql = await mysql.MySQLPool.connect(config["db_host"], config["db_user"],
                                config["db_password"], config["db_database"],
                                config["db_port"])