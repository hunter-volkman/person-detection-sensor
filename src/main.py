import asyncio
from typing import Any, ClassVar, Mapping, Optional, Sequence, Dict
from typing_extensions import Self

from viam.components.sensor import Sensor
from viam.components.camera import Camera
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading, struct_to_dict
from viam.services.vision import Vision
from viam.logging import getLogger
from viam.resource.easy_resource import EasyResource

LOGGER = getLogger(__name__)

class PersonDetector(Sensor, EasyResource, ResourceBase):
    MODEL: ClassVar[Model] = Model(
        ModelFamily("huntervolkman", "person-detection-sensor"), 
        "person-detector"
    )

    def __init__(self, name: str):
        super().__init__(name=name)

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        # Check if vision service dependency is present
        vision_service = next((dep for dep in dependencies.values() if isinstance(dep, Vision)), None)
        if not vision_service:
            raise ValueError("Vision service instance is required for PersonDetector")
        
        sensor = cls(config.name)
        sensor.reconfigure(config, dependencies)
        return sensor

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        attrs = struct_to_dict(config.attributes)
        required_attrs = ["vision_service", "camera_name"]

        for attr in required_attrs:
            if attr not in attrs:
                raise Exception(f"{attr} attribute is required")

        return [attrs["vision_service"], attrs["camera_name"]]

    def reconfigure(
        self,
        config: ComponentConfig,
        dependencies: Mapping[ResourceName, ResourceBase]
    ):
        attrs = struct_to_dict(config.attributes)
        self.vision_service_name = attrs["vision_service"]
        self.camera_name = attrs["camera_name"]
        self.dependencies = dependencies

    async def get_readings(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, Any]:
        # Get camera from dependencies
        camera = self.dependencies.get(ResourceName(namespace="rdk", type="component", subtype="camera", name=self.camera_name))
        if not camera:
            raise ValueError(f"Camera {self.camera_name} is not available")
        
        # Get vision service from dependencies
        vision_service = self.dependencies.get(ResourceName(namespace="rdk", type="service", subtype="vision", name=self.vision_service_name))
        if not vision_service:
            raise ValueError(f"Vision service {self.vision_service_name} is not available")
        
        # Get image from camera
        image = await camera.get_image()
        if not image:
            raise ValueError("Failed to get image from camera")
        
        # Get detections from vision service
        detections = await vision_service.get_detections(image)
        person_detected = any(
            detection.class_name.lower() == "person" 
            for detection in detections
        )

        LOGGER.info(f"Person detected: {person_detected}")

        return {
            "person_detected": 1 if person_detected else 0
        }

if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())
