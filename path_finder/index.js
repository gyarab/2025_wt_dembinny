const { Worker } = require('worker_threads');
const os = require('os');
const fs = require('fs');

// Load calibration data
if (!fs.existsSync('config.json')) {
    console.error("Error: Run 'node calibrate.js' first!");
    process.exit(1);
}
const config = JSON.parse(fs.readFileSync('config.json'));
// CONFIGURATION
const alphabet = "abcdefghijklmnopqrstuvwxyz";
const targetOrigin = "https://matous-tlamka.eu";
const pathLength = 4; // Length of string (e.g., aaaa)
const baselineSize = 5117; // The size of a 404 page on the target
const threadCount = os.cpus().length;

const totalPaths = Math.pow(alphabet.length, pathLength);
const logStream = fs.createWriteStream('found_pages.txt', { flags: 'a' });

// Global telemetry
let totalProcessed = 0;
const startTime = Date.now();

async function start() {
    console.log(`\n--- Launching Node Turbo-Fuzzer ---`);
    console.log(`Target:  ${targetOrigin}`);
    console.log(`Threads: ${threadCount} (One per CPU core)`);
    console.log(`Space:   ${totalPaths.toLocaleString()} combinations`);
    console.log(`------------------------------------\n`);

    const pathsPerThread = Math.floor(totalPaths / threadCount);

    for (let i = 0; i < threadCount; i++) {
        const startIdx = i * pathsPerThread;
        const endIdx = (i === threadCount - 1) ? totalPaths : (i + 1) * pathsPerThread;
        
        const worker = new Worker('./worker.js', {
            workerData: { 
                startIdx, endIdx, alphabet, 
                targetOrigin: config.targetOrigin, 
                baselineSize: config.baselineSize, 
                n: pathLength 
            }
        });

        worker.on('message', (msg) => {
            if (msg.type === 'match') {
                out = `[!] MATCH: /${msg.path} (Status: ${msg.status}, Size: ${msg.size})\n`;
            
                process.stdout.write(out);
                logStream.write(out);
            }
            
            if (msg.type === 'progress') {
                totalProcessed += msg.count;
                const elapsed = (Date.now() - startTime) / 1000;
                const rps = Math.floor(totalProcessed / elapsed);
                const percent = ((totalProcessed / totalPaths) * 100).toFixed(2);
                
                // Overwrite the same line in the console for a clean UI
                process.stdout.write(`\rProgress: ${percent}%  \t| Path: ${msg.path}\t| Speed: ${rps} req/s\t| Found: ${totalProcessed.toLocaleString()}/${totalPaths.toLocaleString()}\n`);
            }
            // You could add a progress bar here using msg.current
        });

        worker.on('error', (err) => console.error(`Worker error: ${err}`));
        worker.on('exit', (code) => {
            if (code !== 0) console.error(`Worker stopped with exit code ${code}`);
        });
    }
}

start();