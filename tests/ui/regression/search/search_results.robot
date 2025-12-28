*** Settings ***
Documentation     Regression test for search functionality.
...               Searches for a known term and verifies that at least one product card is shown.
Resource          ../../resources/keywords/common.robot


*** Test Cases ***
Search Returns Matching Products
    [Documentation]    Search for "hammer" and assert that the results list is non-empty.
    [Tags]    regression

    Open Toolshop
    Fill Text    css=[data-test="search-query"]    hammer
    Click    css=[data-test="search-submit"]
    Wait Until Keyword Succeeds    10s    500ms    Search Results Should Exist
    Close Toolshop


*** Keywords ***
Search Results Should Exist
    [Documentation]    Assert that at least one product card exists after executing the search.
    ${count}=    Get Element Count    css=a.card[data-test^="product-"]
    Should Be True    ${count} > 0