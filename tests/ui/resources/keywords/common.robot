*** Settings ***
Documentation     Shared Browser/Robot keywords and selectors for the Toolshop UI tests.
...               Provides a stable interface for UI suites:
...               - Browser lifecycle (open/close)
...               - Common waits (app readiness, product list readiness)
...               - Failure diagnostics (deterministic screenshot naming)
...               - Login helper (demo user)
...               - Cart navigation helper (/checkout)
Library           Browser    auto_closing_level=SUITE
Library           String
Library           DateTime

*** Variables ***
${BASE_URL}    %{BASE_URL=http://localhost:4200}
${HEADLESS}    %{HEADLESS=true}

# Cart in this app lives under /checkout
${CART_PATH}   /checkout

# Demo credentials (used by login smoke / optional keywords)
${EMAIL}       %{DEMO_EMAIL=customer@practicesoftwaretesting.com}
${PASSWORD}    %{DEMO_PASSWORD=welcome01}

# Selectors (centralized -> easier maintenance)
${NAVBAR}              css=nav.navbar
${PRODUCT_CARD}        css=a.card[data-test^="product-"]
${NAV_SIGN_IN}         css=[data-test="nav-sign-in"]
${LOGIN_EMAIL}         css=input#email
${LOGIN_PASSWORD}      css=input#password
${LOGIN_SUBMIT}        css=[data-test="login-submit"]

*** Keywords ***
Open Toolshop
    [Documentation]    Open a new browser session, navigate to the Toolshop, and wait until the UI is ready.
    New Browser    chromium    headless=${HEADLESS}    chromiumSandbox=false
    New Context    viewport={'width': 1280, 'height': 800}
    New Page       ${BASE_URL}
    Register Keyword To Run On Failure    Capture Failure Screenshot
    Wait Until Toolshop Ready

Capture Failure Screenshot
    [Documentation]    Capture a screenshot on failure with a deterministic, sanitized filename.
    ...                Filename format: FAIL__<suite>__<test>__<timestamp>.png
    ${suite}=    Get Variable Value    ${SUITE NAME}    unknown-suite
    ${test}=     Get Variable Value    ${TEST NAME}     unknown-test

    ${suite}=    Replace String Using Regexp    ${suite}    [^A-Za-z0-9._-]+    _
    ${test}=     Replace String Using Regexp    ${test}     [^A-Za-z0-9._-]+    _

    ${ts}=       Get Current Date    result_format=%Y%m%d-%H%M%S
    Take Screenshot    filename=FAIL__${suite}__${test}__${ts}.png

Wait Until Toolshop Ready
    [Documentation]    Wait until the page body and main navbar are visible (basic app readiness).
    Wait For Elements State    css=body    visible    timeout=20s
    Wait For Elements State    ${NAVBAR}   visible    timeout=20s

Close Toolshop
    [Documentation]    Close the browser session.
    Close Browser

Wait For At Least One Product Card
    [Documentation]    Wait until at least one product card is visible on the listing.
    ...                Uses retries to tolerate initial load delays.
    Wait Until Keyword Succeeds    60s    2s    First Product Card Should Be Visible

First Product Card Should Be Visible
    [Documentation]    Assert the first product card is visible (avoids strict-mode violations).
    # Avoid strict mode violation by targeting the first match explicitly
    Wait For Elements State    ${PRODUCT_CARD} >> nth=0    visible    timeout=5s

Login As Demo User
    [Documentation]    Log in using demo credentials and wait until the login flow completes.
    Wait For Elements State    ${NAV_SIGN_IN}     visible    timeout=20s
    Click    ${NAV_SIGN_IN}

    Wait For Elements State    ${LOGIN_EMAIL}     visible    timeout=20s
    Wait For Elements State    ${LOGIN_PASSWORD}  visible    timeout=20s
    Fill Text    ${LOGIN_EMAIL}     ${EMAIL}
    Fill Text    ${LOGIN_PASSWORD}  ${PASSWORD}
    Click        ${LOGIN_SUBMIT}

    Wait For Login To Complete

Wait For Login To Complete
    [Documentation]    Wait until login is considered complete (URL no longer contains /login).
    Wait Until Keyword Succeeds    20s    500ms    Login Should Be Completed

Login Should Be Completed
    [Documentation]    Single-attempt check used by the retry wrapper for login completion.
    ${url}=    Get Url
    Should Not Contain    ${url}    /login
    Wait For Elements State    ${NAVBAR}    visible    timeout=10s

Go To Cart
    [Documentation]    Navigate directly to the cart/checkout page and wait until it is visible.
    # Deterministic: cart is the /checkout page in this app
    Go To    ${BASE_URL}${CART_PATH}
    Wait Until Keyword Succeeds    20s    500ms    Cart Page Should Be Visible

Cart Page Should Be Visible
    [Documentation]    Presence check for the checkout/cart page.
    # Robust presence check for checkout/cart page
    Wait For Elements State    text=/proceed to checkout/i    visible    timeout=10s