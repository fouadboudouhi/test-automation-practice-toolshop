*** Settings ***
Documentation     Regression test for sorting products by price.
...               Triggers the first sort control and verifies that product cards are still displayed.
Resource          ../../resources/keywords/common.robot


*** Test Cases ***
Sort Products By Price
    [Documentation]    Apply the first price sort option and assert the product list remains non-empty.
    [Tags]    regression

    Open Toolshop
    Click    css=[data-test="sort"] >> nth=0
    Wait Until Keyword Succeeds    10s    500ms    Sorted Results Should Exist
    Close Toolshop


*** Keywords ***
Sorted Results Should Exist
    [Documentation]    Assert that at least one product card exists after applying sorting.
    ${count}=    Get Element Count    css=a.card[data-test^="product-"]
    Should Be True    ${count} > 0