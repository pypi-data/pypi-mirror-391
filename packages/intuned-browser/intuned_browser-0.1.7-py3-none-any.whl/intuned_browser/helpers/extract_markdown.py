from typing import Union

import mdformat
from playwright.async_api import Locator
from playwright.async_api import Page

from intuned_browser.common.evaluate_with_intuned import evaluate_with_intuned


async def extract_markdown(source: Union[Page, Locator]) -> str:
    is_page = isinstance(source, Page)
    if is_page:
        handle = await source.locator("body").element_handle()
    else:
        handle = await source.element_handle()

    md = await evaluate_with_intuned(
        source,
        "(element) => window.__INTUNED__.convertElementToMarkdown(element)",
        handle.as_element(),
    )

    return mdformat.text(md)
