import unittest

from db.sm5 import SM5Game
from db.types import IntRole
from helpers.replay import Replay, ReplayTeam, ReplayPlayer, ReplayEvent, ReplayCellChange
from helpers.replay_sm5 import create_sm5_replay
from tests.helpers.environment import setup_test_database, get_sm5_game_id, \
    teardown_test_database, add_entity, get_red_team, get_green_team, create_zap_event, create_resupply_lives_event


class TestReplaySm5(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await setup_test_database(basic_events=False)

    async def asyncTearDown(self):
        await teardown_test_database()

    async def test_create_sm5_replay(self):
        game = await SM5Game.filter(id=get_sm5_game_id()).first()

        entity1, entity_end1 = await add_entity(entity_id="@NotLoggedIn", name="Indy", team=get_red_team(),
                                                role=IntRole.COMMANDER, type="player", sm5_game=game)
        entity2, entity_end2 = await add_entity(entity_id="@NotMember", name="Miles", team=get_green_team(),
                                                role=IntRole.SCOUT, type="player", sm5_game=game)
        entity3, entity_end3 = await add_entity(entity_id="LoggedIn", name="Bumblebee", team=get_red_team(),
                                                role=IntRole.MEDIC, type="player", sm5_game=game)

        await game.events.add(await create_zap_event(2000, entity1.entity_id, entity2.entity_id))
        await game.events.add(await create_resupply_lives_event(2500, entity3.entity_id, entity1.entity_id))

        replay = await create_sm5_replay(game)

        expected = Replay(
            column_headers=["Role", "Codename", "Score", "Lives", "Shots", "Missiles", "Spec", "Accuracy", "K/D"],
            teams=[ReplayTeam(name="Fire Team",
                              css_class="fire-team",
                              players=[
                                  ReplayPlayer(
                                      cells=[
                                          '<img src="/assets/sm5/roles/commander.png" alt="Commander" width="30" height="30">',
                                          "Indy",
                                          "0",
                                          "15",
                                          "5",
                                          "0",
                                          "",
                                          "",
                                      ],
                                      row_id="r1"),
                                  ReplayPlayer(
                                      cells=[
                                          '<img src="/assets/sm5/roles/medic.png" alt="Medic" width="30" height="30">',
                                          "Bumblebee",
                                          "0",
                                          "20",
                                          "0",
                                          "0",
                                          "",
                                          "",
                                      ],
                                      row_id="r2"),
                              ]),
                   ReplayTeam(name="Earth Team",
                              css_class="earth-team",
                              players=[
                                  ReplayPlayer(
                                      cells=[
                                          '<img src="/assets/sm5/roles/scout.png" alt="Scout" width="30" height="30">',
                                          "Miles",
                                          "0",
                                          "15",
                                          "0",
                                          "0",
                                          "",
                                          "",
                                      ],
                                      row_id="r3"),
                              ]),
                   ],
            events=[ReplayEvent(timestamp_millis=2000,
                                message='<span class="fire-team">Indy</span> zaps <span class="earth-team">Miles</span>',
                                cell_changes=[
                                    ReplayCellChange(row_id="r1", column=4, new_value="29")
                                ],
                                row_changes=[])],
        )

        #self.assertEqual(expected, replay)


if __name__ == '__main__':
    unittest.main()
