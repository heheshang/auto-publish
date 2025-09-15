import com.microsoft.playwright.*;
import com.microsoft.playwright.options.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Random;
import java.util.regex.Pattern;

public class XiaohongshuPublisher {
    
    private static final Logger logger = LoggerFactory.getLogger(XiaohongshuPublisher.class);
    private static final String STORAGE_STATE_PATH = "xhs_storage_state.json";
    private static final String IMAGE_PATH = "eb3de882-8cf6-4830-9307-e3f28888e54e-1.png";
    private static final Random random = new Random();
    
    public static void main(String[] args) {
        logger.info("Starting Xiaohongshu Publisher application");
        try (Playwright playwright = Playwright.create()) {
            run(playwright);
            logger.info("Xiaohongshu Publisher completed successfully");
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
            .setViewportSize(800, 600)
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
            // Navigate to login page with smart waiting
            logger.info("Navigating to Xiaohongshu creator login page");
            page.navigate("https://creator.xiaohongshu.com/login?selfLogout=true", 
                         new Page.NavigateOptions().setWaitUntil(WaitUntilState.NETWORKIDLE));
            logger.info("Successfully navigated to login page");
            
            // Check if already logged in
            Locator publishNoteLocator = page.locator("div").filter(
                new Locator.FilterOptions().setHasText(Pattern.compile("^发布笔记$"))).nth(1);
            
            if (publishNoteLocator.isVisible()) {
                logger.info("User appears to be logged in, checking login status");
                handleLogin(page);
                // Save storage state after successful login
                logger.info("Saving storage state to: {}", STORAGE_STATE_PATH);
                context.storageState(new BrowserContext.StorageStateOptions()
                    .setPath(storagePath));
            } else {
                logger.info("User already logged in, skipping login flow");
            }
            
            logger.info("已登录");
            
            // Navigate to publish page
            logger.info("Navigating to publish page");
            page.navigate("https://creator.xiaohongshu.com/publish/publish?source=official");
            logger.info("已进入发布页面");
            
            // Start publishing process
            publishContent(page);
            logger.info("Content published successfully");
            
        } catch (Exception e) {
            logger.error("Error during execution", e);
            throw new RuntimeException("Failed to complete Xiaohongshu publishing process", e);
        } finally {
            logger.info("Closing browser");
            browser.close();
        }
    }
    
    private static void handleLogin(Page page) {
        logger.info("Starting login process");
        
        try {
            // Click on image to start login
            logger.info("Clicking login image");
            Locator loginImage = page.locator("img");
            humanLikeMouseMove(page, loginImage);
            loginImage.click();
            
            // Navigate to login page
            logger.info("Navigating to login page");
            page.navigate("https://creator.xiaohongshu.com/login?selfLogout=true");
            
            // Wait for login completion and redirect to home
            logger.info("Waiting for login completion and redirect to home");
            page.waitForURL("https://creator.xiaohongshu.com/new/home", 
                           new Page.WaitForURLOptions().setTimeout(60000));
            logger.info("Login completed successfully");
            
        } catch (Exception e) {
            logger.error("Error during login process", e);
            throw new RuntimeException("Login failed", e);
        }
    }
    
    private static void publishContent(Page page) {
        logger.info("Starting content publishing process");
        
        try {
            // Click upload image/text button
            logger.info("Clicking upload image/text button");
            Locator uploadButton = page.getByText("上传图文").nth(1);
            humanLikeMouseMove(page, uploadButton);
            uploadButton.click();
            logger.info("上传图文");
            
            // Upload image
            logger.info("Uploading image");
            Locator fileInput = page.getByRole(AriaRole.TEXTBOX);
            humanLikeMouseMove(page, fileInput);
            
            Path imagePath = Paths.get(IMAGE_PATH);
            if (imagePath.toFile().exists()) {
                fileInput.setInputFiles(imagePath);
                logger.info("已上传图片");
            } else {
                logger.warn("Image file not found: {}, skipping upload", IMAGE_PATH);
            }
            
            // Fill title
            logger.info("Filling title");
            Locator titleInput = page.getByPlaceholder("填写标题会有更多赞哦～");
            humanLikeMouseMove(page, titleInput);
            titleInput.click();
            titleInput.fill("aerqawerqwer");
            logger.info("已填写标题");
            
            // Fill content
            logger.info("Filling content");
            Locator contentInput = page.getByRole(AriaRole.TEXTBOX).nth(1);
            humanLikeMouseMove(page, contentInput);
            contentInput.click();
            contentInput.fill("adfadsfadfasdf");
            logger.info("已填写内容");
            
            // Publish content
            logger.info("Publishing content");
            Locator publishButton = page.getByRole(AriaRole.BUTTON, 
                new Page.GetByRoleOptions().setName("发布"));
            humanLikeMouseMove(page, publishButton);
            publishButton.click();
            logger.info("已经发布");
            
        } catch (Exception e) {
            logger.error("Error during content publishing", e);
            throw new RuntimeException("Content publishing failed", e);
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
