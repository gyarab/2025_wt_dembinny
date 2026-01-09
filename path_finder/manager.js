const { Worker } = require('worker_threads');
const os = require('os');

const cpuCount = os.cpus().length;
const alphabet = "abcdefghijklmnopqrstuvwxyz";

function startFuzzer() {
    const totalPermutations = Math.pow(alphabet.length, 4); // for aaaa-zzzz
    const chunkSize = Math.floor(totalPermutations / cpuCount);

    for (let i = 0; i < cpuCount; i++) {
        const start = i * chunkSize;
        const end = (i === cpuCount - 1) ? totalPermutations : (i + 1) * chunkSize;

        const worker = new Worker('./worker.js', {
            workerData: { start, end, alphabet, target: 'http://matous-tlamka.eu/' }
        });

        worker.on('message', (msg) => {
            if (msg.type === 'match') {
                console.log(`[FOUND] ${msg.url} - Status: ${msg.status}`);
                // Append to found.txt here
            }
            if (msg.type === 'telemetry') {
                // Update your global req/s counter
            }
        });
    }
}

startFuzzer();