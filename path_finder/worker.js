const { parentPort, workerData } = require('worker_threads');
const { Pool } = require('undici');

const { startIdx, endIdx, alphabet, targetOrigin, baselineSize, n } = workerData;

const client = new Pool(targetOrigin, { 
    connections: 30, 
    pipelining: 10 
});

function indexToString(idx, len) {
    let res = "";
    for (let i = 0; i < len; i++) {
        res = alphabet[idx % alphabet.length] + res;
        idx = Math.floor(idx / alphabet.length);
    }
    return res;
}

async function run() {
    for (let i = startIdx; i < endIdx; i++) {
        const path = indexToString(i, n);
        
        try {
            const { statusCode, body } = await client.request({
                path: '/' + path,
                method: 'GET',
                headers: { 'accept-encoding': 'br, gzip, deflate' }
            });

            // Fast raw byte count (no decompression)
            let rawSize = body.size;

            // Discovery: Match if status isn't 404 OR size is different
            if (statusCode === 200 && Math.abs(rawSize - baselineSize) > 100) {
                parentPort.postMessage({ type: 'match', path, status: statusCode, size: rawSize });
            }

        } catch (e) {
            // Socket errors are ignored
        }

        if (i % 250 === 249) parentPort.postMessage({ type: 'progress', count: 250, path: path });
    }
}

run();