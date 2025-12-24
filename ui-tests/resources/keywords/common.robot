*** Settings ***
Documentation     Shared keywords + shared configuration for UI tests (Robot Framework Browser / Playwright).
Library           Browser    auto_closing_level=SUITE

*** Variables ***
${BASE_URL}    %{BASE_URL=https://practicesoftwaretesting.com}
${EMAIL}       %{DEMO_EMAIL=customer@practicesoftwaretesting.com}
${PASSWORD}    %{DEMO_PASSWORD=welcome01}

*** Keywords ***
Open Toolshop
    [Documentation]    Starts a fresh browser and opens the Toolshop homepage. Waits for navbar to be visible.
    New Browser    chromium    headless=true
    New Context    viewport={'width': 1280, 'height': 800}
    New Page       ${BASE_URL}
    Wait For Elements State    css=nav.navbar    visible    timeout=30s
    Register Keyword To Run On Failure    Capture Screenshot

Capture Screenshot
    [Documentation]    Writes screenshots under the current Robot output directory.
    Take Screenshot    ${OUTPUT DIR}/screenshots

Close Toolshop
    [Documentation]    Closes the browser.
    Close Browser