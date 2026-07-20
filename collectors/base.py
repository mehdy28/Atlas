
class BaseCollector:
    """
    Every collector (Internet Archive, NASA, Pexels, etc.)
    must implement this interface. The rest of Atlas never
    needs to know which source a clip came from.
    """

    def search(self, query, rows=20):
        raise NotImplementedError

    def resolve_download(self, item):
        """
        Given a search result item, return (url, filename, filesize_mb).
        """
        raise NotImplementedError
