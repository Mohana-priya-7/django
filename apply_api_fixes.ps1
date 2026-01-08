$ErrorActionPreference = 'Stop'
$path = 'c:\Users\admin\Desktop\storfrontpro\products\views.py'

if (-not (Test-Path $path)) {
    throw "File not found: $path"
}

$content = Get-Content -Raw $path

# 1) expensive(): replace the min_price line with validated block
$pattern1 = "^\s*min_price = request\.query_params\.get\(''min_price'', 50000\)\s*$"
$replacement1 = @'
        min_price = request.query_params.get('min_price', 50000)
        try:
            min_price_value = float(min_price)
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid min_price. Please provide a numeric value."},
                status=status.HTTP_400_BAD_REQUEST
            )
'@
$content = [regex]::Replace($content, $pattern1, $replacement1, [System.Text.RegularExpressions.RegexOptions]::Multiline)

# Ensure we use min_price_value in the queryset
$content = $content -replace 'price__gte=min_price', 'price__gte=min_price_value'
# Fix message and min_price_filter to use min_price_value
$content = $content -replace 'f"No products found above ₹\{min_price\}"', 'f"No products found above ₹{min_price_value}"'
$content = $content -replace '"min_price_filter": float\(min_price\)', '"min_price_filter": float(min_price_value)'

# 2) latest(): replace simple int cast with robust parsing
$pattern2 = "^\s*limit = int\(request\.query_params\.get\(''limit'', 5\)\)\s*$"
$replacement2 = @'
        raw_limit = request.query_params.get('limit', 5)
        try:
            limit = int(raw_limit)
        except (TypeError, ValueError):
            limit = 5
'@
$content = [regex]::Replace($content, $pattern2, $replacement2, [System.Text.RegularExpressions.RegexOptions]::Multiline)

# 3) Fix accidental inline decorator after bulk_create return
$pattern3 = '\)\s*@swagger_auto_schema\('
$replacement3 = ")`r`n`r`n    @swagger_auto_schema("
$content = [regex]::Replace($content, $pattern3, $replacement3)

Set-Content -Path $path -Value $content -Encoding UTF8
Write-Host 'Applied custom API fixes to products\views.py'
