from playwright.sync_api import sync_playwright


def before_all(context):
    context.playwright = sync_playwright().start()


def before_scenario(context, scenario):
    context.browser = context.playwright.chromium.launch()
    context.page = context.browser.new_page()


def after_scenario(context, scenario):
    context.browser.close()


def after_all(context):
    context.playwright.stop()
