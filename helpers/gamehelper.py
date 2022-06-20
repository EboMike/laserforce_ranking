from shared import sql
from objects import Game, GameType
from helpers import ratinghelper

async def get_total_games_played():
    q = await sql.fetchone("SELECT COUNT(*) FROM sm5_game_players")
    q2 = await sql.fetchone("SELECT COUNT(*) FROM laserball_game_players")
    return q[0] + q2[0]

async def get_total_games():
    q = await sql.fetchone("SELECT COUNT(*) FROM games")
    return q[0]

async def log_sm5_game(game: Game):
    await sql.execute("INSERT INTO `games` (winner, type) VALUES (%s, %s);", (game.winner, game.type.value))
    
    # gets id of the inserted game
    last_row = await sql.fetchone("SELECT LAST_INSERT_ID();")
    game_id = last_row[0]
    
    game.red, game.green = await ratinghelper.update_elo(game.red, game.green, game.winner, GameType.SM5)
    print(game.red, game.green)
    game.players = [*game.red, *game.green]

    # update openskill
    
    for player in game.players:
        player.game_player.game_id = game_id

        await sql.execute(
            """INSERT INTO `sm5_game_players` (player_id, game_id, team, role, score)
                            VALUES (%s, %s, %s, %s, %s)""",
            (
                player.player_id,
                player.game_player.game_id,
                player.game_player.team.value,
                player.game_player.role.value,
                player.game_player.score,
            ),
        )

        # update rating
        await sql.execute("""
            UPDATE players SET
            sm5_mu = %s,
            sm5_sigma = %s
            WHERE id = %s
        """, (
            player.sm5_mu, player.sm5_sigma,
            player.id
        ))
        
async def log_laserball_game(game: Game):
    await sql.execute("INSERT INTO `games` (winner, type) VALUES (%s, %s);", (game.winner, game.type.value))
    
    # gets id of the inserted game
    last_row = await sql.fetchone("SELECT LAST_INSERT_ID();")
    game_id = last_row[0]
    
    game.red, game.green = await ratinghelper.update_elo(game.red, game.blue, game.winner, GameType.SM5)
    game.players = [*game.red, *game.blue]

    # update openskill
    
    for player in game.players:
        player.game_player.game_id = game_id

        await sql.execute(
            """INSERT INTO `laserball_game_players` (player_id, game_id, team, goals, assists, steals, clears, blocks)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                player.player_id,
                player.game_player.game_id,
                player.game_player.team.value,
                player.game_player.goals,
                player.game_player.assists,
                player.game_player.steals,
                player.game_player.clears,
                player.game_player.blocks,
            ),
        )

        # update rating
        await sql.execute("""
            UPDATE players SET
            laserball_mu = %s,
            laserball_sigma = %s
            WHERE id = %s
        """, (
            player.laserball_mu, player.laserball_sigma,
            player.id
        ))