const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  LevelFormat, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, Footer, PageNumber, PageOrientation,
} = require('docx');

const FONT = 'Georgia';
const CONTENT_DXA = 9360; // Letter 12240 - 2 x 1440 margins

function parseInline(text) {
  const runs = [];
  const re = /\*\*([^*]+)\*\*|\*([^*\n]+)\*/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) runs.push(new TextRun({ text: text.slice(last, m.index) }));
    if (m[1] !== undefined) runs.push(new TextRun({ text: m[1], bold: true }));
    else runs.push(new TextRun({ text: m[2], italics: true }));
    last = re.lastIndex;
  }
  if (last < text.length) runs.push(new TextRun({ text: text.slice(last) }));
  return runs.length ? runs : [new TextRun({ text: '' })];
}

function splitRow(line) {
  let s = line.trim();
  if (s.startsWith('|')) s = s.slice(1);
  if (s.endsWith('|')) s = s.slice(0, -1);
  return s.split('|').map(c => c.trim());
}

function isSeparator(cells) {
  return cells.length > 0 && cells.every(c => /^:?-{2,}:?$/.test(c) || c === '');
}

function buildTable(rows) {
  const body = rows.filter(r => !isSeparator(r));
  if (!body.length) return null;
  const cols = Math.max(...body.map(r => r.length));
  const colWidths = [];
  // first column wider for label tables
  if (cols === 2) colWidths.push(Math.round(CONTENT_DXA * 0.42), CONTENT_DXA - Math.round(CONTENT_DXA * 0.42));
  else if (cols === 3) colWidths.push(Math.round(CONTENT_DXA * 0.52), Math.round(CONTENT_DXA * 0.20), CONTENT_DXA - Math.round(CONTENT_DXA * 0.52) - Math.round(CONTENT_DXA * 0.20));
  else { const w = Math.floor(CONTENT_DXA / cols); for (let i = 0; i < cols; i++) colWidths.push(i === cols - 1 ? CONTENT_DXA - w * (cols - 1) : w); }

  const tableRows = body.map((cells, ri) => new TableRow({
    tableHeader: ri === 0,
    children: Array.from({ length: cols }, (_, ci) => new TableCell({
      width: { size: colWidths[ci], type: WidthType.DXA },
      shading: ri === 0 ? { type: ShadingType.CLEAR, fill: 'EFEFEF', color: 'auto' } : undefined,
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({
        spacing: { line: 276, after: 0 },
        children: parseInline(cells[ci] || '').map(r => {
          if (ri === 0) { r.root.forEach?.(() => {}); }
          return r;
        }),
      })],
    })),
  }));

  // header bold: rebuild header row runs with bold
  tableRows[0] = new TableRow({
    tableHeader: true,
    children: Array.from({ length: cols }, (_, ci) => new TableCell({
      width: { size: colWidths[ci], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: 'EFEFEF', color: 'auto' },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({
        spacing: { line: 276, after: 0 },
        children: [new TextRun({ text: (body[0][ci] || '').replace(/\*\*/g, ''), bold: true })],
      })],
    })),
  });

  return new Table({
    columnWidths: colWidths,
    width: { size: CONTENT_DXA, type: WidthType.DXA },
    rows: tableRows,
  });
}

function convert(mdPath, outPath) {
  const lines = fs.readFileSync(mdPath, 'utf8').split('\n');
  const children = [];
  let i = 0;
  let olInstance = 0;
  let prevWasOl = false;

  while (i < lines.length) {
    const raw = lines[i];
    const line = raw.replace(/\s+$/, '');

    if (!line.trim()) { prevWasOl = false; i++; continue; }

    // table block
    if (line.trim().startsWith('|')) {
      const rows = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) { rows.push(splitRow(lines[i])); i++; }
      const t = buildTable(rows);
      if (t) { children.push(t); children.push(new Paragraph({ text: '', spacing: { after: 120 } })); }
      prevWasOl = false;
      continue;
    }

    let m;
    if ((m = line.match(/^#\s+(.*)$/))) {
      children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: parseInline(m[1]) }));
    } else if ((m = line.match(/^##\s+(.*)$/))) {
      children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: parseInline(m[1]) }));
    } else if ((m = line.match(/^###\s+(.*)$/))) {
      children.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: parseInline(m[1]) }));
    } else if ((m = line.match(/^[-*]\s+(.*)$/))) {
      children.push(new Paragraph({ numbering: { reference: 'bullets', level: 0 }, children: parseInline(m[1]) }));
    } else if ((m = line.match(/^(\d+)\.\s+(.*)$/))) {
      if (!prevWasOl) olInstance++;
      children.push(new Paragraph({ numbering: { reference: 'ordered', level: 0, instance: olInstance }, children: parseInline(m[2]) }));
      prevWasOl = true;
      i++;
      continue;
    } else {
      children.push(new Paragraph({ children: parseInline(line.trim()) }));
    }
    prevWasOl = false;
    i++;
  }

  const doc = new Document({
    creator: 'Attention Is Currency',
    title: path.basename(mdPath, '.md'),
    styles: {
      default: {
        document: {
          run: { font: FONT, size: 23, color: '1A1A1A' },
          paragraph: { spacing: { line: 340, after: 180 } },
        },
        heading1: {
          run: { font: FONT, size: 40, bold: true, color: '000000' },
          paragraph: { spacing: { before: 0, after: 360 } },
        },
        heading2: {
          run: { font: FONT, size: 28, bold: true, color: '000000' },
          paragraph: { spacing: { before: 420, after: 160 }, keepNext: true },
        },
        heading3: {
          run: { font: FONT, size: 24, bold: true, italics: true, color: '000000' },
          paragraph: { spacing: { before: 320, after: 140 }, keepNext: true },
        },
      },
    },
    numbering: {
      config: [
        {
          reference: 'bullets',
          levels: [{
            level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 520, hanging: 280 } } },
          }],
        },
        {
          reference: 'ordered',
          levels: [{
            level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 520, hanging: 280 } } },
          }],
        },
      ],
    },
    sections: [{
      properties: {
        page: {
          size: { width: 12240, height: 15840, orientation: PageOrientation.PORTRAIT },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 120, after: 0 },
            children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: '808080' })],
          })],
        }),
      },
      children,
    }],
  });

  return Packer.toBuffer(doc).then(buf => { fs.writeFileSync(outPath, buf); console.log('wrote', outPath, buf.length, 'bytes'); });
}

const args = process.argv.slice(2);
const outDir = args[args.length - 1];
const files = args.slice(0, -1);
(async () => {
  for (const f of files) {
    const out = path.join(outDir, path.basename(f, '.md') + '.docx');
    await convert(f, out);
  }
})();
