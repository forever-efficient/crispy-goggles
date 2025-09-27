Feature: Secure Login
  As a user
  I want to log in to the secure area
  So that I can access my account

  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter a valid username and password
    And I click the login button
    Then I should be on the secure area page
    And I should see the success message