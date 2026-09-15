"""Checks headless da cena unificada e de suas regras de interação."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core.engine import Engine
from src.core.state_machine import MuseumState
from src.museum.collisions import CollisionMap, Rect


class CollisionMapTests(unittest.TestCase):
    def test_blocks_solids_and_slides_at_wall(self):
        world = CollisionMap(Rect(0, 0, 10, 10), (Rect(4, 0, 5, 10),), .2)
        self.assertFalse(world.walkable(4.5, 3))
        self.assertTrue(world.walkable(3, 3))
        self.assertEqual(world.move(3, 3, 2, 0), (3, 3))


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Engine()

    @classmethod
    def tearDownClass(cls):
        cls.engine.sound.stop()
        pygame.quit()

    def test_complete_collection_and_asset_fallbacks(self):
        self.assertEqual(len(self.engine.EXHIBITS), 11)
        self.assertEqual(len(self.engine.tour_durations), 11)
        self.assertTrue(self.engine.nefertiti_mesh[0])
        self.assertTrue(self.engine.nefertiti_mesh[1])

    def test_internal_walls_do_not_block_doors(self):
        self.assertFalse(self.engine._walkable(-11, 10))
        self.assertTrue(self.engine._walkable(-11, 23.5))
        self.assertFalse(self.engine._walkable(-7, 31))

    def test_raycast_hits_exhibit_in_front_of_camera(self):
        self.engine._start(MuseumState.CURATION)
        self.engine.camera_pos = [-8, 1.4, 8]
        self.engine.camera_target = self.engine.camera_pos[:]
        self.engine.yaw = 0.0
        self.assertEqual(self.engine._inspect_hit(), 0)

    def test_credits_pause_and_mode_transitions(self):
        self.engine._start(MuseumState.IMMERSIVE_TOUR)
        self.engine._toggle_pause()
        self.assertEqual(self.engine.state_machine.current, MuseumState.PAUSED)
        self.engine._toggle_pause()
        self.assertEqual(self.engine.state_machine.current, MuseumState.IMMERSIVE_TOUR)
        self.engine._open_credits(MuseumState.IMMERSIVE_TOUR)
        self.assertEqual(self.engine.state_machine.current, MuseumState.CREDITS)
        self.engine._close_credits()
        self.assertEqual(self.engine.state_machine.current, MuseumState.IMMERSIVE_TOUR)

    def test_lights_toggle_and_mouse_rotates_camera(self):
        self.engine._start(MuseumState.EXPLORATION)
        self.assertTrue(self.engine.lights_enabled)
        self.engine._event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_i))
        self.assertFalse(self.engine.lights_enabled)
        self.engine._event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_i))
        self.assertTrue(self.engine.lights_enabled)

        self.engine.mouse_grabbed = True
        old_yaw = self.engine.yaw
        self.engine._event(pygame.event.Event(pygame.MOUSEMOTION, rel=(20, -5)))
        self.assertGreater(self.engine.yaw, old_yaw)
        self.assertEqual(self.engine.target_yaw, self.engine.yaw)


if __name__ == "__main__":
    unittest.main()
