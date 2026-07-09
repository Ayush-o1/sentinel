import { chromium, devices } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SCREENSHOT_DIR = path.resolve(__dirname, '../docs/assets/screenshots');

// Ensure directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function capture() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2, // Retina display for professional look
    colorScheme: 'light',
  });
  
  const page = await context.newPage();
  
  // Wait for the app to be ready
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });

  // 1. Landing Page
  console.log('Capturing Landing Page...');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_landing_page.png'), fullPage: true });
  
  // 2. Login Page
  console.log('Capturing Login Page...');
  await page.click('a[href="/login"]');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_login_page.png') });
  
  // Login to the app
  console.log('Logging in...');
  await page.fill('#email', 'demo@sentinel.app');
  await page.fill('#password', 'password123');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(3000); // Wait for dashboard to load
  
  // 3. Dashboard
  console.log('Capturing Dashboard...');
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_dashboard.png'), fullPage: true });

  // 4. Analyze Page (before prediction)
  console.log('Capturing Analyze Page (before)...');
  await page.click('a[href="/analyze"]');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_analyze_before.png') });
  
  // 5. Analyze Page (after prediction)
  console.log('Capturing Analyze Page (after)...');
  await page.fill('textarea', 'URGENT: Your account has been suspended. Click here to verify your identity.');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(5000); // Wait for prediction to finish and LIME explanation to render
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_analyze_after.png'), fullPage: true });
  
  // 6. Prediction History
  console.log('Capturing History...');
  await page.click('a[href="/history"]');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '06_history.png'), fullPage: true });

  // 7. Analytics Dashboard
  console.log('Capturing Analytics...');
  await page.click('a[href="/analytics"]');
  await page.waitForTimeout(3000); // Wait for charts to animate
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '07_analytics.png'), fullPage: true });

  // 8. Mobile responsive view (Dashboard)
  console.log('Capturing Mobile Dashboard...');
  const mobileContext = await browser.newContext({
    ...devices['iPhone 13'],
    deviceScaleFactor: 2,
  });
  const mobilePage = await mobileContext.newPage();
  
  // Login on mobile first
  await mobilePage.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await mobilePage.fill('#email', 'demo@sentinel.app');
  await mobilePage.fill('#password', 'password123');
  await mobilePage.click('button[type="submit"]');
  await mobilePage.waitForTimeout(3000); // Wait for dashboard to load
  
  await mobilePage.screenshot({ path: path.join(SCREENSHOT_DIR, '08_mobile_dashboard.png'), fullPage: true });

  await browser.close();
  console.log('All screenshots captured successfully.');
}

capture().catch(err => {
  console.error('Error taking screenshots:', err);
  process.exit(1);
});
