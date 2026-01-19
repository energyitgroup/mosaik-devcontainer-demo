import mosaik_api_v3
from mosaik_api_v3 import CreateResult, InputData, Meta, ModelName, OutputRequest, Time
from mosaik_api_v3.types import EntityId, OutputData

from pprint import pprint

META: Meta = {
    "api_version": "3.0", # Mosaik API version is dependent on the base class defined in the Simulator constructor parameter
    "type": "hybrid",     # 
    "models": {
        "PVProfits": {
            "public": True,
            "params": ["eid"],
            "trigger": [],
            "non-trigger": ["P[MW]"],
            "persistent": [],
            "non-persistent": ["profit[EUR]"],
        }
    },
}

class Simulator(mosaik_api_v3.Simulator):

    profits: dict[EntityId, float | None]

    def __init__(self):

        self.profits = {}
        super().__init__(META)

    def init(self, sid: str, time_resolution: float, price: float, step_size: int = 900) -> Meta:

        self.sid = sid
        self.time_resolution = time_resolution
        self.step_size = step_size
        self.price = price

        return self.meta

    def create(self, num: int, model: ModelName, eid: None | str | list[str] = None) -> list[CreateResult]:

        if eid is None:
            eid = [
                f"PVProfits-{i}"
                for i in range(len(self.profits), len(self.profits) + num)
            ]

        if isinstance(eid, str):

            if num != 1:
                raise TypeError(
                    "When creating multiple 'PVProfits' entities at once, `eid` must "
                    "be a list of entity IDs or `None`. It is a single string."
                )

            eid = [eid]

        if len(eid) != num:
            raise ValueError(
                "When creating multiple 'PVProfits' entities, the number of elements "
                "of `eid` must match the number of created entities."
            )

        new_entities: list[CreateResult] = []
        for e in eid:

            if e in self.profits:
                raise ValueError(f"Entity with ID {e} has already been created.")

            self.profits[e] = None
            new_entities.append(
                {
                    "eid": e,
                    "type": "PVProfits",
                }
            )

        return new_entities

    def step(self, time: Time, inputs: InputData, max_advance: Time = 3600) -> Time | None:

        for eid, attrs in inputs.items():

            power = sum(attrs["P[MW]"].values())

            self.profits[eid] = (power * self.step_size * self.time_resolution / 3600 * self.price)

        return time + self.step_size

    def get_data(self, outputs: OutputRequest) -> OutputData:

        output_data = {}

        for eid, attrs in outputs.items():

            if eid not in self.profits.keys():
                raise ValueError("Unknown entity ID '%s'" % eid)

            output_data[eid] = {}

            for attr in attrs:

                if attr != "profit[EUR]":
                    raise ValueError("Unknown output attribute '%s'" % attr)

                output_data[eid][attr] = self.profits[eid]

        return output_data
