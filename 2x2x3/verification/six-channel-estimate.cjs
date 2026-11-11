const fs = require('fs');
const path = require('path');
const bom = require('C:/Code/Schrune/src/jlc-bom');

async function main() {
    const cwd = path.resolve(__dirname, '..');
    const pads = require('./pad-counts.json')['2x2x3'];
    const report = await bom.buildJlcBom({cwd, boardCount: 100});
    const results = {};
    for (const boards of [30, 100]) {
        const raw = boards === 30
            ? bom.calculateEconomicEstimate(report.rows, boards)
            : bom.calculateStandardEstimate(report.rows, boards);
        const corrected = report.rows.map(row => ({
            ...row,
            jointsPerBoard: row.designators.reduce((sum, ref) => sum + pads[ref], 0)
        }));
        const existing = boards === 30
            ? bom.calculateEconomicEstimate(corrected, boards)
            : bom.calculateStandardEstimate(corrected, boards);
        const expanded = corrected.map(row => ({
            ...row,
            jointsPerBoard: row.jointsPerBoard * 1.5,
            totalPurchaseCostForBoards(count) {
                return row.totalPurchaseCostForBoards(count * 1.5);
            }
        }));
        const sixChannel = bom.calculateStandardEstimate(expanded, boards);
        sixChannel.secondSideSetup = 25;
        sixChannel.secondSideStencil = 7.86;
        sixChannel.total += 32.86;
        results[boards] = {raw, existing, sixChannel};
    }
    const output = {date: '2026-11-09', currency: 'USD', assumptions: {
        existingJoints: 120, sixChannelJoints: 180,
        sixChannelWarmLeds: 9, sixChannelCoolLeds: 9,
        secondSideAdditionalFees: 32.86,
        excludes: 'PCB fabrication, shipping, tax, attrition, minimum purchases, headers and any other assembly fees'
    }, results};
    fs.writeFileSync(path.join(__dirname, 'six-channel-estimate.json'), JSON.stringify(output, null, 2));
    console.log(JSON.stringify(output, null, 2));
}

main().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
