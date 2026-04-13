# Coordinated Drone–USV Protocol

## Overview

This change adds a **thin coordination layer** between the existing USV control path and the auxiliary drone sensing path.

- **USV remains authoritative** for arming, mode changes, mission upload, and mission start.
- **Drone acts only as an auxiliary sensing platform** with forward-offset/follow behavior managed outside the USV mission core.
- **GCS coordinates startup and relays semantic data only**.
- **USV mission/control flow in `Vehicle/ArdupilotConnection.py` remains intact**; additive helpers wrap the existing `DEBUG_VECT` transport for semantic relay.

## Topology

```text
Drone MAVLink (STATUSTEXT)
    -> DroneConnectionThread
    -> ConnectionManager / StartupCoordinator
    -> MainWindow + DroneStatusWidget
    -> ArdupilotConnectionThread.send_semantic_event()
    -> USV companion MAVLink DEBUG_VECT

MainWindow
    -> ArdupilotConnectionThread
    -> existing USV connection / mission / arm / start flow
```

## Startup Model

Coordinator states:

1. `idle`
2. `connecting-usv`
3. `connecting-drone`
4. `ready`
5. `degraded`

Rules:

- The coordinator treats the **USV link as primary**.
- `ready` means both links are active.
- `degraded` means exactly one link is available.
- Disconnecting both links returns the coordinator to `idle`.

## Message Table

| Message | Direction | Producer | Consumer | Purpose | Encoding / Notes |
|---|---|---|---|---|---|
| `FOLLOW_REFERENCE` | Drone/GCS internal contract | Drone autonomy layer | GCS / optional USV consumer | Forward-offset follow reference for auxiliary sensing | Documented contract only in this change; not routed into USV mission authority |
| `OBSTACLE_REPORT` | Drone -> GCS -> USV | Drone `STATUSTEXT` / GCS relay | ConnectionManager / USV companion | Report sensed obstacle semantics | Ingest prefixes: `OBSTACLE:` or `OBSTACLE_REPORT:`; relay as `DEBUG_VECT(name="OBSTACLE")` |
| `MISSION_TARGET` | Drone or operator -> GCS -> USV | Drone `STATUSTEXT` or operator workflow | ConnectionManager / USV companion | Report semantic mission target candidate | Legacy `TARGET:COLOR:LAT:LON` remains accepted; normalized to `MISSION_TARGET` |
| `DRONE_PROTOCOL_STATE` | Internal UI/state | StartupCoordinator | MainWindow / DroneStatusWidget | Show drone-side coordination state | Values such as `idle`, `connecting`, `ready`, `waiting-link`, `stopped` |
| `USV_PROTOCOL_STATE` | Internal UI/state | StartupCoordinator | MainWindow / DroneStatusWidget | Show USV-side coordination state | Values such as `idle`, `connecting`, `ready`, `waiting-link`, `stopped` |
| Coordinated start | GCS internal orchestration | ConnectionManager | USV thread, then drone thread | Start links in USV-first order | `connect_all(usv_port, usv_baud, drone_port, drone_baud)` |
| Coordinated stop | GCS internal orchestration | ConnectionManager | Drone thread + coordinator | Safe shutdown of auxiliary path | Does not rewrite existing USV stop semantics |

## Ingest Schemas

### Legacy target ingest

```text
TARGET:COLOR:LAT:LON
```

### Normalized target ingest

```text
MISSION_TARGET:COLOR:LAT:LON[:CONFIDENCE]
```

### Obstacle ingest

```text
OBSTACLE:TYPE:LAT:LON[:CONFIDENCE]
OBSTACLE_REPORT:TYPE:LAT:LON[:CONFIDENCE]
```

## Normalized Event Schema

### Mission target

```python
{
  "id": str,
  "event_type": "MISSION_TARGET",
  "color": "RED" | "GREEN" | "BLACK",
  "lat": float,
  "lon": float,
  "source": "drone",
  "confidence": float,
  "timestamp": float,
  "raw_text": str,
}
```

### Obstacle report

```python
{
  "id": str,
  "event_type": "OBSTACLE_REPORT",
  "obstacle_type": str,
  "lat": float,
  "lon": float,
  "source": "drone",
  "confidence": float,
  "timestamp": float,
  "raw_text": str,
}
```

## Relay Schema

The GCS relays semantic events to the USV companion using `DEBUG_VECT`:

| Semantic event | `DEBUG_VECT.name` | `x` | `y` | `z` |
|---|---|---|---|---|
| `MISSION_TARGET` | `TARGET` | latitude | longitude | semantic color id |
| `OBSTACLE_REPORT` | `OBSTACLE` | latitude | longitude | semantic obstacle id |

### Current IDs

- Target colors: `RED=1`, `GREEN=2`, `BLACK=3` (`BLUE` is accepted as an alias and normalized to `BLACK`)
- Obstacles: `BUOY=101`, `ROCK=102`, `VESSEL=103`, `DEBRIS=104`, default `UNKNOWN=100`

## Color Normalization

Competition documentation refers to the Parkour-3 target as **BLACK**, while some older GCS/drone messages used **BLUE**.

To reduce risk:

- legacy `TARGET:BLUE:...` messages are still accepted,
- GCS normalizes them to `BLACK` in semantic events,
- relay encoding maps both `BLUE` and `BLACK` to the same semantic id.

This keeps backward compatibility at ingest while aligning the internal protocol with competition semantics.

## Failure Modes

- **Drone link loss** -> coordinator becomes `degraded`; USV flow remains operational.
- **USV link loss** -> coordinator becomes `degraded`; semantic relay is rejected.
- **Duplicate detections** -> suppressed inside `ConnectionManager` by type/color-or-obstacle + small distance/time window.
- **Low-confidence / malformed detections** -> currently validated for coordinates; confidence is preserved for policy/UI and may be tightened later.

## Operator Workflow

1. Connect the USV using the existing GCS flow.
2. Connect the drone link.
3. Watch coordinator/protocol state in the drone status panel.
4. Drone semantic events appear in UI and are relayed through coordinator policy.
5. USV mission start/stop remains driven by the existing authoritative USV controls.
