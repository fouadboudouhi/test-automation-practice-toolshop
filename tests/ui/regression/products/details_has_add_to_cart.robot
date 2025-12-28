*** Settings ***
Documentation     Regression: product details shows Add to cart.
...               Opens the first product details page and verifies the "Add to cart" button is visible.
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop


*** Test Cases ***
Product Details Has Add To Cart Button
    [Documentation]    Open a product details page and assert the "Add to cart" action is visible.
    [Tags]    regression

    Wait For At Least One Product Card
    Click    css=a.card[data-test^="product-"] >> nth=0
    Wait For Elements State    text=Add to cart    visible    timeout=15s