const API_BASE = "http://127.0.0.1:8000";

const map = L.map("map", { zoomControl: false, attributionControl: false }).setView([19.5, 96.0], 6);
L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png").addTo(map);
window.map = map;

const routeLayer = L.layerGroup().addTo(map);
const scanLayer = L.layerGroup().addTo(map);
const airportLayer = L.layerGroup().addTo(map);

let cities = {};
let planeMarker = null;
let animationFrame = null;

const terminal = document.getElementById("logicTerminal");
const startSelect = document.getElementById("startInput");
const goalSelect = document.getElementById("goalInput");
const computeBtn = document.getElementById("computeBtn");
const resetBtn = document.getElementById("resetBtn");
const centerMapBtn = document.getElementById("centerMapBtn");
const resultOverlay = document.getElementById("resultOverlay");
const nmVal = document.getElementById("nmVal");
const kmVal = document.getElementById("kmVal");

function delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

function log(msg, type = "info") {
    const div = document.createElement("div");
    div.className =
        "mb-1.5 leading-relaxed " +
        (type === "success"
            ? "text-emerald-400"
            : type === "error"
              ? "text-red-400"
              : "text-blue-300/50");
    div.innerHTML = `<span class="opacity-30">${new Date().toLocaleTimeString([], { hour12: false })}</span> > ${msg}`;
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}

function cleanupAnimatedObjects() {
    scanLayer.clearLayers();
    routeLayer.clearLayers();
    if (planeMarker) {
        map.removeLayer(planeMarker);
        planeMarker = null;
    }
    if (animationFrame) {
        cancelAnimationFrame(animationFrame);
        animationFrame = null;
    }
    resultOverlay.classList.add("hidden");
}

function animatePlane(start, end) {
    if (planeMarker) {
        map.removeLayer(planeMarker);
    }
    if (animationFrame) {
        cancelAnimationFrame(animationFrame);
    }

    const startTime = performance.now();
    const duration = 6000;
    const angle = (Math.atan2(end[1] - start[1], end[0] - start[0]) * 180) / Math.PI;

    planeMarker = L.marker(start, {
        icon: L.divIcon({
            className: "plane-container",
            html: `<i class="fas fa-plane plane-icon" style="transform: rotate(${angle - 45}deg);"></i>`,
            iconSize: [24, 24],
            iconAnchor: [12, 12],
        }),
    }).addTo(map);

    function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);

        const currentLat = start[0] + (end[0] - start[0]) * progress;
        const currentLng = start[1] + (end[1] - start[1]) * progress;
        if (planeMarker) {
            planeMarker.setLatLng([currentLat, currentLng]);
        }

        if (progress < 1) {
            animationFrame = requestAnimationFrame(step);
        } else {
            setTimeout(() => {
                if (planeMarker && map.hasLayer(planeMarker)) {
                    animatePlane(start, end);
                }
            }, 2000);
        }
    }

    animationFrame = requestAnimationFrame(step);
}

async function renderScan(scanEdges) {
    for (const [from, to] of scanEdges) {
        if (!cities[from] || !cities[to]) {
            continue;
        }
        L.polyline([cities[from].pos, cities[to].pos], {
            color: "#ef4444",
            weight: 1.5,
            opacity: 0.5,
            className: "path-scan-active",
        }).addTo(scanLayer);
        await delay(120);
    }
}

async function runAnalysis() {
    const start = startSelect.value;
    const goal = goalSelect.value;

    if (!start || !goal) {
        log("Select both origin and destination", "error");
        return;
    }
    if (start === goal) {
        log("Origin and destination must differ", "error");
        return;
    }

    computeBtn.disabled = true;
    cleanupAnimatedObjects();

    log(`Initiating pathfinding: ${start} to ${goal}`);
    map.flyTo(cities[start].pos, 7, { duration: 1.2 });
    await delay(1300);

    try {
        const response = await fetch(`${API_BASE}/api/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ origin: start, destination: goal }),
        });
        const payload = await response.json();
        if (!response.ok) {
            throw new Error(payload.detail || "Analysis failed.");
        }

        await renderScan(payload.scan_edges || []);
        await delay(300);
        scanLayer.clearLayers();

        const routeCoords = payload.route_coords || [];
        if (!routeCoords.length) {
            throw new Error("No route coordinates returned.");
        }

        const roadLine = L.polyline(routeCoords, {
            color: "#10b981",
            weight: 5,
            opacity: 0.9,
            className: "road-route",
        }).addTo(routeLayer);

        L.polyline([payload.start_pos, payload.goal_pos], {
            color: "#3b82f6",
            weight: 2,
            opacity: 0.6,
            className: "air-route",
        }).addTo(routeLayer);

        nmVal.innerText = `${payload.air_distance_nm.toFixed(1)} NM`;
        kmVal.innerText = `${payload.road_distance_km.toFixed(1)} KM`;
        resultOverlay.classList.remove("hidden");

        log(`Path Found: ${payload.route_path.join(" → ")}`, "success");
        log(`Total Distance: ${payload.road_distance_km.toFixed(1)} KM`, "success");

        map.flyToBounds(roadLine.getBounds(), { padding: [100, 100], duration: 1.5 });
        animatePlane(payload.start_pos, payload.goal_pos);
    } catch (error) {
        log(error.message || "No viable path found within current network", "error");
    } finally {
        computeBtn.disabled = false;
    }
}

function clearSystemData() {
    cleanupAnimatedObjects();
    startSelect.selectedIndex = 0;
    goalSelect.selectedIndex = 0;
    terminal.innerHTML = '<div class="text-blue-500 font-bold mb-2">> System Reset...</div>';
    map.flyTo([19.5, 96.0], 6, { duration: 1.2 });
}

async function loadCities() {
    const response = await fetch(`${API_BASE}/api/cities`);
    const payload = await response.json();
    if (!response.ok) {
        throw new Error(payload.detail || "Failed to load cities.");
    }
    cities = payload.cities || {};
    const sortedNames = Object.keys(cities).sort();

    sortedNames.forEach((name) => {
        startSelect.add(new Option(name, name));
        goalSelect.add(new Option(name, name));
        L.circleMarker(cities[name].pos, {
            radius: 3,
            fillColor: "#3b82f6",
            color: "#fff",
            weight: 1,
            opacity: 0.8,
            fillOpacity: 0.6,
        })
            .bindTooltip(name, { className: "bg-black text-white border-0 text-[10px] rounded" })
            .addTo(airportLayer);
    });
}

async function bootstrap() {
    computeBtn.addEventListener("click", runAnalysis);
    resetBtn.addEventListener("click", clearSystemData);
    centerMapBtn.addEventListener("click", () => map.flyTo([19.5, 96.0], 6));
    window.runAnalysis = runAnalysis;
    window.clearSystemData = clearSystemData;

    try {
        await loadCities();
        log("System Ready. City network loaded.", "success");
    } catch (error) {
        log(error.message || "Backend is unreachable.", "error");
    }
}

bootstrap();
