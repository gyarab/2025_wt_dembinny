await (await fetch("/lfc", { method: 'HEAD' })).text()

// .........................................

const alphabet = "abcdefghijklmnopqrstuvwxyz";

const stringToIndex = (str) => str.split('').reduce((acc, char) => (acc * alphabet.length) + alphabet.indexOf(char), 0);
const indexToString = (index, length) => {
    let res = "";
    for (let i = 0; i < length; i++) {
        res = alphabet[index % alphabet.length] + res;
        index = Math.floor(index / alphabet.length);
    }
    return res;
};

/**
 * @param {string} startPath - Where to begin (e.g. "aaa")
 * @param {number} tolerance - Bytes difference from 404 to trigger a warning
 * @param {number} updateFrequency - How often to log progress (default every 100 paths)
 */
async function scanWithETA(startPath, tolerance = 150, updateFrequency = 100) {
    const n = startPath.length;
    const startIndex = stringToIndex(startPath);
    const maxIndex = Math.pow(alphabet.length, n);
    const totalToProcess = maxIndex - startIndex;

    console.log("--- Initializing Scan ---");
    const baselineRes = await fetch('/non-existent-' + Date.now());
    const baselineLength = (await baselineRes.text()).length;
    
    console.log(`Baseline 404 Size: ${baselineLength} bytes`);
    console.log(`Target: ${totalToProcess.toLocaleString()} combinations.`);
    
    let startTime = Date.now();
    let foundCount = 0;

    for (let i = startIndex; i < maxIndex; i++) {
        const path = indexToString(i, n);
        const currentCount = i - startIndex + 1;

        try {
            const response = await fetch(`/${path}`);
            if (response.ok) {
                const text = await response.text();
                const diff = Math.abs(text.length - baselineLength);

                if (diff > tolerance) {
                    foundCount++;
                    // This is your primary filterable output
                    console.warn(`[!] MATCH: /${path} | Diff: ${diff} bytes | Total Found: ${foundCount}`);
                }
            }
        } catch (e) {
            // Error typically means rate limiting or network drop
            console.error(`Error at /${path}. Pausing 5s...`);
            await new Promise(r => setTimeout(r, 5000));
            i--; continue; 
        }

        // Periodic Progress & ETA Update
        if (currentCount % updateFrequency === 0 || i === maxIndex - 1) {
            const elapsedMs = Date.now() - startTime;
            const msPerReq = elapsedMs / currentCount;
            const remainingReq = maxIndex - i;
            const etaMinutes = (remainingReq * msPerReq) / 1000 / 60;

            console.log(
                `Progress: ${((currentCount / totalToProcess) * 100).toFixed(2)}% | ` +
                `Path: /${path} | ` +
                `Speed: ${Math.round(1000/msPerReq)} req/s | ` +
                `ETA: ${etaMinutes.toFixed(1)} min remaining`
            );
        }

        // Small safety delay to prevent browser locking
        // await new Promise(r => setTimeout(r, 0));
    }
    console.log("--- Scan Complete ---");
}

// Start the scan
scanWithETA("algh");


// --------------------------------------------------------


const alphabet = "abcdefghijklmnopqrstuvwxyz";

const stringToIndex = (str) => str.split('').reduce((acc, char) => (acc * alphabet.length) + alphabet.indexOf(char), 0);
const indexToString = (index, length) => {
    let res = "";
    for (let i = 0; i < length; i++) {
        res = alphabet[index % alphabet.length] + res;
        index = Math.floor(index / alphabet.length);
    }
    return res;
};

/**
 * @param {string} startPath - e.g., "aaa"
 * @param {number} tolerance - Byte difference to trigger a warn
 * @param {number} logInterval - Update progress every X paths
 */
