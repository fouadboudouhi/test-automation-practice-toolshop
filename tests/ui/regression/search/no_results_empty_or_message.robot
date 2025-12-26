*** Settings ***
Resource        ../../resources/common.robot
Test Setup      Open Toolshop
Test Teardown   Close Browser

*** Test Cases ***
Search With No Results Shows No Products Message
    ${query}=    Set Variable    __no_such_product__987654321__
    Go To    ${BASE_URL}/
    Wait For Elements State    css=[data-test="search-query"]    visible    timeout=20s

    Fill Text    css=[data-test="search-query"]    ${query}
    # submit search (button click is more reliable than ENTER across browsers)
    Click    css=button:has-text("Search")

    Wait Until Keyword Succeeds    30x    1s    No Results State Should Be Visible


*** Keywords ***
No Results State Should Be Visible
    # 1) Message must appear (regex -> tolerant)
    Wait For Elements State    text=/There are no products found\\.?/i    visible    timeout=2s

    # 2) And there must be no product cards anymore
    ${count}=    Get Element Count    css=a.card[data-test^="product-"]
    Should Be Equal As Integers    ${count}    0
