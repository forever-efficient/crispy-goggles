Feature: Chrome local login

  @local
  Scenario: Login to x.com using local mac Chrome
    Given I use my local Chrome (optional: set CHROME_EXECUTABLE to the binary)
    When I navigate to "https://x.com" and login with env credentials
    Then I should have navigated away from the login page
