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

const MESSAGES = [
  { text: "URGENT: Your bank account has been locked. Please click the link to verify your identity.", type: "sms" },
  { text: "Hey John, are we still on for the meeting tomorrow at 10 AM?", type: "text" },
  { text: "Congratulations! You've won a $500 Amazon gift card. Claim it now!", type: "email" },
  { text: "Don't forget to pick up the groceries on your way home.", type: "sms" },
  { text: "Your Netflix subscription will be canceled unless you update your payment method immediately.", type: "email" },
  { text: "I'll send you the quarterly report by Friday.", type: "text" },
  { text: "Meet singles in your area tonight! No credit card required.", type: "sms" },
  { text: "Can you review the pull request I sent earlier?", type: "text" },
  { text: "Limited time offer: get 80% off all designer watches today only.", type: "email" },
  { text: "Happy birthday! Hope you have a wonderful day.", type: "text" },
];

async function capture() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
    colorScheme: 'light',
  });
  
  const page = await context.newPage();
  
  // 1. Landing Page
  console.log('Navigating to landing page...');
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_landing_page.png'), fullPage: true });
  
  // 2. Login Page
  console.log('Navigating to Login Page...');
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
  console.log('Navigating to Analyze Page...');
  await page.click('a[href="/analyze"]');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_analyze_before.png') });
  
  // Submit 10 real predictions through the UI to verify it works
  console.log('Interacting with Analyze Page and submitting predictions...');
  for (let i = 0; i < MESSAGES.length; i++) {
    const msg = MESSAGES[i];
    console.log(`Submitting message ${i + 1}/${MESSAGES.length}...`);
    
    // Fill text
    await page.fill('textarea', msg.text);
    
    // Select message type by clicking its label
    await page.click(`label:has-text("${msg.type.toUpperCase()}")`);
    
    // Submit
    await page.click('button[type="submit"]');
    
    // Wait for the result to appear
    await page.waitForSelector('button:has-text("Clear")', { timeout: 10000 });
    await page.waitForTimeout(1000); // Wait for animation
    
    // Take a screenshot of the last prediction
    if (i === MESSAGES.length - 1) {
      console.log('Capturing Analyze Page (after prediction)...');
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_analyze_after.png'), fullPage: true });
    } else {
      // Click the Clear button to reset the form for the next message
      await page.click('button:has-text("Clear")');
      await page.waitForTimeout(500);
    }
  }
  
  // 6. Prediction History
  console.log('Navigating to History...');
  await page.click('a[href="/history"]');
  await page.waitForTimeout(2000); // Wait for API fetch
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '06_history.png'), fullPage: true });

  // 7. Analytics Dashboard
  console.log('Navigating to Analytics...');
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
  
  await mobilePage.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await mobilePage.fill('#email', 'demo@sentinel.app');
  await mobilePage.fill('#password', 'password123');
  await mobilePage.click('button[type="submit"]');
  await mobilePage.waitForTimeout(3000);
  
  await mobilePage.screenshot({ path: path.join(SCREENSHOT_DIR, '08_mobile_dashboard.png'), fullPage: true });

  await browser.close();
  console.log('All automated interactions completed and screenshots captured successfully.');
}

capture().catch(err => {
  console.error('Error during interaction:', err);
  process.exit(1);
});
