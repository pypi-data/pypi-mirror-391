# Drupal Behat Command

Run Behat functional tests.

## Usage

```bash
/drupal/behat                 # Run all tests
/drupal/behat @tag            # Run tests with specific tag
/drupal/behat feature.feature # Run specific feature file
```

## Command Execution

### Read Drupal Configuration

Load configuration from `sessions/sessions-config.json`:
- `behat_command`: Behat command (default: `ddev robo behat`)

### Determine Test Scope

1. If tag provided (`@tag`), run tests with that tag
2. If feature file provided, run that specific feature
3. Otherwise, run all tests

### Build Behat Command

**Run all tests**:
```bash
{behat_command}
```

**Run with tag**:
```bash
{behat_command} {tag}
```

**Run specific feature**:
```bash
{behat_command} {feature_file}
```

### Execute Tests

Run command and capture output with real-time streaming.

### Display Results

**On successful test run**:
```
✅ Behat Tests: All tests passed

   Features: 12
   Scenarios: 45
   Steps: 234

   Passed: 234
   Failed: 0
   Skipped: 0
   Pending: 0

   Time: 3m 24s
```

**On test failures**:
```
❌ Behat Tests: {failure_count} failures

   Failed Scenarios:
   ❌ behat/features/user_login.feature:12
      Scenario: User can log in with valid credentials
      Step failed: When I fill in "Password" with "wrong_password"
      Error: Element not found

   ❌ behat/features/article_creation.feature:25
      Scenario: Create new article
      Step failed: Then I should see "Article created"
      Error: Text not found on page

   Summary:
   Scenarios: 45 (43 passed, 2 failed)
   Steps: 234 (230 passed, 4 failed)
   Time: 2m 45s

   Screenshots saved:
   - behat/screenshots/user_login-failed.png
   - behat/screenshots/article_creation-failed.png
```

**On partial run**:
```
✅ Behat Tests: Tag @smoke passed

   Tag: @smoke
   Scenarios: 8
   Steps: 45

   All smoke tests passed

   Time: 45s
```

### Update State

If all tests pass, update state:

```json
{
  "drupal": {
    "quality_gates_passed": ["behat"],
    "pending_tests": false
  }
}
```

## Examples

### Run All Tests

```bash
/drupal/behat
```

Output:
```
🧪 Running all Behat tests...

Feature: User Authentication
  ✅ Scenario: User can log in
  ✅ Scenario: User can log out
  ✅ Scenario: Invalid credentials rejected

Feature: Article Management
  ✅ Scenario: Create article
  ✅ Scenario: Edit article
  ✅ Scenario: Delete article

Feature: Content Display
  ✅ Scenario: View article list
  ✅ Scenario: View single article

✅ All tests passed

   Features: 3
   Scenarios: 8
   Steps: 42
   Time: 1m 32s
```

### Run Specific Tag

```bash
/drupal/behat @smoke
```

Output:
```
🧪 Running tests tagged: @smoke

Feature: Critical Paths
  ✅ @smoke Scenario: Homepage loads
  ✅ @smoke Scenario: User can log in
  ✅ @smoke Scenario: Search works

✅ Smoke tests passed

   Scenarios: 3/3
   Time: 28s
```

### Run Specific Feature

```bash
/drupal/behat behat/features/user_registration.feature
```

Output:
```
🧪 Running: user_registration.feature

Feature: User Registration

  ✅ Scenario: New user can register
     ✅ Given I am on "/user/register"
     ✅ When I fill in "Username" with "newuser"
     ✅ And I fill in "Email" with "newuser@example.com"
     ✅ And I fill in "Password" with "SecurePass123"
     ✅ And I press "Create account"
     ✅ Then I should see "Registration successful"

  ✅ Scenario: Duplicate email rejected
     ✅ Given a user exists with email "existing@example.com"
     ✅ When I register with email "existing@example.com"
     ✅ Then I should see "Email already in use"

✅ Feature passed

   Scenarios: 2/2
   Steps: 11/11
   Time: 15s
```

## Failed Test Details

When tests fail, detailed information is provided:

```bash
/drupal/behat @article
```

Output:
```
🧪 Running tests tagged: @article

Feature: Article Management

  ❌ @article Scenario: Create article with image
     ✅ Given I am logged in as an editor
     ✅ And I am on "/node/add/article"
     ✅ When I fill in "Title" with "Test Article"
     ✅ And I fill in "Body" with "Article content"
     ❌ And I attach the file "test-image.jpg" to "Image"
        Error: Element matching css "input[type='file']" not found

❌ Tests failed

   Scenarios: 1 failed, 4 passed
   Steps: 4 passed, 1 failed
   Time: 42s

   Failure Details:
   File: behat/features/article_management.feature:45
   Step: And I attach the file "test-image.jpg" to "Image"
   Error: Behat\Mink\Exception\ElementNotFoundException
   Screenshot: behat/screenshots/create-article-with-image-failed.png

   Debugging:
   1. Check screenshot: open behat/screenshots/create-article-with-image-failed.png
   2. Verify selector: input[type='file']
   3. Check if image field is enabled on article content type
```

## Test Creation

If invoked during quality gate with user approval:

```
📋 Creating Behat tests for: {feature_name}

   Analyzing feature requirements...
   ✅ Identified 3 user workflows
   ✅ Created test scenarios
   ✅ Added step definitions

   Created: behat/features/{feature_name}.feature

   Scenarios:
   - Basic functionality (happy path)
   - Error handling
   - Edge cases

   Run tests:
   /drupal/behat @{feature_tag}
```

## Configuration

### behat.yml

Ensure `behat/behat.yml` exists:

```yaml
default:
  suites:
    default:
      contexts:
        - FeatureContext
        - Drupal\DrupalExtension\Context\DrupalContext
        - Drupal\DrupalExtension\Context\MinkContext

  extensions:
    Drupal\MinkExtension:
      base_url: http://localhost
      selenium2:
        wd_host: http://selenium:4444/wd/hub
    Drupal\DrupalExtension:
      api_driver: drupal
      drupal:
        drupal_root: /var/www/html/web
      selectors:
        message_selector: '.messages'
        error_message_selector: '.messages--error'
```

## Error Handling

### Behat Not Found

```
❌ Behat not available at: {behat_command}

Install Behat:
  composer require --dev behat/behat drupal/drupal-extension

Configure Behat:
  Create behat/behat.yml with Drupal extension
```

### Screenshot Directory Missing

```
⚠️  Screenshot directory not found

   Creating: behat/screenshots/

   Screenshots will be saved here when tests fail.
```

### Selenium Not Running

```
❌ Selenium server not responding

   Start Selenium:
   ddev start
   ddev exec selenium-standalone start

   Or update behat.yml to use Chrome headless
```

## Integration with Quality Gates

Behat tests integrate with Drupal quality gate protocol:

- **On task completion**: User prompted to create tests
- **Test creation**: Automatic test generation based on feature
- **Test execution**: Validates implementation
- **Results**: Feed into quality gate pass/fail

## Performance

**Test Speed**:
- Unit-style tests: < 1 second per scenario
- Integration tests: 2-5 seconds per scenario
- Full browser tests: 10-30 seconds per scenario

**Optimization Tips**:
- Use `@javascript` tag only when needed
- Tag scenarios for selective running
- Run smoke tests frequently, full suite less often
