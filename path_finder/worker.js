const { workerData, parentPort } = require('worker_threads');
const { Pool } = require('undici');

const client = new Pool(workerData.target, { connections: 100 });

async function run() {
    for (let i = workerData.start; i < workerData.end; i++) {
        const word = generateWord(i, workerData.alphabet);
        
        try {
            const { statusCode, headers } = await client.request({
                path: `/${word}`,
                method: 'GET',
            });

            // Smart Filter
            if (statusCode !== 404) {
                parentPort.postMessage({ 
                    type: 'match', 
                    url: word, 
                    status: statusCode,
                    length: headers['content-length'] 
                });
            }

            // Periodic Telemetry
            if (i % 100 === 0) {
                parentPort.postMessage({ type: 'telemetry', count: 100 });
            }
        } catch (err) {
            // Handle connection drops or timeouts
        }
    }
}

function generateWord(index, alphabet) {
    let word = "";
    let n = index;
    for (let i = 0; i < 4; i++) {
        word = alphabet[n % alphabet.length] + word;
        n = Math.floor(n / alphabet.length);
    }
    return word;
}

run();