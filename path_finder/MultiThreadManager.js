// 1. Define the Worker code
const workerCode = `
    self.onmessage = async (e) => {
        const { startPath, signatureBytes, batchSize } = e.data;
        let currentChars = startPath.split('').map(c => c.charCodeAt(0));
        const len = currentChars.length;
        
        const next = () => {
            for (let i = len - 1; i >= 0; i--) {
                if (currentChars[i] < 122) { // 'z'
                    currentChars[i]++;
                    return true;
                }
                currentChars[i] = 97; // 'a'
            }
            return false;
        };

        const sig = "<h2>TERRA: CONQUEST</h2>";
        
        while (true) {
            const batch = [];
            let lastPath = "";
            for(let i = 0; i < batchSize; i++) {
                lastPath = String.fromCharCode(...currentChars);
                batch.push(lastPath);
                if (!next()) break;
            }

            await Promise.all(batch.map(async (path) => {
                try {
                    const res = await fetch("/" + path);
                    if (res.ok) {
                        const reader = res.body.getReader();
                        const { value } = await reader.read();
                        reader.cancel();

                        if (value) {
                            // Fast check on the first chunk
                            const textHeader = String.fromCharCode(...value.slice(0, 800));
                            if (!textHeader.includes(sig)) {
                                self.postMessage({ type: 'match', path });
                            }
                        }
                    }
                } catch (err) {}
            }));
            
            // Send both the count and the last path processed in this batch
            self.postMessage({ type: 'progress', step: batch.length, path: lastPath });
            if (currentChars.every(c => c === 122)) break;
        }
    };
`;

window.isScanning = true;
const workerBlob = new Blob([workerCode], { type: 'application/javascript' });
const workerUrl = URL.createObjectURL(workerBlob);

async function startMultiThreadedScan(startPath, threadCount = 6) {
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

    const totalPaths = Math.pow(26, startPath.length);
    const startIndex = stringToIndex(startPath);
    const pathsToScan = totalPaths - startIndex;
    const pathsPerWorker = Math.floor(pathsToScan / threadCount);

    let totalProcessed = 0;
    let latestPath = startPath;
    const startTime = Date.now();

    console.log(`%c--- Starting Threaded Scan at 1800+ req/s ---`, "color: #00ffff; font-weight: bold;");

    for (let i = 0; i < threadCount; i++) {
        const worker = new Worker(workerUrl);
        const workerStartIdx = startIndex + (i * pathsPerWorker);
        const workerStartPath = indexToString(workerStartIdx, startPath.length);

        worker.postMessage({
            startPath: workerStartPath,
            batchSize: 25 
        });

        worker.onmessage = (e) => {
            if (!window.isScanning) {
                worker.terminate();
                return;
            }
            
            if (e.data.type === 'match') {
                console.warn(`[!] DISCOVERY: /${e.data.path}`);
            } else if (e.data.type === 'progress') {
                totalProcessed += e.data.step;
                latestPath = e.data.path; // Update the position tracker
            }
        };
    }

    // Logger with Position tracking
    const reporter = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        const speed = Math.round(totalProcessed / elapsed);
        const percent = ((totalProcessed / pathsToScan) * 100).toFixed(2);
        const eta = ( (pathsToScan - totalProcessed) / speed / 60 ).toFixed(1);

        if (!window.isScanning || totalProcessed >= pathsToScan) {
            clearInterval(reporter);
            console.log("%c--- Scan Stopped ---", "color: orange;");
        } else {
            // New logger format with "Current Position"
            console.log(
                `[${latestPath}] | ` + 
                `Speed: ${speed} req/s | ` + 
                `Progress: ${percent}% | ` + 
                `ETA: ${eta}m`
            );
        }
    }, 2000);
}

// Start with 6 threads starting from your current progress
startMultiThreadedScan("ajxc", 6);