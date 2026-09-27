# Gate 3: measuring weight and headroom

## Gate 3 — Weight, measured, not estimated

Never quote a size from memory or from bundlephobia. Bundle the candidate in the scratchpad and
gzip it, which takes about a minute:

```bash
cd "$SCRATCHPAD" && mkdir cand && cd cand && npm init -y
npm i --no-audit --no-fund codemirror @codemirror/lang-markdown @milkdown/crepe esbuild

cat > cm.js <<'EOF'
import { EditorView, basicSetup } from 'codemirror'
import { markdown } from '@codemirror/lang-markdown'
export { EditorView, basicSetup, markdown }
EOF

npx esbuild cm.js --bundle --minify --format=esm --outfile=out.js
node -e "const z=require('zlib'),f=require('fs');const b=f.readFileSync('out.js');
console.log('min',(b.length/1024).toFixed(0),'kB  gzip',(z.gzipSync(b).length/1024).toFixed(0),'kB')"
```

Write the entry file to import **exactly what the integration would import**, not the package
root, or the number is meaningless for a tree-shakeable library.

Then measure the headroom you are spending it against, from the app's own production build:

```bash
npx ng build --configuration production
cd dist/<app>/browser && node -e "
const fs=require('fs'),z=require('zlib');
const idx=fs.readFileSync('index.html','utf8');
let raw=0,gz=0;
for (const f of fs.readdirSync('.').filter(f=>f.endsWith('.js')))
  if (idx.includes(f)) { const b=fs.readFileSync(f); raw+=b.length; gz+=z.gzipSync(b).length }
console.log('initial raw',(raw/1024).toFixed(0),'kB  gzip',(gz/1024).toFixed(0),'kB')"
```

`index.html` referencing the file is what makes a chunk part of the eager graph, which is what the
`initial` budget in `angular.json` measures. Angular budgets are on **raw** bytes, so compare
minified-raw against the budget and quote gzip only as the wire cost.

Decide from the two numbers together. A candidate larger than the remaining headroom is not
automatically rejected: it is rejected *as an eager import*, and the question becomes whether a
dynamic `import()` behind `afterNextRender` is acceptable for that feature. If the library must
run before first paint or before a route guard resolves, lazy loading is not available and the
weight is a hard no.

Back to the index: [angular-dependency-evaluation](angular-dependency-evaluation.md)
