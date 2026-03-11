const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
    try {
        const browser = await puppeteer.launch({
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        const page = await browser.newPage();
        
        // กำหนดขนาดหน้าจอให้ใหญ่และคมชัดพอดี
        await page.setViewport({ width: 1440, height: 1080, deviceScaleFactor: 2 });
        
        const filePath = "file:///" + path.resolve('System Architecture.html').replace(/\\/g, '/');
        console.log(`Loading: ${filePath}`);
        
        // รอให้โหลดเสร็จสมบูรณ์ รวมถึง network idle
        await page.goto(filePath, { waitUntil: 'networkidle0' });
        
        // เผื่อเวลาให้ Font Awesome และ Tailwind โหลดเสร็จเรียบร้อย
        await new Promise(r => setTimeout(r, 2000));
        
        const outputPath = path.resolve('System Architecture.png');
        await page.screenshot({ path: outputPath, fullPage: true });
        
        await browser.close();
        console.log(`Screenshot saved successfully to ${outputPath}`);
    } catch (err) {
        console.error('Error generating screenshot:', err);
    }
})();
