from unittest.mock import MagicMock, patch
from splent_io.splent_feature_auth.services import AuthenticationService

@patch("splent_feature_auth.services.login_user")
def test_authenticate_valid_user(mock_login_user):
    mock_user = MagicMock()
    mock_user.check_password.return_value = True

    repo = MagicMock()
    repo.get_by_email.return_value = mock_user

    service = AuthenticationService(user_repository=repo)
    result = service.login("user@example.com", "1234")

    assert result is True
    mock_login_user.assert_called_once_with(mock_user, remember=True)
