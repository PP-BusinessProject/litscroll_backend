from typing import Tuple

from ._mixins import FallbackNamed, Identified, Named, Timestamped, Toggleable
from .auth.user import User
from .base import Base, Permissions
from .public.book import Book
from .public.book_genre import BookGenre
from .public.book_quote import BookQuote
from .public.book_quote_engagement_prediction import (
    BookQuoteEngagementPrediction,
)
from .public.book_quote_narrative import BookQuoteNarrative
from .public.book_quote_ranking import BookQuoteRanking
from .public.book_quote_style_analysis import BookQuoteStyleAnalysis
from .public.book_quote_user import BookQuoteUser
from .public.genre import Genre
from .public.view_user_suggested_quotes import ViewUserSuggestedQuotes


__all__: Tuple[str, ...] = (
    'FallbackNamed',
    'Identified',
    'Named',
    'Timestamped',
    'Toggleable',
    'User',
    'Base',
    'Permissions',
    'Book',
    'BookGenre',
    'BookQuote',
    'BookQuoteUser',
    'Genre',
    'ViewUserSuggestedQuotes',
    'BookQuoteEngagementPrediction',
    'BookQuoteNarrative',
    'BookQuoteRanking',
    'BookQuoteStyleAnalysis',
)
