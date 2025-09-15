import com.microsoft.playwright.*;
import com.microsoft.playwright.options.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Random;
import java.util.regex.Pattern;

public class ZhihuPublisher {
    
    private static final Logger logger = LoggerFactory.getLogger(ZhihuPublisher.class);
    private static final String STORAGE_STATE_PATH = "zhihu_storage_state.json";
    private static final String COVER_IMAGE_PATH = "78bb0f81-242c-4388-81fc-4581364efd09-1.png";
    private static final Random random = new Random();
    
    public static void main(String[] args) {
        logger.info("Starting Zhihu Publisher application");
        try (Playwright playwright = Playwright.create()) {
            run(playwright);
            logger.info("Zhihu Publisher completed successfully");
        } catch (Exception e) {
            logger.error("Fatal error in main execution", e);
            System.exit(1);
        }
    }
    
    public static void run(Playwright playwright) {
        logger.info("Launching browser with Playwright");
        
        // Browser launch options
        BrowserType.LaunchOptions launchOptions = new BrowserType.LaunchOptions()
            .setHeadless(false)
            .setSlowMo(100);
        
        Browser browser = playwright.chromium().launch(launchOptions);
        logger.info("Browser launched successfully");
        
        // Context options with user agent and viewport settings
        Browser.NewContextOptions contextOptions = new Browser.NewContextOptions()
            .setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            .setViewportSize(1920, 1080)
            .setDeviceScaleFactor(1)
            .setIsMobile(false)
            .setHasTouch(false)
            .setAcceptDownloads(true);
        
        // Load storage state if exists
        Path storagePath = Paths.get(STORAGE_STATE_PATH);
        if (storagePath.toFile().exists()) {
            logger.info("Loading existing storage state from: {}", STORAGE_STATE_PATH);
            contextOptions.setStorageStatePath(storagePath);
        } else {
            logger.info("No existing storage state found, will create new one after login");
        }
        
        BrowserContext context = browser.newContext(contextOptions);
        Page page = context.newPage();
        logger.info("Browser context and page created");
        
        try {
            // Navigate to signin page with smart waiting
            logger.info("Navigating to Zhihu signin page");
            page.navigate("https://www.zhihu.com/signin?next=%2Fcreator", 
                         new Page.NavigateOptions().setWaitUntil(WaitUntilState.NETWORKIDLE));
            logger.info("Successfully navigated to signin page");
            
            // Check if already logged in
            if (!page.url().startsWith("https://www.zhihu.com/creator")) {
                logger.info("User not logged in, proceeding with login flow");
                handleLogin(page);
                // Save storage state after successful login
                logger.info("Saving storage state to: {}", STORAGE_STATE_PATH);
                context.storageState(new BrowserContext.StorageStateOptions()
                    .setPath(storagePath));
            } else {
                logger.info("User already logged in, skipping login flow");
            }
            
            // Publish article
            logger.info("Starting article publishing process");
            publishArticle(page);
            logger.info("Article published successfully");
            
        } catch (Exception e) {
            logger.error("Error during execution", e);
            throw new RuntimeException("Failed to complete Zhihu publishing process", e);
        } finally {
            logger.info("Closing browser");
            browser.close();
        }
    }
    
    private static void handleLogin(Page page) {
        logger.info("Starting login process");
        
        try {
            // Click login button
            Locator loginButton = page.getByRole(AriaRole.BUTTON, 
                new Page.GetByRoleOptions().setName("登录/注册").setExact(true));
            logger.info("Clicking login button");
            humanLikeMouseMove(page, loginButton);
            loginButton.click();
            
            page.waitForLoadState(LoadState.NETWORKIDLE);
            sleepRandom(2, 4);
            
            // Handle login modal if visible
            Locator modal = page.locator(".Modal");
            if (modal.isVisible()) {
                logger.info("Login modal detected, clicking at position");
                humanLikeMouseMove(page, modal);
                modal.click(new Locator.ClickOptions().setPosition(85, 127));
                sleepRandom(3, 5);
            }
            
            // Wait for manual CAPTCHA handling
            logger.info("Waiting for manual CAPTCHA handling");
            System.out.println("请手动处理验证码，完成后按Enter继续...");
            try {
                System.in.read();
            } catch (Exception e) {
                logger.error("Error reading user input", e);
            }
            
            // Wait for login completion and redirect to creator center
            logger.info("Waiting for login completion and redirect to creator center");
            page.waitForURL("https://www.zhihu.com/creator", 
                           new Page.WaitForURLOptions().setTimeout(60000));
            logger.info("Login completed successfully");
            
        } catch (Exception e) {
            logger.error("Error during login process", e);
            throw new RuntimeException("Login failed", e);
        }
    }
    
