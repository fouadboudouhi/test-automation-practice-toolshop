*** Settings ***
Documentation     Smoke: verify a product details page shows an "Add to cart" control.
...               Opens the first product from the listing and asserts the add-to-cart element is visible.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Product Details Shows Add To Cart
    [Documentation]    Open the first product details page and verify the add-to-cart control is visible.
    [Tags]    smoke

    Go To    ${BASE_URL}
    Wait For At Least One Product Card

    # Strict-mode safe: select the first product card.
    Click    xpath=(//a[contains(@class,"card") and starts-with(@data-test,"product-")])[1]

    # Add-to-cart should be present on details page.
    Wait For Elements State    css=[data-test="add-to-cart"]    visible    timeout=30s