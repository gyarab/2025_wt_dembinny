// await (await fetch("/lfc", { method: 'HEAD' })).text()
// Turbo speed
window.isScanning = true;

const alphabet = "abcdefghijklmnopqrstuvwxyz";
const stringToIndex = (s) => s.split('').reduce((a, c) => (a * alphabet.length) + alphabet.indexOf(c), 0);
const indexToString = (idx, len) => {
    let res = "";
    for (let i = 0; i < len; i++) {
        res = alphabet[idx % alphabet.length] + res;
        idx = Math.floor(idx / alphabet.length);
    }
    return res;
};

/**
 * @param {string} startPath - e.g., "aaa"
 * @param {number} concurrency - Number of parallel requests (Try 5-8)
 * @param {number} tolerance - Chunk size difference to trigger a warn
 */
async function turboStreamScan(startPath, concurrency = 6, tolerance = 50) {
    const n = startPath.length;
    const startIndex = stringToIndex(startPath);
    const maxIndex = Math.pow(alphabet.length, n);
    const totalToScan = maxIndex - startIndex;

    console.log("%c--- Initializing Turbo Stream Scan ---", "color: #00e5ff; font-weight: bold;");

    // 1. Get Baseline Chunk Size
    const baselineRes = await fetch('/non-existent-' + Date.now());
    const reader = baselineRes.body.getReader();
    const { value: baselineChunk } = await reader.read();
    const baselineSize = baselineChunk ? baselineChunk.length : 0;
    reader.cancel(); // Stop downloading the rest of the 404

    console.log(`Baseline 404 first-chunk size: ${baselineSize} bytes`);
    
    let currentIndex = startIndex;
    let foundCount = 0;
    const startTime = Date.now();

    const worker = async () => {
        while (currentIndex < maxIndex) {
            // CHECK THE KILL SWITCH
            if (!window.isScanning) {
                console.log("%c[!] Stopping script...", "color: red; font-weight: bold;");
                return; 
            }

            const i = currentIndex++;
            const path = indexToString(i, n);
            const controller = new AbortController();

            try {
                const response = await fetch(`/${path}`, { signal: controller.signal });
                
                if (response.ok) {
                    const reader = response.body.getReader();
                    const { value: chunk } = await reader.read();
                    const chunkSize = chunk ? chunk.length : 0;
                    
                    // Kill the connection as soon as we have the first chunk 

                    if (Math.abs(chunkSize - baselineSize) > tolerance) {
                        if (chunkSize - baselineSize < -2000) {
                            console.error(`[!!!] LARGE NEGATIVE DIFF DETECTED at /${path} | Chunk Size: ${chunkSize} | Diff: ${chunkSize - baselineSize}`);
                            currentIndex--; // Re-scan this one
                            continue;
                        }
                        foundCount++;
                        console.warn(`[!] MATCH: /${path} | Chunk Size: ${chunkSize} | Diff: ${chunkSize - baselineSize} | Found: ${foundCount}`);
                    }
                    controller.abort();
                }
            } catch (e) {
                if (e.name !== 'AbortError') {
                    console.error(`Error at /${path}:`, e.message);
                    await new Promise(r => setTimeout(r, 2000));
                }
            }

            // ETA and Progress
            const processed = currentIndex - startIndex;
            if (processed % 100 === 0 || currentIndex === maxIndex) {
                const elapsed = Date.now() - startTime;
                const msPerReq = elapsed / processed;
                const remaining = maxIndex - currentIndex;
                const etaMin = ((remaining * msPerReq) / concurrency / 1000 / 60).toFixed(1);
                
                console.log(`Progress: ${((processed / totalToScan) * 100).toFixed(2)}% | Path: /${path} | Speed: ${Math.round((1000/msPerReq) * concurrency)} req/s | ETA: ${etaMin} min`);
            }
        }
    };

    // Fire up the workers
    const workers = Array(concurrency).fill(null).map(() => worker());
    await Promise.all(workers);
    
    console.log("%c--- Scan Complete ---", "color: #00e5ff; font-weight: bold;");
}
function stop() {
    window.isScanning = false;
}

// Start scanning
turboStreamScan("aews", 6);
