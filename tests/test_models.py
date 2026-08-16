"""Unit tests for ScanSpace Pydantic models."""

import pytest
from custom_components.scanspace.models import (
    Vec3,
    Wall,
    Door,
    Window,
    Furniture,
    RoomPayload,
    FloorPayload,
    HousePayload,
)


def test_vec3_from_array():
    v = Vec3.from_array([1.0, 2.5, -3.0])
    assert v.x == 1.0
    assert v.y == 2.5
    assert v.z == -3.0


def test_wall_model():
    wall = Wall(
        id="wall_1",
        start=[0.0, 0.0, 0.0],
        end=[4.0, 0.0, 0.0],
        thickness=0.25,
        height=2.7,
    )
    assert wall.id == "wall_1"
    assert wall.thickness == 0.25
    assert wall.height == 2.7


def test_door_and_window_models():
    door = Door(id="door_1", wall_id="wall_1", position=1.5, width=0.85)
    assert door.id == "door_1"
    assert door.width == 0.85

    window = Window(
        id="win_1",
        wall_id="wall_1",
        position=2.5,
        width=1.2,
        sill_height=0.8,
        height=1.4,
    )
    assert window.id == "win_1"
    assert window.sill_height == 0.8
    assert window.height == 1.4


def test_furniture_model():
    furn = Furniture(
        id="f_couch",
        type="sofa",
        position=[1.0, 0.0, 1.0],
        rotation=[0.0, 0.0, 0.0, 1.0],
        dimensions=[2.0, 0.8, 0.9],
        model_uri="models/sofa.glb",
        entity_id="light.couch_light",
    )
    assert furn.id == "f_couch"
    assert furn.type == "sofa"
    assert furn.entity_id == "light.couch_light"


def test_room_area_calculation():
    # 5m x 4m rectangle = 20.0 m²
    room = RoomPayload(
        id="room_1",
        name="Living Room",
        floor_id="floor_1",
        floorOutline=[
            [0.0, 0.0],
            [5.0, 0.0],
            [5.0, 4.0],
            [0.0, 4.0],
        ],
    )
    assert room.area_m2() == pytest.approx(20.0, rel=1e-3)

    # Triangle: (0,0), (4,0), (0,3) -> area = 6.0 m²
    tri_room = RoomPayload(
        id="room_tri",
        name="Attic",
        floor_id="floor_1",
        floorOutline=[
            [0.0, 0.0],
            [4.0, 0.0],
            [0.0, 3.0],
        ],
    )
    assert tri_room.area_m2() == pytest.approx(6.0, rel=1e-3)

    # Incomplete outline (< 3 points)
    empty_room = RoomPayload(id="room_empty", name="Empty", floor_id="floor_1", floorOutline=[[0.0, 0.0]])
    assert empty_room.area_m2() == 0.0


def test_house_payload_deserialization(sample_house_dict):
    house = HousePayload.from_dict(sample_house_dict)
    assert house.id == "house_alpha_01"
    assert house.name == "Musterhaus"
    assert len(house.floors) == 1

    floor = house.floors[0]
    assert floor.id == "floor_ground"
    assert len(floor.rooms) == 1

    room = floor.rooms[0]
    assert room.id == "room_living"
    assert room.name == "Wohnzimmer"
    assert room.area_m2() == 20.0
    assert len(room.walls) == 4
    assert len(room.doors) == 1
    assert len(room.windows) == 1
    assert len(room.furniture) == 2
