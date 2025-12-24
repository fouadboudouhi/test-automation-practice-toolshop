*** Settings ***
Library    Browser    auto_closing_level=SUITE

*** Variables ***
# Default for Docker stack. Override via env in CI/local.
${BASE_URL}    %{BASE_URL=http://localhost:4200}

# Headless default true (CI). For local debugging: export HEADLESS=false
${HEADLESS}    %{HEADLESS=true}

# Demo credentials (override in CI secrets/env if needed)
${EMAIL}       %{DEMO_EMAIL=customer@practicesoftwaretesting.com}
${PASSWORD}    %{DEMO_PASSWORD=welcome01}

*** Keywords ***
Open Toolshop
    [Documentation]    Start a fresh browser, open Toolshop and wait until basic UI is ready.
    New Browser    chromium    headless=${HEADLESS}    chromiumSandbox=false
    New Context    viewport={'width': 1280, 'height': 800}
    New Page       ${BASE_URL}
    Register Keyword To Run On Failure    Capture Screenshot
    Wait Until Toolshop Ready

Wait Until Toolshop Ready
    [Documentation]    Minimal readiness gate: navbar + search are visible.
    Wait For Elements State    css=nav.navbar               visible    timeout=60s
    Wait For Elements State    css=[data-test="search-query"]    visible    timeout=60s

Capture Screenshot
    [Documentation]    Store screenshot inside current Robot output dir (CI artifact friendly).
    Take Screenshot    ${OUTPUT DIR}/screenshots

Wait For Login To Complete
    [Documentation]    After submitting login form, wait until we are no longer on /login.
    Wait Until Keyword Succeeds    30s    1s    Login Should Be Completed

Login Should Be Completed
    ${url}=    Get Url
    Should Not Contain    ${url}    /login
    Wait For Elements State    css=nav.navbar    visible    timeout=10s

Wait For At Least One Product Card
    [Documentation]    Handles slow backend: wait until first product card is visible.
    Wait Until Keyword Succeeds    60s    2s    First Product Card Should Be Visible

First Product Card Should Be Visible
    Wait For Elements State
    ...    xpath=(//a[contains(@class,"card") and starts-with(@data-test,"product-")])[1]
    ...    visible
    ...    timeout=2s

Close Toolshop
    [Documentation]    Close browser.
    Close Browser