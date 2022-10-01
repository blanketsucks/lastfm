from typing import Dict, Any, Optional

__all__ = 'Wiki',

class Wiki:
    __slots__ = ('published', 'summary', 'content')

    def __init__(self, data: Dict[str, Any]) -> None:
        self.published: Optional[str] = data.get('published')
        self.summary: str = data['summary']
        self.content: str = data['content']

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>'