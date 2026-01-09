// await (await fetch("/lfc", { method: 'HEAD' })).text()
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
