# src/schemas/__init__.py

# Імпортуємо схеми користувача та груп
# from .user.user_group import UserGroupBase, UserGroupResponse, UserGroupUpdate, UserGroupEnumSchema
# from .user.user import UserRegister, UserLogin, UserResponse, UserUpdate, UserActivation, UserUpdateGroup
# from .user.token import Token, ActivationTokenResponse, RefreshTokenResponse

# Імпортуємо схеми фільмів
from .movies.genre import GenreBase, GenreResponse # <-- ВЖЕ МАЄ БУТИ
from .movies.movies import MovieBase, MovieCreate, MovieUpdate, MovieResponse
from .movies.favorite_movie import FavoriteMovieBase, FavoriteMovieCreate, FavoriteMovieResponse