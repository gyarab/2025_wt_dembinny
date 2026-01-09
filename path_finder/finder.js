// await (await fetch("/lfc", { method: 'HEAD' })).text()

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

    const baseContent = "<h2>TERRA: CONQUEST</h2>";

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
                    if (!text.includes(baseContent)) { 
                        console.warn(`[!] TRUE MATCH FOUND: /${path}`);
                    }
                    controller.abort();
                }
            } catch (e) {
                if (e.name !== 'AbortError') {
                    console.error(`Error at /${path}:`, e.message);
                    await new Promise(r => setTimeout(r, 1000));
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