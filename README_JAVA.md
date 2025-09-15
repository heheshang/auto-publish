# Zhihu Publisher - Java Implementation

This is a Java implementation of the Zhihu article publisher, converted from the original Python version using Playwright for Java.

## Features

- **Persistent Login State**: Saves and reuses browser storage state to avoid repeated logins
- **Human-like Mouse Movement**: Simulates realistic mouse movements to avoid detection
- **Comprehensive Logging**: Detailed logging with both console and file output
- **Error Handling**: Robust error handling with meaningful error messages
- **CAPTCHA Support**: Manual CAPTCHA handling with user input prompt
- **Article Publishing**: Automated article creation with title, content, cover image, and settings

## Prerequisites

- Java 11 or higher
- Maven 3.6 or higher
- Chrome browser (Playwright will download Chromium automatically)

## Project Structure

```
zhihu-publisher/
├── pom.xml                           # Maven configuration
├── src/main/java/
│   └── ZhihuPublisher.java          # Main application class
├── src/main/resources/
│   └── logback.xml                  # Logging configuration
├── logs/                            # Log files directory
└── zhihu_storage_state.json         # Browser storage state (created after first login)
```

## Building the Project

1. **Clone or download the project**
2. **Install dependencies and browsers**:
   ```bash
   mvn clean compile
   ```
   This will automatically download Playwright browsers.

3. **Build the executable JAR**:
   ```bash
   mvn clean package
   ```

## Running the Application

### Development Mode
```bash
mvn exec:java -Dexec.mainClass="ZhihuPublisher"
```

### Production Mode (using JAR)
```bash
java -jar target/zhihu-publisher-1.0.0-jar-with-dependencies.jar
```

## Configuration

### Cover Image
Place your cover image file named `78bb0f81-242c-4388-81fc-4581364efd09-1.png` in the project root directory, or modify the `COVER_IMAGE_PATH` constant in the code.

### Logging
Logs are written to both console and `logs/zhihu-publisher.log` file. You can adjust logging levels in `src/main/resources/logback.xml`.

## Usage Flow

1. **First Run**: The application will navigate to Zhihu login page
2. **Manual Login**: You'll need to manually handle CAPTCHA and complete login
3. **Storage State**: After successful login, browser state is saved to `zhihu_storage_state.json`
4. **Subsequent Runs**: The application will use saved storage state to skip login
5. **Article Publishing**: Automatically fills title, content, uploads cover image, and publishes

## Key Differences from Python Version

| Feature | Python Version | Java Version |
|---------|---------------|--------------|
| Browser Automation | Playwright Python | Playwright Java |
| Language | Python 3.x | Java 11+ |
| Dependency Management | pip | Maven |
| Logging | print() statements | SLF4J + Logback |
| Error Handling | Basic try-catch | Comprehensive with logging |
| Build System | None required | Maven |

## Troubleshooting

### Browser Not Found
If Playwright can't find browsers, run:
```bash
mvn playwright:install
```

### Login Issues
- Ensure you have a stable internet connection
- Check if Zhihu has changed their login flow
- Verify that the storage state file is being created/loaded properly

### CAPTCHA Problems
- The application pauses for manual CAPTCHA handling
- Complete the CAPTCHA in the browser window
- Press Enter in the console to continue

### Image Upload Issues
- Ensure the cover image file exists in the specified path
- Check file permissions
- Verify image format (PNG, JPG supported)

## Security Notes

- **Storage State**: The `zhihu_storage_state.json` file contains sensitive session data. Keep it secure.
- **Credentials**: Never hardcode credentials in the code
- **CAPTCHA**: Manual handling ensures compliance with anti-bot measures

## Development

### Adding New Features
1. Follow the existing code structure and logging patterns
2. Add appropriate error handling
3. Update this README with new features

### Testing
```bash
# Run with debug logging
mvn exec:java -Dexec.mainClass="ZhihuPublisher" -Dlogback.configurationFile=src/main/resources/logback.xml
```

## License

Same as the original Python project.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `logs/zhihu-publisher.log`
3. Create an issue in the repository
