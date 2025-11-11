from maleo.schemas.resource import Resource, ResourceIdentifier


USER_PROFILE_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="user_profile", name="User Profile", slug="user-profiles"
        )
    ],
    details=None,
)
