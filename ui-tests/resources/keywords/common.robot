*** Settings ***
Library    Browser

*** Keywords ***
Open Toolshop
    New Browser    chromium    headless=true
    New Page       %{BASE_URL}

Close Toolshop
    Close Browser
