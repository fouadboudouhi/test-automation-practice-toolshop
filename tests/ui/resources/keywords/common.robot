*** Settings ***
Library    Browser    auto_closing_level=SUITE

*** Variables ***
${BASE_URL}    %{BASE_URL=http://localhost:4200}
${HEADLESS}    %{HEADLESS=true}
${EMAIL}       %{DEMO_EMAIL=customer@practicesoftwaretesting.com}
${PASSWORD}    %{DEMO_PASSWORD=welcome01}

*** Keywords ***
Open Toolshop
    New Browser    chromium    headless=${HEADLESS}    chromiumSandbox=false
    New Context    viewport={'width': 1280, 'height': 800}
    New Page       ${BASE_URL}
    Register Keyword To Run On Failure    Capture Screenshot
    Wait Until Toolshop Ready

Wait Until Toolshop Ready
    Wait For Elements State    css=nav.navbar                    visible    timeout=60s
    Wait For Elements State    css=[data-test="search-query"]     visible    timeout=60s

Capture Screenshot
    Take Screenshot    ${OUTPUT DIR}/screenshots

Wait For Login To Complete
    Wait Until Keyword Succeeds    30s    1s    Login Should Be Completed

Login Should Be Completed
    ${url}=    Get Url
    Should Not Contain    ${url}    /login
    Wait For Elements State    css=nav.navbar    visible    timeout=10s

Wait For At Least One Product Card
    Wait Until Keyword Succeeds    60s    2s    First Product Card Should Be Visible

First Product Card Should Be Visible
    Wait For Elements State
    ...    xpath=(//a[contains(@class,"card") and starts-with(@data-test,"product-")])[1]
    ...    visible
    ...    timeout=2s

Close Toolshop
    Close Browser
