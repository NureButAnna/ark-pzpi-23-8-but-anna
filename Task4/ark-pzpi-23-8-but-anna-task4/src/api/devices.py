from datetime import datetime
from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.models.notifications import Notifications
from src.models.container_sites import ContainerSite
from src.models.containers import Containers
from src.api.auth import get_current_user
from src.database import get_db
from src.models.devices import Devices
from src.schemas.devices import DeviceResponse, DeviceCreate, DeviceTelemetry
from src.schemas.devices import DeviceTelemetryView, DeviceUpdate


router = APIRouter(
    prefix="/devices",
    tags=["Devices ⚡"]
)


@router.post("/", response_model=DeviceResponse)
def create_device(
    data: DeviceCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("admin", "organization"):
        raise HTTPException(403, "Access denied")

    exists = db.query(Devices).filter(
        Devices.serial_number == data.serial_number
    ).first()

    if exists:
        raise HTTPException(409, "Device already exists")

    device = Devices(
        device_name=data.device_name,
        serial_number=data.serial_number,
        device_type=data.device_type,
        battery_level=data.battery_level,
        status="active",
        container_id=data.container_id
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return device


@router.get("/", response_model=list[DeviceResponse])
def get_devices(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role == "admin":
        return db.query(Devices).all()

    if role == "organization":
        return (
            db.query(Devices)
            .join(Containers)
            .join(ContainerSite)
            .filter(ContainerSite.organization_id == entity.organization_id)
            .all()
        )

    raise HTTPException(403, "Access denied")


@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: int,
    data: DeviceUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    if role not in ("admin", "organization"):
        raise HTTPException(403, "Access denied")

    device = db.query(Devices).filter(
        Devices.device_id == device_id
    ).first()

    if not device:
        raise HTTPException(404, "Device not found")

    # перевірка доступу для організації
    if role == "organization":
        site = (
            db.query(ContainerSite)
            .join(Containers)
            .filter(Containers.container_id == device.container_id)
            .first()
        )

        if not site or site.organization_id != entity.organization_id:
            raise HTTPException(403, "Access denied")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(device, field, value)

    db.commit()
    db.refresh(device)

    return device


def check_fill_level(fill_level: float, container, db: Session):
    if fill_level >= 90:
        db.add(Notifications(
            message="Контейнер майже заповнений",
            message_type="WARNING",
            container_site_id=container.container_site_id
        ))


def check_tilt(tilted: bool, container, db: Session):
    if tilted:
        db.add(Notifications(
            message="Контейнер нахилений",
            message_type="CRITICAL",
            container_site_id=container.container_site_id
        ))


def check_temperature(temperature: float, container, db: Session):
    if temperature >= 60:
        db.add(Notifications(
            message=f"Критично висока температура в контейнері ({temperature} °C)",
            message_type="CRITICAL",
            container_site_id=container.container_site_id
        ))
    elif temperature >= 45:
        db.add(Notifications(
            message=f"Підвищена температура в контейнері ({temperature} °C)",
            message_type="WARNING",
            container_site_id=container.container_site_id
        ))


def check_battery(battery_level: int, device, db: Session):
    if battery_level <= 10:
        db.add(Notifications(
            message="Критично низький рівень заряду батареї пристрою",
            message_type="CRITICAL",
            container_site_id=device.container.container_site_id
        ))
    elif battery_level <= 20:
        db.add(Notifications(
            message="Низький рівень заряду батареї пристрою",
            message_type="WARNING",
            container_site_id=device.container.container_site_id
        ))


@router.post("/telemetry")
def receive_telemetry(
    data: DeviceTelemetry,
    db: Session = Depends(get_db)
):
    device = db.query(Devices).filter(
        Devices.serial_number == data.serial_number
    ).first()

    if not device:
        raise HTTPException(404, "Device not registered")

    if not device.container_id:
        raise HTTPException(409, "Device not bound to container")

    container = db.query(Containers).filter(
        Containers.container_id == device.container_id
    ).first()

    fill_level = max(0, min(data.fill_level, 100))
    temperature = max(-40, min(data.temperature, 120))
    battery_level = max(0, min(data.battery_level, 100))

    device.last_signal = datetime.utcnow()
    device.battery_level = battery_level
    device.status = "active"

    container.fill_level = fill_level
    container.temperature = temperature
    container.tilted = data.tilted
    container.last_update = datetime.utcnow()

    check_fill_level(fill_level, container, db)
    check_tilt(data.tilted, container, db)
    check_temperature(temperature, container, db)
    check_battery(battery_level, device, db)

    db.commit()
    return {"status": "ok"}


@router.get(
    "/{device_id}/telemetry",
    response_model=DeviceTelemetryView
)
def get_device_telemetry(
    device_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    entity, role = current

    device = db.query(Devices).filter(
        Devices.device_id == device_id
    ).first()

    if not device:
        raise HTTPException(404, "Device not found")

    container = db.query(Containers).filter(
        Containers.container_id == device.container_id
    ).first()

    if role == "organization":
        site = db.query(ContainerSite).filter(
            ContainerSite.container_site_id == container.container_site_id
        ).first()

        if site.organization_id != entity.organization_id:
            raise HTTPException(403, "Access denied")

    if role not in ("admin", "organization"):
        raise HTTPException(403, "Access denied")

    return {
        "serial_number": device.serial_number,
        "battery_level": device.battery_level,
        "last_signal": device.last_signal,

        "fill_level": container.fill_level,
        "temperature": container.temperature,
        "tilted": container.tilted,
        "last_update": container.last_update
    }
