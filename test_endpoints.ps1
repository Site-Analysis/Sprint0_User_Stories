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

Write-Host "Testing all endpoints with bbox: $bbox" -ForegroundColor Cyan
Write-Host ("="*80) -ForegroundColor Cyan

foreach ($endpoint in $endpoints) {
    Write-Host "Testing: $endpoint..." -NoNewline
    try {
        $url = "$baseUrl/$endpoint`?bbox=$bbox"
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 60
        $json = $response.Content | ConvertFrom-Json
        
        $result = [PSCustomObject]@{
            Endpoint = $endpoint
            Status = $response.StatusCode
            Elements = $json.element_count
            DataSizeKB = [math]::Round($response.Content.Length / 1024, 2)
        }
        
        Write-Host " OK ($($json.element_count) elements, $($result.DataSizeKB) KB)" -ForegroundColor Green
        
    } catch {
        $result = [PSCustomObject]@{
            Endpoint = $endpoint
            Status = "ERROR"
            Elements = 0
            DataSizeKB = 0
        }
        Write-Host " FAILED" -ForegroundColor Red
    }
    
    $results += $result
    Start-Sleep -Milliseconds 500
}

Write-Host "`n" -NoNewline
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Cyan
$results | Format-Table -AutoSize

# Export to CSV
$results | Export-Csv -Path "endpoint_test_results.csv" -NoTypeInformation
Write-Host "`nResults saved to: endpoint_test_results.csv" -ForegroundColor Green
