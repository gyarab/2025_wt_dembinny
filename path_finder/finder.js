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
