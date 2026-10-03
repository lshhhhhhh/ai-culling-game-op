# Open the JJK S3 OP review page (http://127.0.0.1:8769/), starting its server if needed.
# Same review tool as the Makeine project (port 8766), pointed at assets/jujutsu/op1_v1.
$ErrorActionPreference = 'Stop'
$url = 'http://127.0.0.1:8769'
$runtime = 'assets\lycoris\op1_v1\review'
$ready = $false
try { $ready = (Invoke-RestMethod -Uri "$url/api/review" -TimeoutSec 2).manifest.title -like '*S3*' } catch {}
if (-not $ready) {
    Start-Process -FilePath 'ComfyUI\venv\Scripts\python.exe' `
        -ArgumentList @('pipelines\anime_op\review_school_op.py', '--serve', '--project', 'assets/jujutsu/op1_v1', '--port', '8769') `
        -WorkingDirectory '.' -WindowStyle Hidden `
        -RedirectStandardOutput "$runtime\server.log" -RedirectStandardError "$runtime\server.err"
    for ($i = 0; $i -lt 30 -and -not $ready; $i++) {
        Start-Sleep -Milliseconds 300
        try { $ready = (Invoke-RestMethod -Uri "$url/api/review" -TimeoutSec 1).manifest.title -like '*S3*' } catch {}
    }
}
if (-not $ready) { throw "JJK review page did not start. Check $runtime\server.err" }
Start-Process "$url/"
