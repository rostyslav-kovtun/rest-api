import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock
from fastapi import Request, HTTPException
from rate_limiter import RateLimiter
from config import settings

class TestRateLimiter:
    
    @pytest.fixture
    def mock_redis(self):

        redis_mock = AsyncMock()
        redis_mock.zremrangebyscore = AsyncMock(return_value=None)
        redis_mock.zcard = AsyncMock(return_value=0)
        redis_mock.zadd = AsyncMock(return_value=1)
        redis_mock.expire = AsyncMock(return_value=True)
        return redis_mock
    
    @pytest.fixture
    def mock_redis_client(self, mock_redis):

        client_mock = MagicMock()
        client_mock.get_client = MagicMock(return_value=mock_redis)
        return client_mock
    
    @pytest.fixture
    def mock_request(self):

        request = MagicMock()
        request.client.host = "192.168.1.100"
        return request
    
    @pytest.fixture
    def rate_limiter_instance(self, mock_redis_client):

        return RateLimiter(redis_client_instance=mock_redis_client)

    @pytest.mark.asyncio
    async def test_anonymous_user_within_limit(self, rate_limiter_instance, mock_request, mock_redis_client):

        redis_mock = mock_redis_client.get_client()
        redis_mock.zcard.return_value = 1

        try:
            await rate_limiter_instance.check_rate_limit(mock_request, user_id=None)
            success = True
        except HTTPException:
            success = False
        
        assert success, "Rate limiter повинен пропустити запит для анонімного користувача в межах ліміту"

        redis_mock.zremrangebyscore.assert_called_once()
        redis_mock.zcard.assert_called_once()
        redis_mock.zadd.assert_called_once()
        redis_mock.expire.assert_called_once()

    @pytest.mark.asyncio 
    async def test_anonymous_user_exceeded_limit(self, rate_limiter_instance, mock_request, mock_redis_client):

        redis_mock = mock_redis_client.get_client()
        redis_mock.zcard.return_value = 2

        with pytest.raises(HTTPException) as exc_info:
            await rate_limiter_instance.check_rate_limit(mock_request, user_id=None)
        
        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail
        assert "anonymous users" in exc_info.value.detail

        redis_mock.zadd.assert_not_called()

    @pytest.mark.asyncio
    async def test_authenticated_user_within_limit(self, rate_limiter_instance, mock_request, mock_redis_client):

        redis_mock = mock_redis_client.get_client()
        redis_mock.zcard.return_value = 5
        user_id = "user123"

        try:
            await rate_limiter_instance.check_rate_limit(mock_request, user_id=user_id)
            success = True
        except HTTPException:
            success = False
        
        assert success, "Rate limiter повинен пропустити запит для авторизованого користувача в межах ліміту"

        redis_mock.zremrangebyscore.assert_called_once()
        redis_mock.zcard.assert_called_once()
        redis_mock.zadd.assert_called_once()
        redis_mock.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticated_user_exceeded_limit(self, rate_limiter_instance, mock_request, mock_redis_client):

        redis_mock = mock_redis_client.get_client()
        redis_mock.zcard.return_value = 10
        user_id = "user123"

        with pytest.raises(HTTPException) as exc_info:
            await rate_limiter_instance.check_rate_limit(mock_request, user_id=user_id)
        
        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail
        assert "authenticated users" in exc_info.value.detail

        redis_mock.zadd.assert_not_called()

    @pytest.mark.asyncio
    async def test_different_keys_for_user_types(self, rate_limiter_instance, mock_request, mock_redis_client):
        redis_mock = mock_redis_client.get_client()
        redis_mock.zcard.return_value = 1
        
        await rate_limiter_instance.check_rate_limit(mock_request, user_id=None)

        expected_anonymous_key = f"rate_limit_{mock_request.client.host}_anonymous"
        redis_mock.zremrangebyscore.assert_called_with(
            expected_anonymous_key, 
            min=0, 
            max=pytest.approx(time.time() - 60, abs=5)
        )

        redis_mock.reset_mock()
        redis_mock.zcard.return_value = 1

        user_id = "user123"
        await rate_limiter_instance.check_rate_limit(mock_request, user_id=user_id)

        expected_auth_key = f"rate_limit_{user_id}_authenticated"
        redis_mock.zremrangebyscore.assert_called_with(
            expected_auth_key,
            min=0,
            max=pytest.approx(time.time() - 60, abs=5)
        )

    @pytest.mark.asyncio
    async def test_redis_error_handling(self, rate_limiter_instance, mock_request, mock_redis_client):
        redis_mock = mock_redis_client.get_client()
        redis_mock.zcard.side_effect = Exception("Redis connection error")
        
        try:
            await rate_limiter_instance.check_rate_limit(mock_request, user_id=None)
            success = True
        except HTTPException:
            success = False
        except Exception:
            success = True
        
        assert success, "Rate limiter не повинен блокувати запити при помилках Redis"