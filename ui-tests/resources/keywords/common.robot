*** Settings ***
Library    Browser

*** Variables ***
${BASE_URL}    %{BASE_URL=https://practicesoftwaretesting.com}
${EMAIL}       %{DEMO_EMAIL=customer@practicesoftwaretesting.com}
${PASSWORD}    %{DEMO_PASSWORD=welcome01}

*** Keywords ***
Open Toolshop
    New Browser    chromium    headless=true
    New Context
    ...    viewport={'width': 1920, 'height': 1080}
    ...    userAgent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)
    New Page       ${BASE_URL}

    Wait For Elements State    css=body    visible    timeout=30s
    Ensure Navigation Is Expanded


Ensure Navigation Is Expanded
    [Documentation]    Expands hamburger menu in CI/mobile mode if present.
    ${toggle}=    Get Element Count    css=button.navbar-toggler
    IF    ${toggle} > 0
        Click    css=button.navbar-toggler
        Wait For Elements State    css=[data-test="nav-sign-in"]    visible    timeout=20s
    END


Close Toolshop
    Close Browser