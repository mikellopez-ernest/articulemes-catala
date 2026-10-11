import fitz, glob, os, base64, json
from PIL import Image
from io import BytesIO
root='/mnt/data/articulemes_cat'; doc=fitz.open(glob.glob('/mnt/data/*.pdf')[0]); assets={}
# Coordinates normalized to page screenshots 768x1024. Crop the photograph inside border, not decorative border.
boxes3=[('A',(62,123,344,331)),('E',(437,121,709,333)),('I',(62,436,344,645)),('O',(437,431,713,643)),('U',(215,725,531,927))]
keys=[['B','D','F','G','J','K'],['L','LL','M','N','NY','P'],['R','RR','S','T','V','X']]
for pi in range(2,6):
    if pi==2: specs=boxes3
    else:
        specs=[]
        for row in range(3):
            for col in range(2):
                x0,x1=(62,340) if col==0 else (435,712)
                y0,y1=[(124,319),(426,618),(735,922)][row]
                specs.append((keys[pi-3][row*2+col],(x0,y0,x1,y1)))
    page=doc[pi]; mat=fitz.Matrix(2,2); pix=page.get_pixmap(matrix=mat,alpha=False); im=Image.open(BytesIO(pix.tobytes('png')))
    for key,(x0,y0,x1,y1) in specs:
        # coordinate screenshot (768x1024) to rendered page actual
        bb=tuple(round(v*(im.width/768 if i%2==0 else im.height/1024)) for i,v in enumerate((x0,y0,x1,y1)))
        im.crop(bb).save(f'{root}/assets/{key}.jpg',quality=87,optimize=True)
        with open(f'{root}/assets/{key}.jpg','rb') as f: assets[key]='data:image/jpeg;base64,'+base64.b64encode(f.read()).decode()
