$bbox = "51.5,-0.1,51.51,-0.09"
$baseUrl = "http://127.0.0.1:8000/api/roads"

$endpoints = @(
    "basic-network",
    "classification",
    "surface",
    "lanes",
    "speed-limits",
    "oneway",
    "width",
    "traffic-signals",
    "stop-yield",
    "crosswalks",
    "lighting",
    "access-restrictions",
    "bridges-tunnels",
    "turn-restrictions",
    "parking",
    "sidewalks",
    "bicycle-infrastructure",
    "names-references",
    "condition",
    "toll",
    "motorway-junctions",
    "elevation",
    "bus-stops",
    "railway-crossings",
    "emergency-access",
    "construction",
    "turn-lanes",
    "vehicle-restrictions",
    "service-roads",
    "shoulders",
    "roundabouts",
    "speed-bumps",
    "street-names-multilingual"
)

$results = @()

Write-Host "`n" -NoNewline
Write-Host ("="*100) -ForegroundColor Cyan
Write-Host "PERFORMANCE TEST - All Endpoints" -ForegroundColor Cyan
Write-Host "Test Area: Central London | Bbox: $bbox" -ForegroundColor Cyan
Write-Host ("="*100) -ForegroundColor Cyan
Write-Host "`n"

$totalTime = [System.Diagnostics.Stopwatch]::StartNew()

foreach ($endpoint in $endpoints) {
    Write-Host ("{0,-35}" -f "Testing: $endpoint") -NoNewline -ForegroundColor White
    
    try {
        $url = "$baseUrl/$endpoint`?bbox=$bbox"
        
        # Measure response time
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 60
        $stopwatch.Stop()
        
        $json = $response.Content | ConvertFrom-Json
        $responseTimeMs = [math]::Round($stopwatch.Elapsed.TotalMilliseconds, 2)
        $responseTimeSec = [math]::Round($stopwatch.Elapsed.TotalSeconds, 3)
        
        $result = [PSCustomObject]@{
            Endpoint = $endpoint
            Status = $response.StatusCode
            ResponseTimeMs = $responseTimeMs
            ResponseTimeSec = $responseTimeSec
            Elements = $json.element_count
            DataSizeKB = [math]::Round($response.Content.Length / 1024, 2)
            ElementsPerSec = if($responseTimeSec -gt 0) { [math]::Round($json.element_count / $responseTimeSec, 2) } else { 0 }
        }
        
        $timeColor = if($responseTimeMs -lt 1000) { "Green" } elseif($responseTimeMs -lt 3000) { "Yellow" } else { "Red" }
        Write-Host (" {0,8} ms " -f $responseTimeMs) -NoNewline -ForegroundColor $timeColor
        Write-Host ("| {0,5} elements | {0,8} KB" -f $json.element_count, $result.DataSizeKB) -ForegroundColor Gray
        
    } catch {
        $result = [PSCustomObject]@{
            Endpoint = $endpoint
            Status = "ERROR"
            ResponseTimeMs = 0
            ResponseTimeSec = 0
            Elements = 0
            DataSizeKB = 0
            ElementsPerSec = 0
        }
        Write-Host " FAILED" -ForegroundColor Red
    }
    
    $results += $result
    Start-Sleep -Milliseconds 200
}

$totalTime.Stop()

Write-Host "`n"
Write-Host ("="*100) -ForegroundColor Cyan
Write-Host "TEST COMPLETE" -ForegroundColor Green
Write-Host ("="*100) -ForegroundColor Cyan
Write-Host "`n"

# Statistics
$avgTime = [math]::Round(($results | Where-Object {$_.Status -eq 200} | Measure-Object -Property ResponseTimeMs -Average).Average, 2)
$minTime = ($results | Where-Object {$_.Status -eq 200} | Measure-Object -Property ResponseTimeMs -Minimum).Minimum
$maxTime = ($results | Where-Object {$_.Status -eq 200} | Measure-Object -Property ResponseTimeMs -Maximum).Maximum
$totalElements = ($results | Measure-Object -Property Elements -Sum).Sum
$totalDataKB = [math]::Round(($results | Measure-Object -Property DataSizeKB -Sum).Sum, 2)
$totalDataMB = [math]::Round($totalDataKB / 1024, 2)

Write-Host "PERFORMANCE SUMMARY:" -ForegroundColor Cyan
Write-Host "  Total Test Duration:     $([math]::Round($totalTime.Elapsed.TotalSeconds, 2)) seconds" -ForegroundColor White
Write-Host "  Average Response Time:   $avgTime ms" -ForegroundColor White
Write-Host "  Fastest Endpoint:        $minTime ms" -ForegroundColor Green
Write-Host "  Slowest Endpoint:        $maxTime ms" -ForegroundColor Yellow
Write-Host "  Total Elements Retrieved: $totalElements" -ForegroundColor White
Write-Host "  Total Data Retrieved:    $totalDataMB MB ($totalDataKB KB)" -ForegroundColor White
Write-Host "`n"

# Sort by response time
Write-Host "ENDPOINTS RANKED BY SPEED (Fastest to Slowest):" -ForegroundColor Cyan
$results | Where-Object {$_.Status -eq 200} | Sort-Object ResponseTimeMs | Format-Table -AutoSize Endpoint, ResponseTimeMs, Elements, DataSizeKB

Write-Host "`n"
Write-Host "ENDPOINTS RANKED BY DATA VOLUME:" -ForegroundColor Cyan
$results | Where-Object {$_.Status -eq 200} | Sort-Object DataSizeKB -Descending | Select-Object -First 10 | Format-Table -AutoSize Endpoint, Elements, DataSizeKB, ResponseTimeMs

# Export detailed results
$results | Export-Csv -Path "endpoint_performance_test.csv" -NoTypeInformation
Write-Host "`nDetailed results saved to: endpoint_performance_test.csv" -ForegroundColor Green

# Create markdown table for README
$mdTable = @"

## ⚡ Performance Test Results

**Test Configuration:**
- Location: Central London
- Bounding Box: $bbox
- Test Date: $(Get-Date -Format "MMMM dd, yyyy HH:mm:ss")
- Total Test Duration: $([math]::Round($totalTime.Elapsed.TotalSeconds, 2)) seconds
- Server: FastAPI + Uvicorn on localhost

### Overall Statistics
- **Average Response Time:** $avgTime ms
- **Fastest Endpoint:** $minTime ms
- **Slowest Endpoint:** $maxTime ms
- **Total Data Retrieved:** $totalDataMB MB
- **Total Elements:** $totalElements

### Detailed Endpoint Performance

| # | Endpoint | Response Time | Elements | Data Size | Elements/Sec |
|---|----------|--------------|----------|-----------|--------------|
"@

$counter = 1
foreach ($r in ($results | Where-Object {$_.Status -eq 200} | Sort-Object ResponseTimeMs)) {
    $mdTable += "`n| $counter | ``$($r.Endpoint)`` | $($r.ResponseTimeMs) ms | $($r.Elements) | $($r.DataSizeKB) KB | $($r.ElementsPerSec) |"
    $counter++
}

$mdTable | Out-File -FilePath "performance_results.md" -Encoding UTF8
Write-Host "Markdown table saved to: performance_results.md" -ForegroundColor Green
Write-Host "`n"
