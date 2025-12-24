*** Settings ***
Documentation     Smoke test verifying that product navigation is possible.
...               This test intentionally validates URL navigation instead of
...               product detail rendering due to known demo application bugs.
Resource          ../resources/keywords/common.robot

*** Test Cases ***
Product Page Is Reachable
    [Documentation]    Ensures that clicking a product leads to a product route.
    Open Toolshop

    # Wait until at least one product card exists (strict-mode safe)
    Wait Until Keyword Succeeds    15s    500ms    Product Cards Should Exist

    # Navigate to first available product
    Click    css=a.card[data-test^="product-"] >> nth=0

    # Smoke-level assertion: URL changes to product route
    Wait Until Keyword Succeeds    10s    500ms    Product URL Should Be Active

    Close Toolshop


*** Keywords ***
Product Cards Should Exist
    [Documentation]    Checks that at least one product card is present.
    ${count}=    Get Element Count    css=a.card[data-test^="product-"]
    Should Be True    ${count} > 0

Product URL Should Be Active
    [Documentation]    Validates that the browser navigated to a product URL.
    ${url}=    Get Url
    Should Contain    ${url}    /product/