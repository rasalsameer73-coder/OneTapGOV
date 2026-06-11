Param(
    [Parameter(ValueFromRemainingArguments=$true)]
    $pytestArgs
)

# Run pytest but override pytest.ini addopts so coverage enforcement is skipped
$python = Join-Path -Path $PSScriptRoot -ChildPath "..\.venv\Scripts\python.exe"
& $python -m pytest -o addopts= @pytestArgs
