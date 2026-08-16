"""Pydantic models for ScanSpace payloads."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Vec3(BaseModel):
    x: float
    y: float
    z: float

    @classmethod
    def from_array(cls, arr: list[float]) -> "Vec3":
        return cls(x=arr[0], y=arr[1], z=arr[2])


class Wall(BaseModel):
    id: str
    start: list[float]
    end: list[float]
    thickness: float = 0.15
    height: float = 2.5


class Door(BaseModel):
    id: str
    wall_id: str
    position: float
    width: float = 0.9


class Window(Door):
    sill_height: float = 0.9
    height: float = 1.2


class Furniture(BaseModel):
    id: str
    type: str
    position: list[float]
    rotation: list[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])
    dimensions: list[float]
    model_uri: str | None = None
    entity_id: str | None = None


class RoomPayload(BaseModel):
    id: str
    name: str
    floor_id: str
    walls: list[Wall] = Field(default_factory=list)
    floor_outline: list[list[float]] = Field(default_factory=list, alias="floorOutline")
    ceiling_height: float = 2.5
    doors: list[Door] = Field(default_factory=list)
    windows: list[Window] = Field(default_factory=list)
    furniture: list[Furniture] = Field(default_factory=list)
    scan_state: str = "incomplete"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RoomPayload":
        return cls.model_validate(data)

    def area_m2(self) -> float:
        outline = self.floor_outline
        if len(outline) < 3:
            return 0.0
        total = 0.0
        for i in range(len(outline)):
            a = outline[i]
            b = outline[(i + 1) % len(outline)]
            total += a[0] * b[1] - a[1] * b[0]
        return abs(total) / 2.0


class FloorPayload(BaseModel):
    id: str
    name: str
    elevation: float = 0.0
    rooms: list[RoomPayload] = Field(default_factory=list)


class HousePayload(BaseModel):
    id: str
    name: str
    floors: list[FloorPayload] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HousePayload":
        return cls.model_validate(data)
