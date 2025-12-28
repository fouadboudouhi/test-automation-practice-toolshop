*** Settings ***
Documentation     Regression: open first product details from product listing (home).
...               Opens the first product card and verifies the details page is shown.
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop


*** Test Cases ***
Open First Product Details
    [Documentation]    Open the first product details page and assert the "Add to cart" button is visible.
    [Tags]    regression

    Wait For At Least One Product Card
    Click    css=a.card[data-test^="product-"] >> nth=0
    Wait For Elements State    text=Add to cart    visible    timeout=15s