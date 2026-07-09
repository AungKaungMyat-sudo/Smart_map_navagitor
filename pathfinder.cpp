#include <cmath>
#include <iostream>
#include <limits>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

struct City {
    double lat;
    double lng;
    std::vector<std::string> neighbors;
};

static const std::unordered_map<std::string, City> CITIES = {
    {"Yangon", {16.8661, 96.1951, {"Naypyidaw", "Bago", "Pathein", "Mawlamyine", "Henzada"}}},
    {"Bago", {17.3304, 96.4814, {"Yangon", "Naypyidaw", "Hpa-An", "Pyay", "Taungoo"}}},
    {"Hpa-An", {16.8904, 97.6366, {"Bago", "Mawlamyine", "Myawaddy"}}},
    {"Mawlamyine", {16.4870, 97.6330, {"Yangon", "Dawei", "Hpa-An"}}},
    {"Dawei", {14.0828, 98.1940, {"Mawlamyine", "Myeik"}}},
    {"Myeik", {12.4381, 98.5996, {"Dawei", "Kawthaung"}}},
    {"Kawthaung", {9.9833, 98.5500, {"Myeik"}}},
    {"Myawaddy", {16.6833, 98.5167, {"Hpa-An"}}},
    {"Pathein", {16.7754, 94.7381, {"Henzada", "Yangon", "Ngwesaung", "Myaungmya"}}},
    {"Ngwesaung", {16.8631, 94.3833, {"Pathein"}}},
    {"Myaungmya", {16.5833, 94.9167, {"Pathein", "Labutta"}}},
    {"Labutta", {16.1500, 94.7667, {"Myaungmya"}}},
    {"Henzada", {17.6500, 95.4500, {"Pathein", "Kyangin", "Yangon", "Pyay"}}},
    {"Kyangin", {18.3300, 95.2400, {"Pyay", "Henzada", "Thandwe"}}},
    {"Naypyidaw", {19.7633, 96.0785, {"Yangon", "Mandalay", "Pyay", "Bago", "Heho", "Taungoo", "Magway", "Yamethin"}}},
    {"Taungoo", {18.9333, 96.4333, {"Bago", "Naypyidaw", "Loikaw"}}},
    {"Pyay", {18.8239, 95.2267, {"Naypyidaw", "Kyangin", "Bago", "Thandwe", "Henzada", "Magway"}}},
    {"Magway", {20.1500, 94.9167, {"Naypyidaw", "Pyay", "Nyaung-U", "Minbu", "Taungdwingyi"}}},
    {"Minbu", {20.1833, 94.8833, {"Magway", "Ann"}}},
    {"Taungdwingyi", {20.0167, 95.5333, {"Magway", "Yamethin"}}},
    {"Yamethin", {20.4333, 96.1500, {"Naypyidaw", "Taungdwingyi", "Meiktila"}}},
    {"Meiktila", {20.8833, 95.8667, {"Yamethin", "Mandalay", "Nyaung-U", "Myingyan"}}},
    {"Mandalay", {21.9588, 96.0891, {"Naypyidaw", "Heho", "Myitkyina", "Nyaung-U", "Lashio", "Sagaing", "Pyin Oo Lwin", "Meiktila"}}},
    {"Pyin Oo Lwin", {22.0333, 96.4667, {"Mandalay", "Lashio"}}},
    {"Sagaing", {21.8787, 95.9791, {"Mandalay", "Monywa", "Shwebo"}}},
    {"Monywa", {22.1167, 95.1333, {"Sagaing", "Shwebo", "Pakokku", "Kalay"}}},
    {"Shwebo", {22.5667, 95.7000, {"Sagaing", "Monywa", "Katha"}}},
    {"Nyaung-U", {21.1786, 94.9100, {"Mandalay", "Pyay", "Magway", "Pakokku", "Meiktila"}}},
    {"Pakokku", {21.3333, 95.0833, {"Nyaung-U", "Monywa", "Mindat"}}},
    {"Myingyan", {21.4667, 95.3833, {"Meiktila", "Mandalay"}}},
    {"Heho", {20.7454, 96.7972, {"Naypyidaw", "Taunggyi", "Inle", "Mandalay"}}},
    {"Taunggyi", {20.7833, 97.0333, {"Heho", "Loikaw", "Kengtung"}}},
    {"Inle", {20.5000, 96.9000, {"Heho"}}},
    {"Loikaw", {19.6667, 97.2167, {"Taunggyi", "Taungoo"}}},
    {"Lashio", {22.9749, 97.7511, {"Pyin Oo Lwin", "Muse"}}},
    {"Muse", {23.9833, 97.9000, {"Lashio"}}},
    {"Kengtung", {21.2833, 99.6000, {"Taunggyi", "Tachileik"}}},
    {"Tachileik", {20.4431, 99.8814, {"Kengtung"}}},
    {"Sittwe", {20.1332, 92.8732, {"Thandwe", "Nyaung-U", "Mrauk-U"}}},
    {"Mrauk-U", {20.6000, 93.2000, {"Sittwe", "Ann"}}},
    {"Ann", {19.7833, 94.0333, {"Mrauk-U", "Minbu"}}},
    {"Thandwe", {18.4633, 94.2989, {"Sittwe", "Pyay", "Kyangin", "Gwa"}}},
    {"Gwa", {17.5833, 94.5833, {"Thandwe"}}},
    {"Mindat", {21.3667, 93.9833, {"Pakokku", "Hakha"}}},
    {"Hakha", {22.6422, 93.6067, {"Mindat", "Falam"}}},
    {"Falam", {22.9167, 93.6833, {"Hakha", "Kalay"}}},
    {"Myitkyina", {25.3831, 97.3964, {"Mandalay", "Bhamo", "Putao"}}},
    {"Bhamo", {24.2667, 97.2333, {"Myitkyina", "Katha"}}},
    {"Katha", {24.1833, 96.3333, {"Bhamo", "Shwebo"}}},
    {"Putao", {27.3333, 97.4000, {"Myitkyina"}}},
    {"Kalay", {23.2000, 94.0500, {"Falam", "Monywa", "Tamu"}}},
    {"Tamu", {24.2167, 94.3000, {"Kalay"}}},
};