print('Extracted',len(assets),'images')
# Embedded resources make the page standalone and easy to share.
html=r'''<!doctype html><html lang="ca"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Articulemes · Generador en català</title><style>
:root{font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#243044;background:#f5f7fb}*{box-sizing:border-box}body{margin:0}main{max-width:1050px;margin:32px auto;padding:0 20px}h1{margin:0;font-size:30px}p{line-height:1.5;color:#536175}.panel{background:white;border:1px solid #e2e8f0;border-radius:18px;padding:24px;margin-top:18px;box-shadow:0 4px 18px #1231 0}.bar{display:flex;gap:10px;flex-wrap:wrap;align-items:center}textarea{width:100%;min-height:92px;padding:14px;border:1px solid #c7d0da;border-radius:10px;font-size:20px;resize:vertical}button{cursor:pointer;background:#225f9a;color:white;border:none;padding:10px 16px;border-radius:9px;font-weight:600}button.secondary{background:#e8f0f9;color:#1f4974}button:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid orange}label{display:inline-flex;gap:6px;align-items:center}#result{margin-top:20px}.word{break-inside:avoid;display:inline-flex;vertical-align:top;flex-direction:column;gap:9px;margin:4px 18px 18px 0;padding:14px;border:1px solid #e2e8f0;border-radius:13px;background:#fff}.word>strong{text-align:center;font-size:21px}.sounds{display:flex;flex-wrap:wrap;gap:7px}.sound{width:86px;position:relative;text-align:center}.sound img{display:block;width:86px;height:74px;object-fit:cover;border:2px solid #d4deea;border-radius:10px}.sound select{width:100%;margin-top:4px;padding:4px 1px;font-size:13px;border:1px solid #ccd3db;background:white;border-radius:5px}.sound .gr{font-size:12px;color:#64748b;height:19px;overflow:hidden}.notice{font-size:13px;color:#865500;margin-top:10px;line-height:1.5}.muted{font-size:13px;color:#64748b}.legend{display:flex;flex-wrap:wrap;gap:10px}.legend img{width:60px;height:53px;object-fit:cover;border-radius:6px}.item{text-align:center;font-size:12px}.warn{background:#fff8e7;border-radius:9px;padding:12px;color:#745106}.footer{margin:22px 0;color:#66758b;font-size:12px}@media print{body{background:white}main{max-width:100%;margin:0}.no-print{display:none!important}.panel{border:0;box-shadow:none;padding:0}.word{margin:4px 12px 15px 0}.sound select{appearance:none;border:0;text-align:center}.sound img{print-color-adjust:exact} h1{font-size:20px}}@media(max-width:640px){main{margin:12px auto;padding:0 12px}.panel{padding:14px}.sound,.sound img{width:69px}.sound img{height:58px}}
</style></head><body><main><div class="no-print"><h1>Articulemes · Català</h1><p>Prototip educatiu: escriu paraules i ajusta els sons abans d'imprimir la fitxa. Les correspondències són aproximacions ortogràfiques, no una transcripció fonètica validada.</p></div><section class="panel"><div class="no-print"><label for="text">Text a convertir</label><textarea id="text" spellcheck="false">mama papa gat nyap lluna</textarea><div class="bar"><button id="convert">Genera els articulemes</button><button id="print" class="secondary">Imprimeix / Desa com a PDF</button><label><input id="showwords" type="checkbox" checked> Mostra les paraules</label></div><div id="warnings" class="notice"></div></div><div id="result" aria-live="polite"></div></section><section class="panel no-print"><h2>Inventari de 23 articulemes</h2><div class="legend" id="legend"></div><p class="muted">Imatges del document «Articulemes nivell inicial · Comunicar-nos Català», coordinat per Belinda Haro Castilla. Material CC BY-NC-SA. Ús no comercial, mantenint-ne l'atribució i les condicions de la llicència. No distribuir comercialment.</p></section><div class="footer">Fotografies: Comunicar_Nos · Belinda Haro Castilla · Siembra Estrellas. Aquesta eina és un prototip independent i no està afiliada amb el projecte original.</div></main><script>
const PICTURES = __IMAGES__;
const KEYS = ['A','E','I','O','U','B','D','F','G','J','K','L','LL','M','N','NY','P','R','RR','S','T','V','X'];
const textEl=document.getElementById('text'), out=document.getElementById('result'),warnings=document.getElementById('warnings');
const alertSet=new Set();
function phonemes(word){let w=word.toLocaleLowerCase('ca'), out=[],i=0;const push=(symbol,segment,note)=>{out.push({symbol,segment,note});if(note)alertSet.add(note)};
while(i<w.length){let rem=w.slice(i),ch=w[i],next=w[i+1]||'',two=rem.slice(0,2),three=rem.slice(0,3);
if(three==='tge'||three==='tgi'){push('J',three,'Cal revisar els sons representats per «tg/tj»: la foto disponible només n’aproxima l’articulació.');i+=3;continue}
if(two==='tj'){push('J',two,'Cal revisar els sons representats per «tg/tj».');i+=2;continue}
if(['ny','ll','rr','tx','ss'].includes(two)){push(({ny:'NY',ll:'LL',rr:'RR',tx:'X',ss:'S'})[two],two);i+=2;continue}
if(two==='qu'&&'eèéií'.includes(w[i+2]||'')){push('K',two);i+=2;continue}
if(two==='gu'&&'eèéií'.includes(w[i+2]||'')){push('G',two);i+=2;continue}
if(two==='ig'&&i+2===w.length){push('X',two,'El dígraf final «ig» exigeix comprovació segons la paraula.');i+=2;continue}
if(two==='ix'){push('X',two,'La «ix» pot tenir realitzacions diferents segons el context.');i+=2;continue}
if(ch==='h'){i++;continue}
if(ch==='ç'){push('S',ch);i++;continue}
if(ch==='c'){push('eèéií'.includes(next)?'S':'K',ch);i++;continue}
if(ch==='g'){push('eèéií'.includes(next)?'J':'G',ch);i++;continue}
if(ch==='q'){push('K',ch,'Cal revisar la seqüència amb «q».');i++;continue}
if(ch==='x'){push('X',ch,'La lletra «x» no sempre correspon al mateix so.');i++;continue}
if(ch==='r'){push(i===0?'RR':'R',ch,'La pronunciació de «r» depèn de la posició i el context.');i++;continue}
if(ch==='s'||ch==='z'){push('S',ch,'El document agrupa S/Z; no distingeix totes les realitzacions sonores.');i++;continue}
if(ch==='v'){push('V',ch,'La distinció B/V depèn de la varietat de català.');i++;continue}
if('àáa'.includes(ch)){push('A',ch);i++;continue}
if('èée'.includes(ch)){push('E',ch,'Les vocals E/O poden variar segons accentuació i dialecte; el material només conté 5 vocals.');i++;continue}
if('ìíïi'.includes(ch)){push('I',ch);i++;continue}
if('òóo'.includes(ch)){push('O',ch,'Les vocals E/O poden variar segons accentuació i dialecte; el material només conté 5 vocals.');i++;continue}
if('ùúüu'.includes(ch)){push('U',ch);i++;continue}
let fallback={b:'B',d:'D',f:'F',j:'J',k:'K',l:'L',m:'M',n:'N',p:'P',t:'T'}[ch];
if(fallback){push(fallback,ch);i++;continue}push(null,ch,'No s’ha pogut identificar un símbol.');i++}
return out}
function createWord(word){let div=document.createElement('div');div.className='word';let strong=document.createElement('strong');strong.textContent=word;strong.className='word-label';div.append(strong);let row=document.createElement('div');row.className='sounds';for(let item of phonemes(word)){let cell=document.createElement('div');cell.className='sound';let img=document.createElement('img');img.alt='Articulema '+(item.symbol||'?');if(item.symbol)img.src=PICTURES[item.symbol];let g=document.createElement('div');g.className='gr';g.textContent=item.segment;cell.append(img,g);let select=document.createElement('select');select.title='Tria manualment el so correcte';for(let key of ['',...KEYS]){let op=document.createElement('option');op.value=key;op.textContent=key||'—';op.selected=key===item.symbol;select.append(op)}select.addEventListener('change',()=>{if(select.value){img.src=PICTURES[select.value];img.alt='Articulema '+select.value;img.style.visibility='visible'}else img.style.visibility='hidden'});cell.append(select);row.append(cell)}div.append(row);return div}
function render(){alertSet.clear();out.replaceChildren();let content=textEl.value.normalize('NFC');let words=content.match(/[a-zA-ZàáèéíìïòóúùüçñÀÁÈÉÍÌÏÒÓÚÙÜÇÑ·]+/g)||[];for(let word of words.slice(0,120))out.append(createWord(word));document.querySelectorAll('.word-label').forEach(x=>x.style.display=document.getElementById('showwords').checked?'':'none');let notes=[...alertSet];warnings.textContent=(words.length>120?'Només es mostren les primeres 120 paraules. ':'')+(notes.length?'Revisió logopèdica recomanada: '+notes.join(' '):'Revisa la pronunciació abans d’utilitzar la fitxa; el català presenta neutralitzacions i variants dialectals.');}
document.getElementById('convert').onclick=render;document.getElementById('print').onclick=()=>window.print();document.getElementById('showwords').onchange=()=>document.querySelectorAll('.word-label').forEach(x=>x.style.display=document.getElementById('showwords').checked?'':'none');let legend=document.getElementById('legend');for(let key of KEYS){let d=document.createElement('div');d.className='item';let im=document.createElement('img');im.src=PICTURES[key];im.alt=key;d.append(im,document.createElement('div'));d.lastChild.textContent=key;legend.append(d)}render();</script></body></html>'''
with open(f'{root}/Articulemes_catala.html','w') as f:f.write(html.replace('__IMAGES__',json.dumps(assets)))
