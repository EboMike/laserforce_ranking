from objects import Team, Role, Player, GameType, SM5GamePlayer, LaserballGamePlayer

async def get_data_from_form_sm5(players: list, game_players: list, data: dict, team: Team):
    team_ = team.value[0] # green = "g", red = "r", blue = "b"
    for i in range(1, 8):
        try:
            player_name = data[f"{team_}name{i}"]
            player_role = data[f"{team_}role{i}"]
            player_score = data[f"{team_}score{i}"]
            if player_name == "" or player_role == "" or player_score == "":
                break
        except KeyError:
            break
        
        try:
            player = await Player.from_name(player_name)
        except IndexError:  # player doens't exist
            raise ValueError("Invalid data!")
        
        player_id = player.player_id
        game = SM5GamePlayer(player_id, 0, team, Role(player_role), int(player_score))
        game_players.append(game)
        player.game_player = game
        players.append(player)

async def get_data_from_form_laserball(players: list, game_players: list, data: dict, team: Team):
    team_ = team.value[0] # green = "g", red = "r", blue = "b"
    for i in range(1, 8):
        try:
            player_name = data[f"{team_}name{i}"]
            player_goals = data[f"{team_}goals{i}"]
            player_assists = data[f"{team_}assists{i}"]
            player_steals = data[f"{team_}steals{i}"]
            player_clears = data[f"{team_}clears{i}"]
            player_blocks = data[f"{team_}blocks{i}"]
            if not player_name or not player_goals or not player_assists or not player_steals or not player_clears or not player_blocks:
                break
        except KeyError:
            break
        
        try:
            player = await Player.from_name(player_name)
        except IndexError:  # player doens't exist
            raise ValueError("Invalid data!")
        
        player_id = player.player_id
        game = LaserballGamePlayer(player_id, 0, team, player_goals, player_assists, player_steals, player_clears, player_blocks)
        game_players.append(game)
        player.game_player = game
        players.append(player)