constexpr double PI = 3.14159265358979323846;
constexpr double EARTH_RADIUS_KM = 6371.0;

double toRadians(double degrees) {
    return degrees * PI / 180.0;
}

double haversineKm(const City& a, const City& b) {
    const double dLat = toRadians(b.lat - a.lat);
    const double dLng = toRadians(b.lng - a.lng);
    const double lat1 = toRadians(a.lat);
    const double lat2 = toRadians(b.lat);

    const double h = std::sin(dLat / 2) * std::sin(dLat / 2) +
                     std::cos(lat1) * std::cos(lat2) * std::sin(dLng / 2) * std::sin(dLng / 2);
    return 2 * EARTH_RADIUS_KM * std::asin(std::sqrt(h));
}

std::string escapeJson(const std::string& input) {
    std::ostringstream out;
    for (char c : input) {
        if (c == '"' || c == '\\') {
            out << '\\' << c;
        } else {
            out << c;
        }
    }
    return out.str();
}

int main(int argc, char* argv[]) {
    std::ios::sync_with_stdio(false);

    std::string start;
    std::string goal;

    if (argc >= 3) {
        start = argv[1];
        goal = argv[2];
    } else {
        if (!(std::cin >> start >> goal)) {
            std::cout << "{\"error\":\"Expected start and goal city names.\"}\n";
            return 1;
        }
    }

    if (!CITIES.count(start) || !CITIES.count(goal)) {
        std::cout << "{\"error\":\"Unknown origin or destination.\"}\n";
        return 1;
    }

    if (start == goal) {
        std::cout << "{\"path\":[\"" << escapeJson(start) << "\"],\"distance_km\":0.0}\n";
        return 0;
    }

    std::unordered_map<std::string, double> dist;
    std::unordered_map<std::string, std::string> prev;
    for (const auto& entry : CITIES) {
        dist[entry.first] = std::numeric_limits<double>::infinity();
    }
    dist[start] = 0.0;

    using Node = std::pair<double, std::string>;
    std::priority_queue<Node, std::vector<Node>, std::greater<Node>> pq;
    pq.push({0.0, start});

    while (!pq.empty()) {
        auto [currentDist, city] = pq.top();
        pq.pop();

        if (currentDist > dist[city]) {
            continue;
        }
        if (city == goal) {
            break;
        }

        const City& current = CITIES.at(city);
        for (const std::string& neighborName : current.neighbors) {
            if (!CITIES.count(neighborName)) {
                continue;
            }
            const City& neighbor = CITIES.at(neighborName);
            const double edge = haversineKm(current, neighbor);
            const double nextDist = currentDist + edge;
            if (nextDist < dist[neighborName]) {
                dist[neighborName] = nextDist;
                prev[neighborName] = city;
                pq.push({nextDist, neighborName});
            }
        }
    }

    if (!std::isfinite(dist[goal])) {
        std::cout << "{\"error\":\"No path found.\"}\n";
        return 1;
    }

    std::vector<std::string> path;
    for (std::string at = goal; !at.empty(); at = prev.count(at) ? prev[at] : "") {
        path.push_back(at);
        if (at == start) {
            break;
        }
    }
    std::reverse(path.begin(), path.end());

    if (path.empty() || path.front() != start || path.back() != goal) {
        std::cout << "{\"error\":\"Failed to reconstruct path.\"}\n";
        return 1;
    }

    std::ostringstream json;
    json << "{\"path\":[";
    for (size_t i = 0; i < path.size(); ++i) {
        if (i > 0) {
            json << ',';
        }
        json << "\"" << escapeJson(path[i]) << "\"";
    }
    json << "],\"distance_km\":" << dist[goal] << "}\n";

    std::cout << json.str();
    return 0;
}
