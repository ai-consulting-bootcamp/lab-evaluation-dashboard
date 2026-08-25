import fs from "node:fs/promises";
import path from "node:path";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const root = path.dirname(new URL(import.meta.url).pathname);
const evalCsv = await fs.readFile(path.join(root, "data/evaluation_data_clean.csv"), "utf8");
const agreeCsv = await fs.readFile(path.join(root, "data/judge_agreement_data.csv"), "utf8");

const workbook = await Workbook.fromCSV(evalCsv, { sheetName: "Evaluation Data" });
const parseSimpleCsv = (text) => text.trim().split(/\r?\n/).map((line) => line.split(",").map((value) => {
  const numeric = Number(value);
  return value !== "" && Number.isFinite(numeric) ? numeric : value;
}));
const agreementRows = parseSimpleCsv(agreeCsv);
const agreementSheet = workbook.worksheets.add("Judge Agreement");
agreementSheet.getRangeByIndexes(0, 0, agreementRows.length, agreementRows[0].length).values = agreementRows;
const summary = workbook.worksheets.add("Dashboard Guide");

summary.showGridLines = false;
summary.getRange("A1:H2").merge();
summary.getRange("A1").values = [["Model Evaluation Dashboard — Data Workbook"]];
summary.getRange("A1:H2").format = {
  fill: "#13263D",
  font: { bold: true, color: "#FFFFFF", size: 18 },
  verticalAlignment: "center",
  horizontalAlignment: "left",
};
summary.getRange("A4:B8").values = [
  ["Purpose", "Auditable source tables for the Tableau dashboards"],
  ["Evaluation rows", 1800],
  ["Agreement rows", 900],
  ["Date range", "2026-05-26 to 2026-08-23"],
  ["Agreement rule", "Absolute judge-score difference ≤ 10 points"],
];
summary.getRange("A4:A8").format = { fill: "#DDF2F1", font: { bold: true, color: "#13263D" } };
summary.getRange("A4:B8").format.borders = { preset: "outside", style: "thin", color: "#D9E1EA" };
summary.getRange("A10:H10").merge();
summary.getRange("A10").values = [["The sample is deterministic and synthetic. It follows Option B in the lab because the preceding five-case LLM-judge calibration was too small for the recommended 100+ row distribution analysis."]];
summary.getRange("A10:H10").format = { fill: "#FFF4E8", font: { color: "#6B3B0C", italic: true }, wrapText: true };
summary.getRange("A1:H12").format.rowHeight = 24;
summary.getRange("A1:H12").format.autofitColumns();
summary.getRange("B4:B10").format.columnWidth = 62;

for (const sheetName of ["Evaluation Data", "Judge Agreement"]) {
  const sheet = workbook.worksheets.getItem(sheetName);
  sheet.showGridLines = false;
  const used = sheet.getUsedRange();
  const header = used.getRow(0);
  header.format = { fill: "#13263D", font: { bold: true, color: "#FFFFFF" } };
  used.format.autofitColumns();
  sheet.freezePanes.freezeRows(1);
}

workbook.worksheets.getItem("Evaluation Data").getRange("C2:C1801").format.numberFormat = "0.00";
workbook.worksheets.getItem("Evaluation Data").getRange("E2:E1801").format.numberFormat = "yyyy-mm-dd";
workbook.worksheets.getItem("Judge Agreement").getRange("C2:E901").format.numberFormat = "0.00";
workbook.worksheets.getItem("Judge Agreement").getRange("H2:H901").format.numberFormat = "yyyy-mm-dd";

const check = await workbook.inspect({
  kind: "table",
  range: "'Dashboard Guide'!A1:H12",
  include: "values,formulas",
  tableMaxRows: 12,
  tableMaxCols: 8,
});
console.log(check.ndjson);
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 50 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

const preview = await workbook.render({ sheetName: "Dashboard Guide", range: "A1:H12", scale: 1.5, format: "png" });
await fs.writeFile(path.join(root, "screenshots/data_workbook_preview.png"), new Uint8Array(await preview.arrayBuffer()));
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(path.join(root, "evaluation_dashboard_data.xlsx"));
