from typing import List, Dict, Any, Optional
from app.models.base import (
    SpecialistModel,
    RemoteSensingVQAModel,
    ChangeDetectionModel,
    OpticalSARModel,
    GroundingModel,
    GeoAnalysisModel
)

class ModelRegistry:
    def __init__(self):
        self._models: List[SpecialistModel] = []

    def register(self, model: SpecialistModel):
        self._models.append(model)

    def find_model_for_task(self, task: str) -> Optional[SpecialistModel]:
        for model in self._models:
            if task in model.supported_tasks:
                return model
        return None

registry = ModelRegistry()

# Register the placeholders
registry.register(RemoteSensingVQAModel())
registry.register(ChangeDetectionModel())
registry.register(OpticalSARModel())
registry.register(GroundingModel())
registry.register(GeoAnalysisModel())
