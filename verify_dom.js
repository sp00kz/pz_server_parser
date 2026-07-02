// Headless render-equivalence check for the JS-table pages.
//   node verify_dom.js OLD.html NEW.html
// Renders both with jsdom (the page JS builds the table on load), then compares
// a signature of the RENDERED output: column headers, every row's cell HTML, and
// each control <select>'s populated options. Exit 0 = identical render, 1 = differs.
const fs = require('fs');
const { JSDOM, VirtualConsole } = require('jsdom');

function render(file) {
  const html = fs.readFileSync(file, 'utf8');
  const errors = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => errors.push(String(e.message || e)));
  const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc });
  const w = dom.window, d = w.document;
  try { d.dispatchEvent(new w.Event('DOMContentLoaded', { bubbles: true })); } catch (_) {}
  try { w.dispatchEvent(new w.Event('load')); } catch (_) {}
  return { d, w, errors };
}

function signature(d) {
  const headers = [...d.querySelectorAll('thead th, table th')].map(t => t.textContent.trim() + '~' + (t.style.textAlign||''));
  const rows = [...d.querySelectorAll('tbody tr')].map(tr =>
    tr.className + '>>' + [...tr.children].map(td => (td.className||'') + '::' + td.innerHTML).join(' | '));
  const selects = [...d.querySelectorAll('select')].map(s =>
    s.id + ':[' + [...s.options].map(o => o.value).join(',') + ']');
  return { headers, rows, selects, rowCount: rows.length };
}

function main() {
  const [oldF, newF] = process.argv.slice(2);
  const a = render(oldF), b = render(newF);
  if (a.errors.length) console.log('  [old jsdom errors]', a.errors.slice(0, 3));
  if (b.errors.length) console.log('  [new jsdom errors]', b.errors.slice(0, 3));
  const sa = signature(a.d), sb = signature(b.d);
  let ok = true;
  const eq = (x, y) => JSON.stringify(x) === JSON.stringify(y);

  if (!eq(sa.headers, sb.headers)) { ok = false; console.log('FAIL headers:\n  old', sa.headers, '\n  new', sb.headers); }
  else console.log(`ok: headers (${sa.headers.length})`);

  if (sa.rowCount !== sb.rowCount) { ok = false; console.log(`FAIL row count: old ${sa.rowCount} new ${sb.rowCount}`); }
  else {
    let diffs = 0;
    for (let i = 0; i < sa.rows.length; i++) if (sa.rows[i] !== sb.rows[i]) {
      if (diffs < 5) { console.log(`FAIL row ${i}:\n  old ${sa.rows[i]}\n  new ${sb.rows[i]}`); }
      diffs++; ok = false;
    }
    if (!diffs) console.log(`ok: ${sa.rowCount} rows identical`);
    else console.log(`  (${diffs} differing rows)`);
  }

  if (!eq(sa.selects, sb.selects)) { ok = false; console.log('FAIL selects:\n  old', sa.selects, '\n  new', sb.selects); }
  else console.log(`ok: ${sa.selects.length} control(s)`);

  console.log('\n' + (ok ? 'RENDER-IDENTICAL ✓' : 'RENDER DIFFERS ✗'));
  process.exit(ok ? 0 : 1);
}
main();
