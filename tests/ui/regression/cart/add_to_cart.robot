*** Settings ***
Documentation     Regression test for add-to-cart functionality.
...               Expected to expose known demo application issues.
Resource          ../../resources/keywords/common.robot
Test Setup        Open Toolshop
Test Teardown     Close Toolshop


*** Test Cases ***
Add Product To Cart
    [Documentation]    Add the first visible product to the cart and verify the cart entry point appears.
    [Tags]    regression

    Wait Until Keyword Succeeds    15s    500ms    Product Cards Should Exist
    Click    css=a.card[data-test^="product-"] >> nth=0
    Click    text=Add to cart
    Wait For Elements State    text=Shopping cart    visible    timeout=10s


*** Keywords ***
Product Cards Should Exist
    [Documentation]    Assert that at least one product card is rendered on the page.
    ${count}=    Get Element Count    css=a.card[data-test^="product-"]
    Should Be True    ${count} > 0