*** Settings ***
Documentation     Regression test for category filtering.
...               Applies the first available category filter and verifies that product cards are shown.
Resource          ../../resources/keywords/common.robot


*** Test Cases ***
Filter Products By Category
    [Documentation]    Apply the first category filter and assert the result list is non-empty.
    [Tags]    regression

    Open Toolshop
    Click    css=[data-test^="category-"] >> nth=0
    Wait Until Keyword Succeeds    10s    500ms    Filtered Results Should Exist
    Close Toolshop


*** Keywords ***
Filtered Results Should Exist
    [Documentation]    Assert that at least one product card exists after applying the filter.
    ${count}=    Get Element Count    css=a.card[data-test^="product-"]
    Should Be True    ${count} > 0