# Person Detection Sensor Module

A custom Viam module that provides a sensor component for real-time person detection using computer vision.

## Overview

This module integrates with Viam's vision service to create a sensor that returns binary feedback about person presence in camera frames. The sensor returns:
- `1` when a person is detected
- `0` when no person is detected

## Requirements

- Viam server
- Camera component
- Vision service configured with person detection model

## Configuration

### Module Configuration

```json
{
  "type": "local",
  "name": "local-module-1",
  "executable_path": "/path/to/module/run.sh"
}
```

### Sensor Configuration

```json
{
  "name": "sensor-1",
  "type": "sensor",
  "model": "huntervolkman:person-detection-sensor:person-detector",
  "attributes": {
    "vision_service": "vision-1",
    "camera_name": "camera-1"
  }
}
```

### Required Attributes

- `vision_service`: Name of the configured vision service (required)
- `camera_name`: Name of the camera component to use (required)

## Sensor Readings

The sensor provides a single reading:
```json
{
  "person_detected": 1  // or 0
}
```

## Dependencies

This module depends on:
- A configured camera component
- A configured vision service with person detection capabilities

## Usage Example

1. Configure a camera component
2. Configure the vision service with person detection model
3. Configure this sensor with the required attributes
4. Read from the sensor to get real-time person detection status

The sensor can be used for:
- Security monitoring
- Occupancy detection
- Automated responses to human presence
- Integration with other Viam components and services