// await (await fetch("/lfc", { method: 'HEAD' })).text()

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