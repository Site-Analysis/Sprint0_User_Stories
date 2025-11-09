
## âš¡ Performance Test Results

**Test Configuration:**
- Location: Central London
- Bounding Box: 51.5,-0.1,51.51,-0.09
- Test Date: November 09, 2025 18:44:25
- Total Test Duration: 80.38 seconds
- Server: FastAPI + Uvicorn on localhost

### Overall Statistics
- **Average Response Time:** 2004.18 ms
- **Fastest Endpoint:** 1244.23 ms
- **Slowest Endpoint:** 3897.44 ms
- **Total Data Retrieved:** 2.32 MB
- **Total Elements:** 17048

### Detailed Endpoint Performance

| # | Endpoint | Response Time | Elements | Data Size | Elements/Sec |
|---|----------|--------------|----------|-----------|--------------|
| 1 | `motorway-junctions` | 1244.23 ms | 0 | 0.38 KB | 0 |
| 2 | `traffic-signals` | 1283.16 ms | 50 | 7.67 KB | 38.97 |
| 3 | `toll` | 1317.74 ms | 0 | 0.39 KB | 0 |
| 4 | `width` | 1346.15 ms | 143 | 15.68 KB | 106.24 |
| 5 | `turn-lanes` | 1430.53 ms | 46 | 6.9 KB | 32.15 |
| 6 | `access-restrictions` | 1433.47 ms | 214 | 19.47 KB | 149.34 |
| 7 | `railway-crossings` | 1445.1 ms | 0 | 0.38 KB | 0 |
| 8 | `lanes` | 1462.77 ms | 454 | 62.57 KB | 310.32 |
| 9 | `service-roads` | 1530.81 ms | 583 | 49.16 KB | 380.8 |
| 10 | `crosswalks` | 1567.9 ms | 366 | 47.6 KB | 233.42 |
| 11 | `oneway` | 1606.63 ms | 591 | 75.84 KB | 367.77 |
| 12 | `roundabouts` | 1645.93 ms | 0 | 0.39 KB | 0 |
| 13 | `stop-yield` | 1665.25 ms | 32 | 4.12 KB | 19.22 |
| 14 | `parking` | 1670.79 ms | 63 | 5.59 KB | 37.7 |
| 15 | `bicycle-infrastructure` | 1726.54 ms | 377 | 41.45 KB | 218.3 |
| 16 | `bus-stops` | 1742.79 ms | 24 | 9.91 KB | 13.77 |
| 17 | `vehicle-restrictions` | 1745.04 ms | 141 | 18.79 KB | 80.8 |
| 18 | `classification` | 1748.72 ms | 1441 | 158.82 KB | 823.9 |
| 19 | `street-names-multilingual` | 1963.84 ms | 1882 | 230.29 KB | 958.25 |
| 20 | `bridges-tunnels` | 2020.24 ms | 134 | 15.58 KB | 66.34 |
| 21 | `surface` | 2095.84 ms | 2795 | 314.56 KB | 1333.49 |
| 22 | `lighting` | 2107.83 ms | 2290 | 265.05 KB | 1086.34 |
| 23 | `condition` | 2148.34 ms | 3 | 0.75 KB | 1.4 |
| 24 | `turn-restrictions` | 2152.17 ms | 182 | 16.3 KB | 84.57 |
| 25 | `shoulders` | 2252.04 ms | 4 | 0.85 KB | 1.78 |
| 26 | `emergency-access` | 2413.41 ms | 12 | 2.04 KB | 4.97 |
| 27 | `speed-bumps` | 2543.33 ms | 44 | 6.75 KB | 17.3 |
| 28 | `names-references` | 2798.81 ms | 1882 | 230.29 KB | 672.38 |
| 29 | `speed-limits` | 3059 ms | 1373 | 177.76 KB | 448.84 |
| 30 | `sidewalks` | 3467.25 ms | 905 | 118.24 KB | 261.03 |
| 31 | `construction` | 3600.7 ms | 0 | 0.44 KB | 0 |
| 32 | `basic-network` | 3897.44 ms | 1017 | 472.53 KB | 260.97 |
