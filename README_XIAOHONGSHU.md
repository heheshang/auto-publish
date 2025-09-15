# Xiaohongshu Publisher (Java Implementation)

This is a Java implementation of the Xiaohongshu (Little Red Book) content publisher using Playwright for browser automation.

## Features

- **Automated Login**: Handles login with persistent storage state to avoid repeated logins
- **Content Publishing**: Uploads images and publishes posts with title and content
- **Human-like Behavior**: Simulates realistic mouse movements to avoid detection
- **Comprehensive Logging**: Detailed logging throughout the publishing process
- **Error Handling**: Robust error handling and recovery mechanisms
- **Storage State Persistence**: Saves login state for future sessions

## Prerequisites

- Java 11 or higher
- Maven 3.6+
- Playwright browsers (will be downloaded automatically)

## Project Structure

```
src/
├── main/
│   └── java/
│       ├── XiaohongshuPublisher.java    # Main publisher class
│       └── ZhihuPublisher.java          # Existing Zhihu publisher (reference)
└── test/
    └── java/
        └── XiaohongshuPublisherTest.java # Test class
```

## Usage

### Running the Publisher

1. **Compile the project:**
   ```bash
   mvn compile
   ```

2. **Run the main class:**
   ```bash
   mvn exec:java -Dexec.mainClass="XiaohongshuPublisher"
   ```

3. **Or run the test class:**
   ```bash
   mvn exec:java -Dexec.mainClass="XiaohongshuPublisherTest"
   ```

### Configuration

The publisher uses the following configuration:

- **Storage State**: `xhs_storage_state.json` (saves login state)
- **Image Path**: `eb3de882-8cf6-4830-9307-e3f28888e54e-1.png` (default image to upload)
- **Browser Settings**: 
  - User Agent: Chrome 120.0.0.0
  - Viewport: 800x600
  - Headless: false (for debugging)

### Publishing Process

1. **Login Check**: Checks if user is already logged in using storage state
2. **Login Flow**: If not logged in, handles the login process
3. **Navigate to Publish Page**: Goes to the content creation page
4. **Upload Image**: Uploads the specified image file
5. **Fill Content**: Adds title and content to the post
6. **Publish**: Clicks the publish button

### Logging

The publisher provides detailed logging in both English and Chinese:
- Login status and navigation
- Image upload progress
- Content filling status
- Publishing completion

### Error Handling

- Graceful handling of missing image files
- Timeout management for page loads
- Exception handling with detailed error messages
- Browser cleanup in finally blocks

## Customization

### Changing the Image

Modify the `IMAGE_PATH` constant in `XiaohongshuPublisher.java`:

```java
private static final String IMAGE_PATH = "your-image-file.png";
```

### Changing Browser Settings

Adjust the browser configuration in the `run()` method:

```java
Browser.NewContextOptions contextOptions = new Browser.NewContextOptions()
    .setUserAgent("Your User Agent")
    .setViewportSize(1920, 1080)
    .setHeadless(true); // Run in headless mode
```

### Modifying Content

Change the default content in the `publishContent()` method:

```java
titleInput.fill("Your Title");
contentInput.fill("Your Content");
```

## Troubleshooting

### Browser Not Found
If Playwright browsers are not installed, run:
```bash
mvn exec:java -Dexec.mainClass="com.microsoft.playwright.CLI" -Dexec.args="install"
```

### Login Issues
- Check if the storage state file `xhs_storage_state.json` exists
- Manually complete CAPTCHA if prompted during login
- Ensure your credentials are correct

### Image Upload Issues
- Verify the image file exists in the specified path
- Check image format compatibility (PNG, JPG, etc.)
- Ensure image size meets platform requirements

## Security Notes

- Store credentials securely (not hardcoded in the application)
- Use environment variables for sensitive data
- Regularly update storage state files
- Monitor for platform changes that might affect automation

## Comparison with Python Version

This Java implementation maintains feature parity with the original Python version:
- ✅ Persistent login state management
- ✅ Human-like mouse movement simulation
- ✅ Image upload functionality
- ✅ Content publishing workflow
- ✅ Comprehensive logging
- ✅ Error handling and recovery

Additional improvements:
- Better type safety with Java's strong typing
- Enhanced error handling with checked exceptions
- Improved logging with SLF4J
- Maven-based dependency management

## License

This project follows the same licensing as the original Python implementation.
