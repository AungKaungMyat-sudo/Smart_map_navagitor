import json
import math
import os
import shutil
import subprocess
from collections import deque
from pathlib import Path
from typing import Dict, List, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(title="Smart Map Navigator API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


CITIES: Dict[str, Dict[str, List]] = {
    "Yangon": {"pos": [16.8661, 96.1951], "neighbors": ["Naypyidaw", "Bago", "Pathein", "Mawlamyine", "Henzada"]},
    "Bago": {"pos": [17.3304, 96.4814], "neighbors": ["Yangon", "Naypyidaw", "Hpa-An", "Pyay", "Taungoo"]},
    "Hpa-An": {"pos": [16.8904, 97.6366], "neighbors": ["Bago", "Mawlamyine", "Myawaddy"]},
    "Mawlamyine": {"pos": [16.4870, 97.6330], "neighbors": ["Yangon", "Dawei", "Hpa-An"]},
    "Dawei": {"pos": [14.0828, 98.1940], "neighbors": ["Mawlamyine", "Myeik"]},
    "Myeik": {"pos": [12.4381, 98.5996], "neighbors": ["Dawei", "Kawthaung"]},
    "Kawthaung": {"pos": [9.9833, 98.5500], "neighbors": ["Myeik"]},
    "Myawaddy": {"pos": [16.6833, 98.5167], "neighbors": ["Hpa-An"]},
    "Pathein": {"pos": [16.7754, 94.7381], "neighbors": ["Henzada", "Yangon", "Ngwesaung", "Myaungmya"]},
    "Ngwesaung": {"pos": [16.8631, 94.3833], "neighbors": ["Pathein"]},
    "Myaungmya": {"pos": [16.5833, 94.9167], "neighbors": ["Pathein", "Labutta"]},
    "Labutta": {"pos": [16.1500, 94.7667], "neighbors": ["Myaungmya"]},
    "Henzada": {"pos": [17.6500, 95.4500], "neighbors": ["Pathein", "Kyangin", "Yangon", "Pyay"]},
    "Kyangin": {"pos": [18.3300, 95.2400], "neighbors": ["Pyay", "Henzada", "Thandwe"]},
    "Naypyidaw": {"pos": [19.7633, 96.0785], "neighbors": ["Yangon", "Mandalay", "Pyay", "Bago", "Heho", "Taungoo", "Magway", "Yamethin"]},
    "Taungoo": {"pos": [18.9333, 96.4333], "neighbors": ["Bago", "Naypyidaw", "Loikaw"]},
    "Pyay": {"pos": [18.8239, 95.2267], "neighbors": ["Naypyidaw", "Kyangin", "Bago", "Thandwe", "Henzada", "Magway"]},
    "Magway": {"pos": [20.1500, 94.9167], "neighbors": ["Naypyidaw", "Pyay", "Nyaung-U", "Minbu", "Taungdwingyi"]},
    "Minbu": {"pos": [20.1833, 94.8833], "neighbors": ["Magway", "Ann"]},
    "Taungdwingyi": {"pos": [20.0167, 95.5333], "neighbors": ["Magway", "Yamethin"]},
    "Yamethin": {"pos": [20.4333, 96.1500], "neighbors": ["Naypyidaw", "Taungdwingyi", "Meiktila"]},
    "Meiktila": {"pos": [20.8833, 95.8667], "neighbors": ["Yamethin", "Mandalay", "Nyaung-U", "Myingyan"]},
    "Mandalay": {"pos": [21.9588, 96.0891], "neighbors": ["Naypyidaw", "Heho", "Myitkyina", "Nyaung-U", "Lashio", "Sagaing", "Pyin Oo Lwin", "Meiktila"]},
    "Pyin Oo Lwin": {"pos": [22.0333, 96.4667], "neighbors": ["Mandalay", "Lashio"]},
    "Sagaing": {"pos": [21.8787, 95.9791], "neighbors": ["Mandalay", "Monywa", "Shwebo"]},
    "Monywa": {"pos": [22.1167, 95.1333], "neighbors": ["Sagaing", "Shwebo", "Pakokku", "Kalay"]},
    "Shwebo": {"pos": [22.5667, 95.7000], "neighbors": ["Sagaing", "Monywa", "Katha"]},
    "Nyaung-U": {"pos": [21.1786, 94.9100], "neighbors": ["Mandalay", "Pyay", "Magway", "Pakokku", "Meiktila"]},
    "Pakokku": {"pos": [21.3333, 95.0833], "neighbors": ["Nyaung-U", "Monywa", "Mindat"]},
    "Myingyan": {"pos": [21.4667, 95.3833], "neighbors": ["Meiktila", "Mandalay"]},
    "Heho": {"pos": [20.7454, 96.7972], "neighbors": ["Naypyidaw", "Taunggyi", "Inle", "Mandalay"]},
    "Taunggyi": {"pos": [20.7833, 97.0333], "neighbors": ["Heho", "Loikaw", "Kengtung"]},
    "Inle": {"pos": [20.5000, 96.9000], "neighbors": ["Heho"]},
    "Loikaw": {"pos": [19.6667, 97.2167], "neighbors": ["Taunggyi", "Taungoo"]},
    "Lashio": {"pos": [22.9749, 97.7511], "neighbors": ["Pyin Oo Lwin", "Muse"]},
    "Muse": {"pos": [23.9833, 97.9000], "neighbors": ["Lashio"]},
    "Kengtung": {"pos": [21.2833, 99.6000], "neighbors": ["Taunggyi", "Tachileik"]},
    "Tachileik": {"pos": [20.4431, 99.8814], "neighbors": ["Kengtung"]},
    "Sittwe": {"pos": [20.1332, 92.8732], "neighbors": ["Thandwe", "Nyaung-U", "Mrauk-U"]},
    "Mrauk-U": {"pos": [20.6000, 93.2000], "neighbors": ["Sittwe", "Ann"]},
    "Ann": {"pos": [19.7833, 94.0333], "neighbors": ["Mrauk-U", "Minbu"]},
    "Thandwe": {"pos": [18.4633, 94.2989], "neighbors": ["Sittwe", "Pyay", "Kyangin", "Gwa"]},
    "Gwa": {"pos": [17.5833, 94.5833], "neighbors": ["Thandwe"]},
    "Mindat": {"pos": [21.3667, 93.9833], "neighbors": ["Pakokku", "Hakha"]},
    "Hakha": {"pos": [22.6422, 93.6067], "neighbors": ["Mindat", "Falam"]},
    "Falam": {"pos": [22.9167, 93.6833], "neighbors": ["Hakha", "Kalay"]},
    "Myitkyina": {"pos": [25.3831, 97.3964], "neighbors": ["Mandalay", "Bhamo", "Putao"]},
    "Bhamo": {"pos": [24.2667, 97.2333], "neighbors": ["Myitkyina", "Katha"]},
    "Katha": {"pos": [24.1833, 96.3333], "neighbors": ["Bhamo", "Shwebo"]},
    "Putao": {"pos": [27.3333, 97.4000], "neighbors": ["Myitkyina"]},
    "Kalay": {"pos": [23.2000, 94.0500], "neighbors": ["Falam", "Monywa", "Tamu"]},
    "Tamu": {"pos": [24.2167, 94.3000], "neighbors": ["Kalay"]},
}


class AnalyzeRequest(BaseModel):
    origin: str
    destination: str


def haversine_km(a: List[float], b: List[float]) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def bfs_scan_edges(start: str, goal: str) -> List[List[str]]:
    visited = {start}
    queue = deque([start])
    edges: List[List[str]] = []

    while queue:
        city = queue.popleft()
        for neighbor in CITIES[city]["neighbors"]:
            if neighbor in visited:
                continue
            visited.add(neighbor)
            edges.append([city, neighbor])
            if neighbor == goal:
                return edges
            queue.append(neighbor)
    return edges


def compile_pathfinder_if_needed(binary_path: Path, source_path: Path) -> None:
    compiler = shutil.which("g++")
    if compiler is None:
        raise HTTPException(status_code=500, detail="g++ compiler not found. Install MinGW or a C++ compiler.")

    if binary_path.exists() and binary_path.stat().st_mtime >= source_path.stat().st_mtime:
        return

    result = subprocess.run(
        [compiler, str(source_path), "-O2", "-std=c++17", "-o", str(binary_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compile pathfinder.cpp: {result.stderr.strip() or result.stdout.strip()}",
        )


def run_pathfinder(origin: str, destination: str) -> Dict:
    root = Path(__file__).resolve().parent
    source_path = root / "pathfinder.cpp"
    binary_name = "pathfinder.exe" if os.name == "nt" else "pathfinder"
    binary_path = root / binary_name

    if not source_path.exists():
        raise HTTPException(status_code=500, detail="pathfinder.cpp not found.")

    compile_pathfinder_if_needed(binary_path, source_path)

    result = subprocess.run(
        [str(binary_path), origin, destination],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = (result.stdout or "").strip()
    if not payload:
        raise HTTPException(status_code=500, detail=f"Pathfinder failed: {result.stderr.strip()}")

    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Invalid pathfinder response: {payload}") from exc

    if result.returncode != 0 or "error" in parsed:
        raise HTTPException(status_code=400, detail=parsed.get("error", "No valid path found."))

    return parsed


@app.get("/api/cities")
def get_cities() -> Dict[str, Dict[str, List[float]]]:
    return {"cities": {name: {"pos": details["pos"]} for name, details in CITIES.items()}}


@app.post("/api/analyze")
def analyze_route(req: AnalyzeRequest) -> Dict:
    origin = req.origin.strip()
    destination = req.destination.strip()

    if origin not in CITIES or destination not in CITIES:
        raise HTTPException(status_code=400, detail="Unknown origin or destination.")
    if origin == destination:
        raise HTTPException(status_code=400, detail="Origin and destination must differ.")

    path_output = run_pathfinder(origin, destination)
    route_path = path_output["path"]
    road_distance_km = round(float(path_output["distance_km"]), 1)
    air_distance_km = haversine_km(CITIES[origin]["pos"], CITIES[destination]["pos"])
    air_distance_nm = round(air_distance_km * 0.539957, 1)
    scan_edges = bfs_scan_edges(origin, destination)

    return {
        "route_path": route_path,
        "road_distance_km": road_distance_km,
        "air_distance_nm": air_distance_nm,
        "scan_edges": scan_edges,
        "start_pos": CITIES[origin]["pos"],
        "goal_pos": CITIES[destination]["pos"],
        "route_coords": [CITIES[name]["pos"] for name in route_path],
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