async function fastScanETA(startPath, tolerance = 100, logInterval = 100) {
    const n = startPath.length;
    const startIndex = stringToIndex(startPath);
    const maxIndex = Math.pow(alphabet.length, n);
    const totalToScan = maxIndex - startIndex;

    console.log("%c--- Initializing Fast Scan ---", "color: cyan; font-weight: bold;");
    
    // Get Baseline using HEAD request
    const baselineRes = await fetch('/non-existent-' + Date.now(), { method: 'HEAD' });
    const baselineSize = parseInt(baselineRes.headers.get('content-length')) || 0;
    
    console.log(`Baseline 404 Header Size: ${baselineSize} bytes`);
    console.log(`Remaining to scan: ${totalToScan.toLocaleString()}`);

    let startTime = Date.now();
    let foundCount = 0;

    for (let i = startIndex; i < maxIndex; i++) {
        const path = indexToString(i, n);
        const processedSoFar = i - startIndex + 1;

        try {
            // Using HEAD is much faster as it doesn't download the HTML body
            const response = await fetch(`/${path}`, { method: 'HEAD' });

            if (response.ok) {
                const size = parseInt(response.headers.get('content-length')) || 0;
                const diff = Math.abs(size - baselineSize);

                if (diff > tolerance) {
                    foundCount++;
                    console.warn(`[!] MATCH: /${path} | Header Size: ${size} | Diff: ${diff} | Total: ${foundCount}`);
                }
            }
        } catch (e) {
            console.error(`Connection error at /${path}. Pausing 3s...`);
            await new Promise(r => setTimeout(r, 3000));
            i--; continue;
        }

        // --- ETA and Progress Logic ---
        if (processedSoFar % logInterval === 0 || i === maxIndex - 1) {
            const elapsedMs = Date.now() - startTime;
            const msPerReq = elapsedMs / processedSoFar;
            const remainingReq = maxIndex - i;
            const etaMinutes = (remainingReq * msPerReq) / 1000 / 60;

            console.log(
                `Progress: ${((processedSoFar / totalToScan) * 100).toFixed(2)}% | ` +
                `Current: /${path} | ` +
                `Speed: ${Math.round(1000 / msPerReq)} req/s | ` +
                `ETA: ${etaMinutes.toFixed(1)} min`
            );
        }

        // Short delay to keep the browser responsive
        await new Promise(r => setTimeout(r, 40));
    }

    console.log("%c--- Scan Complete ---", "color: cyan; font-weight: bold;");
}

// Start scanning from 'aaa'
fastScanETA("aaa");


// ======================================
// Turbo speed

const alphabet = "abcdefghijklmnopqrstuvwxyz";
const stringToIndex = (str) => str.split('').reduce((acc, char) => (acc * alphabet.length) + alphabet.indexOf(char), 0);
const indexToString = (index, length) => {
    let res = "";
    for (let i = 0; i < length; i++) {
        res = alphabet[index % alphabet.length] + res;
        index = Math.floor(index / alphabet.length);
    }
    return res;
};

/**
 * @param {string} startPath - e.g., "aaa"
 * @param {number} concurrency - How many requests to run at once (Suggested: 5-10)
 * @param {number} tolerance - Byte difference to trigger a warn
 */