    private static void publishArticle(Page page) {
        logger.info("Navigating to article writing page");
        
        try {
            // Navigate to article writing page
            page.navigate("https://zhuanlan.zhihu.com/write", 
                         new Page.NavigateOptions().setTimeout(60000));
            logger.info("Successfully navigated to article writing page");
            
            // Fill title
            logger.info("Filling article title");
            Locator titleInput = page.getByPlaceholder("请输入标题（最多 100 个字）");
            humanLikeMouseMove(page, titleInput);
            titleInput.click();
            titleInput.fill("标题标题标题标题标题标题标题标题标题标题标题标题");
            logger.info("Title filled successfully");
            
            // Fill content
            logger.info("Filling article content");
            Locator contentDiv = page.locator("div").filter(
                new Locator.FilterOptions().setHasText(Pattern.compile("^请输入正文$"))).nth(1);
            humanLikeMouseMove(page, contentDiv);
            contentDiv.click();
            
            Locator contentInput = page.getByRole(AriaRole.TEXTBOX).nth(1);
            humanLikeMouseMove(page, contentInput);
            contentInput.fill("内容内容内容内容内容内容内容内容内容内容内容内容内容内容····");
            logger.info("Content filled successfully");
            
            // Upload cover image
            logger.info("Uploading cover image from: {}", COVER_IMAGE_PATH);
            Locator coverLabel = page.locator("label").filter(
                new Locator.FilterOptions().setHasText("添加文章封面"));
            humanLikeMouseMove(page, coverLabel);
            
            Path coverImagePath = Paths.get(COVER_IMAGE_PATH);
            if (coverImagePath.toFile().exists()) {
                coverLabel.setInputFiles(coverImagePath);
                logger.info("Cover image uploaded successfully");
            } else {
                logger.warn("Cover image file not found: {}, skipping upload", COVER_IMAGE_PATH);
            }
            
            // Toggle gift option
            logger.info("Toggling gift option");
            Locator giftLabel = page.locator("label").filter(
                new Locator.FilterOptions().setHasText("开启送礼物"));
            humanLikeMouseMove(page, giftLabel);
            giftLabel.getByRole(AriaRole.IMG).click();
            
            // Confirm settings
            logger.info("Confirming settings");
            Locator confirmButton = page.getByRole(AriaRole.BUTTON, 
                new Page.GetByRoleOptions().setName("确定"));
            humanLikeMouseMove(page, confirmButton);
            confirmButton.click();
            
            // Publish article
            logger.info("Publishing article");
            Locator publishButton = page.getByRole(AriaRole.BUTTON, 
                new Page.GetByRoleOptions().setName("发布"));
            humanLikeMouseMove(page, publishButton);
            publishButton.click();
            logger.info("Article publish button clicked");
            
        } catch (Exception e) {
            logger.error("Error during article publishing", e);
            throw new RuntimeException("Article publishing failed", e);
        }
    }
    
    private static void humanLikeMouseMove(Page page, Locator locator) {
        try {
            BoundingBox box = locator.boundingBox();
            if (box != null) {
                // Random move near the element first
                int steps1 = random.nextInt(6) + 3; // 3-8 steps
                page.mouse().move(
                    box.x + random.nextInt(101) - 50, // -50 to +50 offset
                    box.y + random.nextInt(41) - 20,  // -20 to +20 offset
                    new Mouse.MoveOptions().setSteps(steps1)
                );
                sleepRandom(0.3, 0.8);
                
                // Precise move to center of element
                int steps2 = random.nextInt(4) + 2; // 2-5 steps
                page.mouse().move(
                    box.x + box.width / 2,
                    box.y + box.height / 2,
                    new Mouse.MoveOptions().setSteps(steps2)
                );
                sleepRandom(0.2, 0.5);
            } else {
                logger.warn("Could not get bounding box for locator, skipping mouse movement simulation");
            }
        } catch (Exception e) {
            logger.error("Error during mouse movement simulation", e);
        }
    }
    
    private static void sleepRandom(double minSeconds, double maxSeconds) {
        try {
            long millis = (long) ((minSeconds + random.nextDouble() * (maxSeconds - minSeconds)) * 1000);
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            logger.warn("Sleep interrupted", e);
        }
    }
}
