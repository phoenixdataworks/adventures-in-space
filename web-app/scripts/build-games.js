/**
 * Build script for compiling Pygame games with Pygbag
 * This script compiles each game and copies the output to the public/games directory
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Game configurations
const games = [
  {
    id: 'adventures-in-space',
    sourceDir: '../adventures-in-space',
    mainFile: 'main.py',
  },
  {
    id: 'santa-vs-grunch',
    sourceDir: '../santa-vs-grunch',
    mainFile: 'main.py',
  },
  {
    id: 'snake-jump',
    sourceDir: '../snake-jump',
    mainFile: 'snake-jump.py',
  },
  {
    id: 'bible_stories',
    sourceDir: '../bible_stories',
    mainFile: 'main.py',
  },
  {
    id: 'joseph_mary_run',
    sourceDir: '../joseph_mary_run',
    mainFile: 'main.py',
  },
];

const rootDir = path.resolve(__dirname, '..');
const gamesOutputDir = path.join(rootDir, 'public', 'games');

// Create output directory
if (!fs.existsSync(gamesOutputDir)) {
  fs.mkdirSync(gamesOutputDir, { recursive: true });
}

console.log('🎮 Building Pygame games with Pygbag...\n');

let successCount = 0;
let failCount = 0;

for (const game of games) {
  const sourceDir = path.resolve(__dirname, game.sourceDir);
  const outputDir = path.join(gamesOutputDir, game.id);
  
  console.log(`📦 Building ${game.id}...`);
  
  if (!fs.existsSync(sourceDir)) {
    console.log(`   ⚠️  Source directory not found: ${sourceDir}`);
    failCount++;
    continue;
  }
  
  const mainFile = path.join(sourceDir, game.mainFile);
  if (!fs.existsSync(mainFile)) {
    console.log(`   ⚠️  Main file not found: ${mainFile}`);
    failCount++;
    continue;
  }
  
  try {
    // Run pygbag to build the game
    // --build flag creates a static build suitable for deployment
    const buildDir = path.join(sourceDir, 'build', 'web');
    
    console.log(`   📁 Source: ${sourceDir}`);
    console.log(`   🔨 Running pygbag...`);
    
    execSync(`cd "${sourceDir}" && python -m pygbag --build "${game.mainFile}"`, {
      stdio: 'pipe',
      timeout: 300000, // 5 minute timeout
    });
    
    // Check if build was successful
    if (fs.existsSync(buildDir)) {
      // Copy build output to public/games directory
      if (fs.existsSync(outputDir)) {
        fs.rmSync(outputDir, { recursive: true });
      }
      
      copyDirSync(buildDir, outputDir);
      console.log(`   ✅ Successfully built ${game.id}`);
      successCount++;
    } else {
      console.log(`   ❌ Build directory not found after pygbag`);
      failCount++;
    }
  } catch (error) {
    console.log(`   ❌ Error building ${game.id}:`);
    console.log(`      ${error.message}`);
    failCount++;
  }
  
  console.log('');
}

console.log('─'.repeat(50));
console.log(`\n📊 Build Summary:`);
console.log(`   ✅ Successful: ${successCount}`);
console.log(`   ❌ Failed: ${failCount}`);
console.log(`   📁 Output: ${gamesOutputDir}\n`);

if (failCount > 0) {
  console.log('⚠️  Some games failed to build. Make sure pygbag is installed:');
  console.log('   pip install pygbag\n');
}

/**
 * Recursively copy a directory
 */
function copyDirSync(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });
  
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    if (entry.isDirectory()) {
      copyDirSync(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}


