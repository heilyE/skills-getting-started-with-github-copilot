from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


class TestRootRedirect:
    """Tests for root path redirection."""
    
    def test_root_redirect(self, reset_activities):
        """Test that GET / redirects to /static/index.html"""
        # Arrange: nothing to arrange, just preparing the request
        
        # Act: make the request without following redirects
        response = client.get("/", follow_redirects=False)
        
        # Assert: verify the redirect status and location
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for retrieving activities list."""
    
    def test_get_activities(self, reset_activities):
        """Test that GET /activities returns the activities list"""
        # Arrange: prepare for the request
        expected_activities = ["Chess Club", "Programming Class"]
        
        # Act: fetch the activities
        response = client.get("/activities")
        
        # Assert: verify response and content
        assert response.status_code == 200
        data = response.json()
        for activity in expected_activities:
            assert activity in data


class TestSignup:
    """Tests for participant signup."""
    
    def test_signup_success(self, reset_activities):
        """Test successful signup for an activity"""
        # Arrange: prepare signup data
        activity_name = "Soccer Club"
        email = "test@mergington.edu"
        
        # Act: submit the signup request
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: verify success response
        assert response.status_code == 200
        assert email in response.json()["message"]
        
        # Assert: verify participant was added via GET
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]

    def test_signup_duplicate(self, reset_activities):
        """Test signup fails for duplicate participant"""
        # Arrange: prepare data for a duplicate signup attempt
        activity_name = "Chess Club"
        email = "duplicate@mergington.edu"
        
        # Act: first signup (should succeed)
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Act: attempt duplicate signup (should fail)
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: verify the duplicate signup is rejected
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]


class TestUnregister:
    """Tests for participant unregistration."""
    
    def test_unregister_success(self, reset_activities):
        """Test successful unregister from an activity"""
        # Arrange: sign up a participant first
        activity_name = "Basketball Club"
        email = "remove@mergington.edu"
        
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act: unregister the participant
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: verify unregister success
        assert response.status_code == 200
        assert email in response.json()["message"]
        
        # Assert: verify participant was removed via GET
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]

    def test_unregister_missing(self, reset_activities):
        """Test unregister fails for non-participant"""
        # Arrange: prepare data for unregistering a non-participant
        activity_name = "Drama Club"
        email = "notmember@mergington.edu"
        
        # Act: attempt to unregister a non-participant
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: verify the unregister fails with 404
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"]
