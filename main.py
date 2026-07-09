from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.engine import SecurityEngine 

app = FastAPI(title="Jailbreak Attack Guard")
guard_system = SecurityEngine()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/inspect")
async def inspect_endpoint(request: PromptRequest):
    try:
        result = guard_system.inspect_prompt(request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Jailbreak Guard Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-50 text-slate-800 min-h-screen flex font-sans">
        
        <!-- Sidebar - Audit History -->
        <div class="w-80 bg-white border-r border-slate-200 flex flex-col shrink-0 shadow-sm">
            <div class="p-4 border-b border-slate-200 bg-slate-100/50 flex justify-between items-center">
                <h2 class="font-bold text-slate-700 flex items-center gap-2 text-sm uppercase tracking-wider">
                     Audit Logs History
                </h2>
                <button onclick="downloadReport()" id="downloadBtn" disabled class="text-xs bg-indigo-50 border border-indigo-200 text-indigo-600 font-medium py-1 px-2.5 rounded hover:bg-indigo-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                    Export Report
                </button>
            </div>
            <div id="historyList" class="flex-1 overflow-y-auto p-3 space-y-2 text-sm text-slate-500">
                <div id="emptyState" class="text-center py-8 text-slate-400 italic">No prompts scanned yet</div>
            </div>
        </div>

        <!-- Main Workspace Area -->
        <div class="flex-1 flex flex-col items-center justify-center p-8">
            <div class="w-full max-w-2xl bg-white rounded-xl shadow-md p-8 border border-slate-200">
                <div class="flex items-center gap-3 mb-2">
                    <span class="text-2xl"></span>
                    <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">AI Security Firewall</h1>
                </div>
                <p class="text-slate-500 text-sm mb-6">Analyze input strings via Multi-Layer Security validation: Base64 Normalization, Perplexity check, and Small-LM evaluation.</p>
                
                <div class="mb-4">
                    <label class="block text-sm font-semibold mb-2 text-slate-700">Input Prompt</label>
                    <textarea id="promptInput" rows="4" class="w-full bg-slate-50 border border-slate-300 rounded-lg p-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 placeholder-slate-400 font-mono text-sm shadow-inner transition-all" placeholder="Paste a prompt or base64 payload here..."></textarea>
                </div>
                
                <button onclick="analyzePrompt()" id="submitBtn" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 px-4 rounded-lg shadow transition-colors duration-150">
                    Analyze Prompt
                </button>
                
                <!-- Output Analytics Panel -->
                <div id="results" class="hidden mt-6 pt-6 border-t border-slate-200 animate-fadeIn">
                    <div class="flex items-center justify-between mb-4">
                        <span class="text-sm font-semibold text-slate-600">Firewall Verdict</span>
                        <span id="verdictBadge" class="px-3 py-1 rounded-full text-xs font-extrabold tracking-wider uppercase shadow-sm"></span>
                    </div>
                    
                    <div id="reasonBox" class="p-3.5 rounded-lg text-sm mb-4 border font-medium shadow-sm"></div>
                    
                    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Pipeline Telemetry</h3>
                    <div class="grid grid-cols-3 gap-3 text-center mb-4">
                        <div class="bg-slate-50 p-3 rounded-lg border border-slate-200">
                            <div class="text-xs font-medium text-slate-500">Perplexity</div>
                            <div id="metricPpl" class="text-lg font-mono font-bold mt-0.5 text-slate-800"></div>
                        </div>
                        <div class="bg-slate-50 p-3 rounded-lg border border-slate-200">
                            <div class="text-xs font-medium text-slate-500">Semantic Label</div>
                            <div id="metricVerdict" class="text-lg font-bold mt-0.5 capitalize text-slate-800"></div>
                        </div>
                        <div class="bg-slate-50 p-3 rounded-lg border border-slate-200">
                            <div class="text-xs font-medium text-slate-500">Confidence</div>
                            <div id="metricConfidence" class="text-lg font-mono font-bold mt-0.5 text-slate-800"></div>
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Processed Text Output</label>
                        <div id="processedText" class="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs font-mono text-emerald-400 max-h-24 overflow-y-auto shadow-inner"></div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Global array holding full history logs for reporting
            let auditHistory = [];

            async function analyzePrompt() {
                const promptInput = document.getElementById('promptInput').value;
                const submitBtn = document.getElementById('submitBtn');
                const resultsDiv = document.getElementById('results');
                
                if(!promptInput.trim()) return alert("Please enter a text prompt.");
                
                submitBtn.disabled = true;
                submitBtn.innerText = "Processing Pipeline...";
                
                try {
                    const response = await fetch('/inspect', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: promptInput })
                    });
                    
                    const data = await response.json();
                    
                    // Render Metrics Panels
                    const badge = document.getElementById('verdictBadge');
                    const reason = document.getElementById('reasonBox');
                    
                    if(data.blocked) {
                        badge.className = "px-3 py-1 rounded-full text-xs font-extrabold tracking-wider uppercase bg-rose-50 text-rose-700 border border-rose-200";
                        badge.innerText = "BLOCKED";
                        reason.className = "p-3.5 bg-rose-50 text-rose-800 rounded-lg text-sm mb-4 border border-rose-200";
                    } else {
                        badge.className = "px-3 py-1 rounded-full text-xs font-extrabold tracking-wider uppercase bg-emerald-50 text-emerald-700 border border-emerald-200";
                        badge.innerText = "PASSED";
                        reason.className = "p-3.5 bg-emerald-50 text-emerald-800 rounded-lg text-sm mb-4 border border-emerald-200";
                    }
                    
                    reason.innerText = data.reason;
                    document.getElementById('metricPpl').innerText = data.metrics.perplexity;
                    document.getElementById('metricVerdict').innerText = data.metrics.semantic_verdict;
                    document.getElementById('metricConfidence').innerText = (data.metrics.confidence_score * 100).toFixed(1) + "%";
                    document.getElementById('processedText').innerText = data.processed_text;
                    
                    resultsDiv.classList.remove('hidden');

                    // Commit entry to running history list
                    appendHistoryRecord(promptInput, data);

                } catch (err) {
                    alert("Failed to hit the security backend endpoints.");
                    console.error(err);
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.innerText = "Analyze Prompt";
                }
            }

            function appendHistoryRecord(originalPrompt, resultData) {
                const historyList = document.getElementById('historyList');
                const emptyState = document.getElementById('emptyState');
                if (emptyState) emptyState.remove();

                const logEntry = {
                    timestamp: new Date().toISOString(),
                    input: originalPrompt,
                    evaluation: resultData
                };
                auditHistory.unshift(logEntry); // Add to beginning of session list

                // Enable export button
                document.getElementById('downloadBtn').disabled = false;

                // Create visual item element
                const element = document.createElement('div');
                const badgeColor = resultData.blocked ? 'bg-rose-100 text-rose-700 border-rose-200' : 'bg-emerald-100 text-emerald-700 border-emerald-200';
                const statusLabel = resultData.blocked ? 'BLOCKED' : 'PASSED';
                
                element.className = "bg-white p-3 rounded-lg border border-slate-200 shadow-sm flex flex-col gap-1 hover:border-slate-300 transition-all cursor-pointer";
                element.onclick = () => {
                    document.getElementById('promptInput').value = originalPrompt;
                    analyzePrompt();
                };

                element.innerHTML = `
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-extrabold px-2 py-0.5 rounded border ${badgeColor}">${statusLabel}</span>
                        <span class="text-[10px] text-slate-400 font-mono">${new Date().toLocaleTimeString()}</span>
                    </div>
                    <p class="text-xs font-medium text-slate-700 truncate">${originalPrompt.substring(0, 60)}...</p>
                    <div class="text-[11px] text-slate-400 font-mono">ppl: ${resultData.metrics.perplexity} | verdict: ${resultData.metrics.semantic_verdict}</div>
                `;

                historyList.insertBefore(element, historyList.firstChild);
            }

            

      

        function downloadReport() {
                if (auditHistory.length === 0) return;
                
                // 1. Build a clean, scannable human-readable text block
                let txtContent = `==================================================\n`;
                txtContent += `          AI ATTACK DETECTION SYSTEM REPORT      \n`;
                txtContent += `==================================================\n`;
                txtContent += `Generated At: ${new Date().toLocaleString()}\n`;
                txtContent += `Total Prompts Scanned: ${auditHistory.length}\n`;
                txtContent += `Flagged Incidents: ${auditHistory.filter(item => item.evaluation.blocked).length}\n`;
                txtContent += `==================================================\n\n`;

                auditHistory.forEach((log, index) => {
                    txtContent += `[LOG ENTRY #${auditHistory.length - index}] [${new Date(log.timestamp).toLocaleTimeString()}]\n`;
                    txtContent += `--------------------------------------------------\n`;
                    txtContent += `VERDICT:      ${log.evaluation.blocked ? "⛔ BLOCKED" : "✅ PASSED"}\n`;
                    txtContent += `REASON:       ${log.evaluation.reason}\n`;
                    txtContent += `PERPLEXITY:   ${log.evaluation.metrics.perplexity}\n`;
                    txtContent += `SEMANTIC:     ${log.evaluation.metrics.semantic_verdict} (Confidence: ${(log.evaluation.metrics.confidence_score * 100).toFixed(1)}%)\n`;
                    txtContent += `RAW INPUT:    "${log.input}"\n`;
                    if (log.input !== log.evaluation.processed_text) {
                        txtContent += `PROCESSED:    "${log.evaluation.processed_text}"\n`;
                    }
                    txtContent += `\n==================================================\n\n`;
                });

                // 2. Trigger a clean plain text file download pipeline
                const blob = new Blob([txtContent], { type: 'text/plain;charset=utf-8' });
                const url = URL.createObjectURL(blob);
                const downloadAnchor = document.createElement('a');
                downloadAnchor.setAttribute("href", url);
                downloadAnchor.setAttribute("download", `security_audit_report_${Date.now()}.txt`);
                document.body.appendChild(downloadAnchor);
                downloadAnchor.click();
                
                // Cleanup browser memory reference
                document.body.removeChild(downloadAnchor);
                URL.revokeObjectURL(url);
            }
        </script>
        
    </body>
    </html>
    """