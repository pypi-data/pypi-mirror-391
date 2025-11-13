Pagination
==========

Fitrequest provides an easy way to handle paginated responses using the ``@paginated`` decorator. This decorator accepts an optional argument ``page_cls``, which specifies how pages should be processed.

The default page handler is ``PageDict``, which expects API responses in this format:

.. code-block:: json

    {
        "results": ["a", "b", "c"],
        "next": "https://my.next.page.url"
    }

Basic Usage
-----------

Here's a simple example of how to use pagination with Fitrequest:

.. code-block:: python

    from fitrequest.decorators import fit, paginated
    from fitrequest.client import FitRequest

    class TestClient(FitRequest):
        client_name = 'test_client'
        base_url = 'https://test.skillcorner.fr'

        @paginated
        @fit(endpoint='/items/')
        def get_items(self, **kwargs) -> list[dict]: ...

        @paginated
        @fit(endpoint='/items/')
        async def async_get_items(self, **kwargs) -> list[dict]: ...

Customizing Field Names
-----------------------

If your API uses different field names for results and next page URLs, you can create a custom page handler:

.. code-block:: python

    from fitrequest.decorators import fit, paginated, PageDict
    from fitrequest.client import FitRequest

    @dataclass
    class CustomPageDict(PageDict):
        results_kw: str = 'data'  # Field name for results
        next_kw: str = 'next_page'  # Field name for next page URL

    class TestClient(FitRequest):
        client_name = 'test_client'
        base_url = 'https://test.skillcorner.fr'

        @paginated(page_cls=CustomPageDict)
        @fit(endpoint='/items/')
        def get_items(self, **kwargs) -> list[dict]: ...

        @paginated(page_cls=CustomPageDict)
        @fit(endpoint='/items/')
        async def async_get_items(self, **kwargs) -> list[dict]: ...

Advanced Customization
----------------------

For more complex cases, you can create a custom page handler by inheriting from ``AbstractPage``. Your class must implement:

1. How to extract results and next page URL
2. How to save results (for Fitrequest's ``save_*`` methods)

Example: Handling a non-standard response format

.. code-block:: python

    from fitrequest.decorators import fit, paginated, AbstractPage
    from fitrequest.client import FitRequest

    class CustomPageString(AbstractPage):
        def __init__(self, data: str) -> None:
            self._results, self._next_url = data.split(sep='|', maxsplit=1)

        @property
        def results(self) -> Iterable:
            return map(int, self._results.split(sep=','))

        @property
        def next_url(self) -> str | None:
            return self._next_url if self._next_url != '' else None

        @staticmethod
        def save_results(filepath: Path, results: list) -> None:
            filepath.write_text('\n'.join(str(num) for num in results))

        @staticmethod
        async def async_save_results(filepath: Path, results: list) -> None:
            async with aiofiles.open(filepath, mode='x') as data_file:
                await data_file.write('\n'.join(str(num) for num in results))

    class TestClient(FitRequest):
        client_name = 'test_client'
        base_url = 'https://test.skillcorner.fr'

        @paginated(page_cls=CustomPageString)
        @fit(endpoint='/items/')
        def get_items(self, **kwargs) -> list[int]: ...

        @paginated(page_cls=CustomPageString)
        @fit(endpoint='/items/')
        async def async_get_items(self, **kwargs) -> list[int]: ...

Flexibility
-----------

As shown in these examples, Fitrequest's pagination system is highly flexible. You can easily create custom page handlers to work with any API response format.
