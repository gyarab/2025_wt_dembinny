const { Client } = require('undici');
const fs = require('fs');

const targetOrigin = "https://matous-tlamka.eu"; // Your target

async function calibrate() {
    console.log(`Calibrating baseline for: ${targetOrigin}...`);
    const client = new Client(targetOrigin);
    
    try {
        // Request a path that definitely won't exist
        const { statusCode, headers, body } = await client.request({
            path: '/CALIBRATION_LOCK_123456789',
            method: 'GET',
            headers: { 'accept-encoding': 'br, gzip, deflate' }
        });

        let rawSize = 0;
        for await (const chunk of body) {
            rawSize += chunk.length;
        }

        const config = {
            targetOrigin,
            baselineSize: rawSize,
            statusCode: statusCode,
            encoding: headers['content-encoding'] || 'identity'
        };

        fs.writeFileSync('config.json', JSON.stringify(config, null, 2));
        console.log(`\nCalibration Complete!`);
        console.log(`Detected 404 Baseline: ${rawSize} bytes (${config.encoding})`);
        console.log(`Saved to config.json\n`);
    } catch (err) {
        console.error("Calibration failed:", err.message);
    } finally {
        await client.close();
    }
}

calibrate();