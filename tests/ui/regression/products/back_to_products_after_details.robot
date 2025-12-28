*** Settings ***
Documentation     Regression: navigate back after opening product details.
...               Opens the first product details page, navigates back, and verifies the product list is visible again.
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop


*** Test Cases ***
Navigate Back To Products From Details
    [Documentation]    Open a product details page, go back, and assert the products list is visible again.
    [Tags]    regression

    Wait For At Least One Product Card
    Click    css=a.card[data-test^="product-"] >> nth=0
    Wait For Elements State    text=Add to cart    visible    timeout=15s
    Go Back
    Wait For At Least One Product Card