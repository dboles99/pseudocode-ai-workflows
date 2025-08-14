<# 
PseudoToPy.ps1
Tiny pseudocode→Python converter (line-based). Usage:
  .\PseudoToPy.ps1 -Input .\example.pseudo -Output .\example.py
#>
param(
  [Parameter(Mandatory=$true)][string]$Input,
  [Parameter()][string]$Output
)

$indent = 0
$IND = "    "
$lines = Get-Content -Path $Input -Raw | -split "\r?\n"
$py = New-Object System.Collections.Generic.List[string]

function Write-Line($text) {
  $py.Add( ($IND * $indent) + $text )
}

foreach ($line in $lines) {
  $trim = $line.Trim()

  if ($trim -match '^FUNCTION\s+([A-Za-z0-9_]+)\((.*?)\)\s*->\s*(.*)$') {
    $name = $matches[1]
    $args = $matches[2]
    $args_py = ($args -split ',') | ForEach-Object { $_.Trim().ToLower() } | Where-Object { $_ -ne '' } | ForEach-Object { $_ } -join ', '
    Write-Line ("def {0}({1}):" -f $name.ToLower(), $args_py)
    $indent++
    continue
  }

  if ($trim -match '^END\s*FUNCTION$') { $indent = [Math]::Max(0, $indent-1); continue }

  if ($trim -match '^SET\s+([A-Za-z0-9_]+)\s*:=\s*(.+)$') {
    Write-Line (("{0} = {1}" -f $matches[1].ToLower(), $matches[2]))
    continue
  }

  if ($trim -match '^IF\s+(.+?)\s+THEN$') { Write-Line ("if {0}:" -f $matches[1]); $indent++; continue }
  if ($trim -match '^ELSE$')            { $indent = [Math]::Max(0, $indent-1); Write-Line ("else:"); $indent++; continue }
  if ($trim -match '^ENDIF$')           { $indent = [Math]::Max(0, $indent-1); continue }

  if ($trim -match '^FOR\s+EACH\s+([A-Za-z0-9_]+)\s+IN\s+(.+)$') {
    Write-Line ("for {0} in {1}:" -f $matches[1].ToLower(), $matches[2])
    $indent++
    continue
  }
  if ($trim -match '^ENDFOR$')          { $indent = [Math]::Max(0, $indent-1); continue }

  if ($trim -match '^WHILE\s+(.+?)\s+DO$') {
    Write-Line ("while {0}:" -f $matches[1]); $indent++; continue
  }
  if ($trim -match '^ENDWHILE$')        { $indent = [Math]::Max(0, $indent-1); continue }

  if ($trim -match '^RETURN\s+(.+)$')  { Write-Line ("return {0}" -f $matches[1]); continue }
  if ($trim -match '^CONTINUE$')        { Write-Line ("continue"); continue }

  if ($trim -eq '') { Write-Line ""; continue }

  # Fallback: pass as-is (e.g., function calls)
  Write-Line $trim
}

if ($Output) {
  Set-Content -Path $Output -Value ($py -join [Environment]::NewLine) -Encoding UTF8
} else {
  ($py -join [Environment]::NewLine) | Write-Output
}
