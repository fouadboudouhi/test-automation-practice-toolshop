*** Settings ***
Documentation     Smoke: verify product thumbnails are visible on the product listing.
...               Waits for the first product image to become visible and asserts its src attribute is non-empty.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Product Thumbnails Are Visible
    [Documentation]    Assert the first product thumbnail image is visible and has a non-empty src.
    [Tags]    smoke

    # NOTE: Product list is on the home page.
    Go To    ${BASE_URL}
    Wait For Elements State    xpath=(//a[contains(@class,"card") and starts-with(@data-test,"product-")]//img)[1]    visible    timeout=60s

    ${src}=    Get Attribute    xpath=(//a[contains(@class,"card") and starts-with(@data-test,"product-")]//img)[1]    src
    Should Not Be Empty    ${src}