async function turboScan(startPath, concurrency = 6, tolerance = 150) {
    const n = startPath.length;
    const startIndex = stringToIndex(startPath);
    const maxIndex = Math.pow(alphabet.length, n);
    const totalToScan = maxIndex - startIndex;

    console.log("%c--- Initializing Turbo Scan ---", "color: orange; font-weight: bold;");
    
    // Baseline check
    const baselineRes = await fetch('/404-' + Date.now(), { method: 'HEAD' });
    const baselineSize = parseInt(baselineRes.headers.get('content-length')) || 0;
    
    let currentIndex = startIndex;
    let foundCount = 0;
    const startTime = Date.now();

    // The worker function that picks the next available index
    const worker = async () => {
        while (currentIndex < maxIndex) {
            const i = currentIndex++;
            const path = indexToString(i, n);

            try {
                // We use HEAD for speed, change to GET if the server returns 0 for HEAD
                const response = await fetch(`/${path}`, { method: 'HEAD' });
                
                if (response.ok) {
                    const size = parseInt(response.headers.get('content-length')) || 0;
                    if (Math.abs(size - baselineSize) > tolerance) {
                        foundCount++;
                        console.warn(`[!] MATCH: /${path} | Size: ${size} | Total: ${foundCount}`);
                    }
                }
            } catch (e) {
                // If we hit a rate limit, the worker will stop for 5 seconds
                console.error(`Rate limit or error at /${path}. Worker pausing...`);
                await new Promise(r => setTimeout(r, 5000));
            }

            // Report progress periodically
            const processed = currentIndex - startIndex;
            if (processed % 100 === 0) {
                const elapsed = Date.now() - startTime;
                const msPerReq = elapsed / processed;
                const remaining = maxIndex - currentIndex;
                const etaMin = ((remaining * msPerReq) / concurrency / 1000 / 60).toFixed(1);
                
                console.log(`Progress: ${((processed / totalToScan) * 100).toFixed(2)}% | Last: /${path} | Speed: ${Math.round((1000/msPerReq) * concurrency)} req/s | ETA: ${etaMin} min`);
            }
        }
    };

    // Launch parallel workers
    const workers = Array(concurrency).fill(null).map(() => worker());
    await Promise.all(workers);
    
    console.log("%c--- Turbo Scan Complete ---", "color: orange; font-weight: bold;");
}

// Start with 6 parallel connections
turboScan("aaa", 6);

`Progress: 0.57% | Last: /ado | Speed: 570 req/s | ETA: 0.5 min
VM5967:64 Progress: 1.14% | Last: /ahn | Speed: 601 req/s | ETA: 0.5 min
VM5967:64 Progress: 1.71% | Last: /ali | Speed: 614 req/s | ETA: 0.5 min
VM5967:64 Progress: 2.28% | Last: /apf | Speed: 582 req/s | ETA: 0.5 min
VM5967:64 Progress: 2.84% | Last: /asy | Speed: 589 req/s | ETA: 0.5 min`

// *********************************************
//Fixed turbo read

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
                    controller.abort(); 

                    if (Math.abs(chunkSize - baselineSize) > tolerance) {
                        foundCount++;
                        console.warn(`[!] MATCH: /${path} | Chunk Size: ${chunkSize} | Diff: ${chunkSize - baselineSize} | Found: ${foundCount}`);
                    }
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


// 000000000000000000000000000000000000000000000
// smart turbo scan with block detections

// Add a "Kill Switch"
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

async function smartTurboScan(startPath, concurrency = 4) {
    const n = startPath.length;
    let currentIndex = stringToIndex(startPath);
    const maxIndex = Math.pow(alphabet.length, n);

    console.log("%c--- Starting Smart Scan (Keyword Based) ---", "color: #00ff00");

    const worker = async () => {
        while (currentIndex < maxIndex && window.isScanning) {
            const path = indexToString(currentIndex++, n);
            
            try {
                const response = await fetch(`/${path}`);
                if (response.ok) {
                    const reader = response.body.getReader();
                    const { value } = await reader.read();
                    const text = new TextDecoder().decode(value);
                    reader.cancel();

                    // IGNORE common block pages
                    if (text.includes("cf-browser-verification") || text.includes("Access denied")) {
                        console.error(`Blocked at /${path}. Slowing down...`);
                        await new Promise(r => setTimeout(r, 100)); // Wait 100ms if blocked
                        continue;
                    }

                    // SEARCH for a signature that proves it's a real, different page
                    // Adjust "Matouš Tlamka" to something unique to your 404 page
                    if (!text.includes("<h2>TERRA: CONQUEST</h2>")) { 
                        console.warn(`[!] TRUE MATCH FOUND: /${path}`);
                    }
                }
            } catch (e) {
                await new Promise(r => setTimeout(r, 1000));
            }
            
            // Slow down the concurrency to avoid triggers
            // await new Promise(r => setTimeout(r, 250)); 
        }
    };

    const workers = Array(concurrency).fill(null).map(() => worker());
    await Promise.all(workers);
}
function stop() {
    window.isScanning = false;
}

// Call with lower concurrency to be stealthier
smartTurboScan("aews", 6);