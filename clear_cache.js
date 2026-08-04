// I am creating a script to clear the Next.js cache just in case it's a caching issue!
const fs = require('fs');
const path = require('path');

const nextDir = path.join(__dirname, 'frontend', '.next');
if (fs.existsSync(nextDir)) {
  fs.rmSync(nextDir, { recursive: true, force: true });
  console.log('✅ Cleared .next cache');
} else {
  console.log('No cache found');
}
