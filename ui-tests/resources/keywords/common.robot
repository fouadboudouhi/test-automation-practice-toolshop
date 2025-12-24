*** Settings ***
Library    Browser

*** Keywords ***
Open Toolshop
    New Browser    chromium    headless=true
    New Context    viewport={'width': 1920, 'height': 1080}
    New Page       %{BASE_URL}

    # CI-stable page readiness
    Wait For Load State    domcontentloaded    timeout=30s
    Wait For Application Ready


Wait For Application Ready
    [Documentation]    Waits until the SPA navigation is rendered.
    Wait Until Keyword Succeeds    30s    1s    Navigation Should Be Present


Navigation Should Be Present
    ${count}=    Get Element Count    css=nav
    Should Be True    ${count} > 0


Close Toolshop
    Close Browser