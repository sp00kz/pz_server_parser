// Verify food recipe-mode renders identically: node verify_food_recipe.js OLD NEW RECIPE
const fs=require('fs'); const {JSDOM,VirtualConsole}=require('jsdom');
function sig(file, recipe){
  const dom=new JSDOM(fs.readFileSync(file,'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:new VirtualConsole()});
  const w=dom.window,d=w.document;
  try{w.dispatchEvent(new w.Event('load'));}catch(e){}
  const sel=d.querySelector('#recipe'); sel.value=recipe;
  sel.dispatchEvent(new w.Event('change',{bubbles:true}));
  const headers=[...d.querySelectorAll('th')].map(t=>t.textContent.trim()+'~'+(t.style.textAlign||''));
  const rows=[...d.querySelectorAll('tbody tr')].map(tr=>[...tr.children].map(td=>(td.className||'')+'::'+td.innerHTML).join('|'));
  const cap=(d.querySelector('#cap')||{}).innerHTML||'';
  const cnt=(d.querySelector('#count')||{}).textContent||'';
  return {s:JSON.stringify({headers,rows,cap,cnt}),n:rows.length};
}
const [oldF,newF,recipe]=process.argv.slice(2);
const a=sig(oldF,recipe), b=sig(newF,recipe);
if(a.s===b.s){console.log(`recipe "${recipe}": IDENTICAL (${b.n} ingredients)`);}
else{const A=JSON.parse(a.s),B=JSON.parse(b.s);console.log(`recipe "${recipe}": DIFFERS`);
  if(JSON.stringify(A.headers)!==JSON.stringify(B.headers))console.log(' headers old',A.headers,'new',B.headers);
  if(A.cnt!==B.cnt)console.log(' count old:',A.cnt,'new:',B.cnt);
  if(A.cap!==B.cap)console.log(' cap old:',A.cap.slice(0,140),'\n     new:',B.cap.slice(0,140));
  for(let i=0;i<Math.max(A.rows.length,B.rows.length);i++)if(A.rows[i]!==B.rows[i]){console.log(` row ${i} old: ${(A.rows[i]||'').slice(0,150)}\n        new: ${(B.rows[i]||'').slice(0,150)}`);break;}
  process.exit(1);}
