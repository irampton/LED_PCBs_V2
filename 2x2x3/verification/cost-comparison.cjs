const fs = require('fs');
const path = require('path');
const bom = require('C:/Code/Schrune/src/jlc-bom');

async function main() {
    const root = path.resolve(__dirname, '../..');
    const counts = JSON.parse(fs.readFileSync(path.join(__dirname, 'pad-counts.json')));
    const results = {};
    for (const name of ['2x2x4', '2x2x3']) {
        const report = await bom.buildJlcBom({cwd: path.join(root, name), boardCount: 30});
        const raw = bom.calculateEconomicEstimate(report.rows, 30);
        for (const row of report.rows) {
            row.jointsPerBoard = row.designators.reduce((total, ref) => total + counts[name][ref], 0);
        }
        results[name] = {
            rawSchruneEconomic: raw,
            correctedEconomic: bom.calculateEconomicEstimate(report.rows, 30),
            jointsPerBoard: report.rows.reduce((total, row) => total + row.jointsPerBoard, 0),
            stockWarnings: report.stockWarnings,
            rows: report.rows
        };
    }
    fs.writeFileSync(path.join(__dirname, 'cost-comparison.json'), JSON.stringify(results, null, 2));
    console.log(JSON.stringify(Object.fromEntries(Object.entries(results).map(([name, r]) => [name, {
        raw: r.rawSchruneEconomic,
        corrected: r.correctedEconomic,
        jointsPerBoard: r.jointsPerBoard
    }])), null, 2));
}

main().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
