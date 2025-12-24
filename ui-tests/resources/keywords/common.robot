*** Settings ***
Documentation     Common keywords for browser lifecycle management.
...               These keywords are intentionally minimal and deterministic.
Library           Browser

*** Keywords ***
Open Toolshop
    [Documentation]    Opens the application under test in a clean browser context.
    New Browser    chromium    headless=true
    New Context    viewport={'width': 1280, 'height': 800}
    New Page       %{BASE_URL}
    Wait For Load State    networkidle

Close Toolshop
    [Documentation]    Closes the browser and frees all resources.
    Close Browser