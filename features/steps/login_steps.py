# Updated step definition to remove the problematic line.
# We will manually take and save a screenshot.

from behave import given, then, when  # type: ignore[import]

from utils.healing_locators import find_element_with_healing


@given("I am on the login page")
def given_i_am_on_the_login_page(context):
    context.page.goto("https://the-internet.herokuapp.com/login")

    # Take a screenshot of the login page.
    # Playwright will automatically save this to your project directory.
    # The first time you run this, it creates the baseline.
    # You will need to manually check this image for correctness.
    context.page.screenshot(path="login_page_baseline.png")


@when("I enter a valid username and password")
def when_i_enter_valid_credentials(context):
    username_field = find_element_with_healing(
        context.page, ["#username", 'input[name="username"]', 'input[id="username"]'],
    )
    username_field.fill("tomsmith")

    password_field = find_element_with_healing(
        context.page, ["#password", 'input[name="password"]'],
    )
    password_field.fill("SuperSecretPassword!")


@when("I click the login button")
def when_i_click_the_login_button(context):
    login_button = find_element_with_healing(
        context.page,
        ['button[type="submit"]', 'page.get_by_role("button", name="Login")'],
    )
    login_button.click()


@then("I should be on the secure area page")
def then_i_should_be_on_secure_area_page(context):
    # This step is for functionality, not visuals
    context.page.wait_for_selector("#flash.success")
    assert "secure" in context.page.url


@then("I should see the success message")
def then_i_should_see_the_success_message(context):
    # This assertion is for text content and visibility
    success_message = context.page.locator("#flash.success")
    assert "You logged into a secure area!" in success_message.text_content()
