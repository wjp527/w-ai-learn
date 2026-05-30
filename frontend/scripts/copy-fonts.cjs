const fs = require('fs')
const path = require('path')

const root = path.join(__dirname, '..')
const srcDir = path.join(root, 'src', 'assets', 'fonts')
const destDir = path.join(root, 'dist', 'assets', 'fonts')

if (!fs.existsSync(srcDir)) {
  console.warn('[copy-fonts] skip: source missing', srcDir)
  process.exit(0)
}

fs.mkdirSync(destDir, { recursive: true })

for (const name of fs.readdirSync(srcDir)) {
  if (!/\.(woff2?|ttf|otf)$/i.test(name)) continue
  fs.copyFileSync(path.join(srcDir, name), path.join(destDir, name))
  console.log('[copy-fonts]', name)
}
