const { Worker } = require('worker_threads');
const fs = require('fs');
const path = require('path');

const cpuCount = 8;
const alphabet = "abcdefghijklmnopqrstuvwxyz";

// create/open found log in project root
const foundLogPath = path.join(__dirname, 'found.txt');
const foundStream = fs.createWriteStream(foundLogPath, { flags: 'a' });

// ensure stream closed on exit
process.on('exit', () => {
	foundStream.end();
});

function startFuzzer() {
    const totalPermutations = Math.pow(alphabet.length, 4); // for aaaa-zzzz
    const chunkSize = Math.floor(totalPermutations / cpuCount);

    for (let i = 0; i < cpuCount; i++) {
        const start = i * chunkSize;
        const end = (i === cpuCount - 1) ? totalPermutations : (i + 1) * chunkSize;

        const worker = new Worker('./path_finder/worker.js', {
            workerData: { start, end, alphabet, target: 'http://matous-tlamka.eu/' }
        });

        worker.on('message', (msg) => {
            if (msg.type === 'match') {
                console.log(`[FOUND] ${msg.url} - Status: ${msg.status}`);
                foundStream.write(`${new Date().toISOString()} ${msg.url} - Status: ${msg.status}\n`);
            }
            if (msg.type === 'telemetry') {
                // Update your global req/s counter
            }
        });
    }
}

startFuzzer();