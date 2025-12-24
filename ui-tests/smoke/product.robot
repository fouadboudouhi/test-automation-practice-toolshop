*** Settings ***
Documentation     Smoke test verifying that at least one product card is visible.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Product Page Is Reachable
    [Documentation]
    ...    Pass criteria:
    ...    - At least one product card is visible
    ...    Notes:
    ...    - Selector matches multiple cards -> strict-mode risk if used in wait directly
    ...    - We wait for the first match via XPath, then count via CSS
    Wait For Elements State    xpath=(//a[contains(@class,"card") and starts-with(@data-test,"product-")])[1]    visible    timeout=20s
    ${count}=    Get Element Count    css=a.card[data-test^="product-"]
    Should Be True    ${count} > 0