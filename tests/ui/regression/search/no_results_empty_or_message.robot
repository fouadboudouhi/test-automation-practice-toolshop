*** Settings ***
Documentation     Regression: searching with a query that yields no results should show a "no products" state.
...               Uses a unique query to avoid matching existing products and asserts that:
...               (1) a "no products found" message appears and (2) no product cards are shown.
Resource          ../../resources/common.robot
Test Setup        Open Toolshop
Test Teardown     Close Browser


*** Test Cases ***
Search With No Results Shows No Products Message
    [Documentation]    Search with a non-existing term and verify the "no results" UI state is displayed.
    ${query}=    Set Variable    __no_such_product__987654321__

    Go To    ${BASE_URL}/
    Wait For Elements State    css=[data-test="search-query"]    visible    timeout=20s

    Fill Text    css=[data-test="search-query"]    ${query}
    # Submit search (button click is more reliable than ENTER across browsers).
    Click    css=button:has-text("Search")

    Wait Until Keyword Succeeds    30x    1s    No Results State Should Be Visible


*** Keywords ***
No Results State Should Be Visible
    [Documentation]    Assert that the "no products found" message is visible and product cards count is zero.

    # 1) Message must appear (regex -> tolerant).
    Wait For Elements State    text=/There are no products found\\.?/i    visible    timeout=2s

    # 2) And there must be no product cards anymore.
    ${count}=    Get Element Count    css=a.card[data-test^="product-"]
    Should Be Equal As Integers    ${count}    0