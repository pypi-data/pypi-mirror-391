import dataclasses
import pathlib

import yaml


@dataclasses.dataclass(kw_only=True)
class TransformConfig:
    destack: bool | None = None
    # Crop region is given in the format (x0, y0, width, height) where (x0, y0) is the
    # top-left corner.
    crop: tuple[int, int, int, int] | None = None


@dataclasses.dataclass(kw_only=True)
class CameraConfig:
    resolution: tuple[int, int]
    rtsp_url: str
    transform: TransformConfig | None = None


@dataclasses.dataclass(kw_only=True)
class ServerConfig:
    cameras: dict[str, CameraConfig]
    close_bbox_diagonal_px: float
    http_port: int
    recording_lifetime_s: float
    status_frequency_hz: float

    @property
    def camera_ids(self) -> list[str]:
        return list(self.cameras.keys())


def _load_transform_config(transform_dict: dict) -> TransformConfig:
    """Load transform configuration from a dictionary."""
    crop = transform_dict.get("crop")
    # YAML doesn't have built in tuple support so we convert it here.
    if crop is not None:
        crop = tuple(crop)

    transform = TransformConfig(destack=transform_dict.get("destack"), crop=crop)
    return transform


def _load_camera_configs(cameras_dict: dict) -> dict[str, CameraConfig]:
    """Load camera configurations from a dictionary."""
    cameras = {}
    for cam_id, cam_dict in cameras_dict.items():
        if transform_dict := cam_dict.get("transform"):
            transform = _load_transform_config(transform_dict)
        else:
            transform = None

        cameras[cam_id] = CameraConfig(
            # YAML doesn't have built in tuple support so we convert it here.
            resolution=tuple(cam_dict["resolution"]),
            rtsp_url=cam_dict["rtsp_url"],
            transform=transform,
        )
    return cameras


def load(path: pathlib.Path) -> ServerConfig:
    """Loads the server configuration from a YAML file."""
    with open(path, "r") as f:
        loaded_cfg = yaml.safe_load(f)

    cameras = _load_camera_configs(loaded_cfg.get("cameras", {}))

    server_cfg = ServerConfig(
        cameras=cameras,
        close_bbox_diagonal_px=loaded_cfg["close_bbox_diagonal_px"],
        http_port=loaded_cfg["http_port"],
        recording_lifetime_s=loaded_cfg["recording_lifetime_s"],
        status_frequency_hz=loaded_cfg["status_frequency_hz"],
    )
    if len(server_cfg.cameras) == 0:
        raise ValueError("Configuration must specify at least one camera.")
    return server_cfg


def save(config: ServerConfig, path: pathlib.Path) -> None:
    """Saves the server configuration to a YAML file."""
    data = dataclasses.asdict(config)

    # YAML doesn't have built in tuple support so we convert it here.
    for cam_cfg in data["cameras"].values():
        cam_cfg["resolution"] = list(cam_cfg["resolution"])

    with open(path, "w") as f:
        yaml.safe_dump(data, f)
