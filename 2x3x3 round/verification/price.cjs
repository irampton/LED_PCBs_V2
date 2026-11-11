const fs = require('fs');
const path = require('path');
const bom = require('C:/Code/Schrune/src/jlc-bom');

async function main() {
    const cwd = path.resolve(__dirname, '..');
    const counts = require('./pad-counts.json');
    const report = await bom.buildJlcBom({cwd, boardCount: 100});
    const results = {};
    for (const boards of [30, 100]) {
        const displayRows = report.rows.map(row => ({...row, perBoardCost: row.totalPurchaseCostForBoards(boards) / boards}));
        const sections = Object.fromEntries(Object.entries(report.sections).map(([section, rows]) => [section, displayRows.filter(row => row.section === section)]));
        fs.writeFileSync(path.join(__dirname, `jlc-bom-${boards}.txt`), bom.renderJlcBomReport({...report, rows: displayRows, sections, boardCount: boards}));
        const rows = report.rows.map(row => ({
            ...row,
            jointsPerBoard: row.designators.reduce((sum, ref) => sum + counts[ref], 0)
        }));
        const standard = bom.calculateStandardEstimate(rows, boards);
        const estimate = {...standard, secondSideSetup: 25, secondSideStencil: 7.86, handSolderAllowance: 3.5};
        estimate.total = standard.total + 25 + 7.86 + 3.5;
        estimate.perBoard = estimate.total / boards;
        results[boards] = estimate;
    }
    const output = {date: '2026-11-09', currency: 'USD', service: 'Standard, double-sided, with populated through-hole header', jointsPerBoard: report.rows.reduce((sum, row) => sum + row.designators.reduce((n, ref) => n + counts[ref], 0), 0), results, stockWarnings: report.stockWarnings, exclusions: 'PCB fabrication, shipping, tax, attrition, minimum purchases, additional manual assembly/panel/x-ray fees; hand soldering is a $3.50 allowance only, subject to quotation', parts: report.rows.map(row => ({lcsc: row.lcsc, quantity: row.quantity, stock: row.stock, section: row.section, pricing: row.jlcPart.prices}))};
    fs.writeFileSync(path.join(__dirname, 'price-estimate.json'), JSON.stringify(output, null, 2));
    console.log(JSON.stringify({results, stockWarnings: report.stockWarnings}, null, 2));
}

main().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
