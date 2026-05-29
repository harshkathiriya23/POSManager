from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "personID",
            "username",
            "name",
            "email",
            "role",
            "role_display",
            "mobile_number",
            "alternative_contact_number",
            "address",
            "profile_picture",
            "is_profile_completed",
            "is_active",
            "date_joined",
            "last_login",
        )
        read_only_fields = (
            "id",
            "username",
            "date_joined",
            "last_login",
            "is_profile_completed",
            "is_active",
        )


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("personID", "role", "name", "password")

    def validate_personID(self, value):
        person_id = value.strip()
        if not person_id:
            raise serializers.ValidationError("Person ID is required.")
        if User.objects.filter(personID__iexact=person_id).exists():
            raise serializers.ValidationError(
                "This Person ID is already in use. Each Person ID must be unique."
            )
        return person_id

    def create(self, validated_data):
        person_id = validated_data["personID"]
        user = User(
            personID=person_id,
            username=person_id,
            name=validated_data.get("name", ""),
            role=validated_data["role"],
            is_active=True,
            is_profile_completed=False,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """SuperAdmin: update user details and activate/deactivate accounts."""

    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = User
        fields = (
            "personID",
            "name",
            "email",
            "role",
            "mobile_number",
            "alternative_contact_number",
            "address",
            "is_active",
            "password",
        )

    def validate_password(self, value):
        if value:
            validate_password(value)
        return value or None

    def validate_personID(self, value):
        person_id = value.strip()
        if not person_id:
            raise serializers.ValidationError("Person ID is required.")
        qs = User.objects.filter(personID__iexact=person_id)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "This Person ID is already in use. Each Person ID must be unique."
            )
        return person_id

    def validate(self, attrs):
        request = self.context.get("request")
        if (
            self.instance
            and request
            and request.user.is_authenticated
            and self.instance.pk == request.user.pk
            and attrs.get("is_active") is False
        ):
            raise serializers.ValidationError(
                {"is_active": "You cannot deactivate your own account."}
            )
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        person_id = validated_data.get("personID")
        if person_id and person_id != instance.personID:
            instance.username = person_id
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


def _sync_name_to_user_fields(instance):
    if instance.name:
        parts = instance.name.split(" ", 1)
        instance.first_name = parts[0]
        instance.last_name = parts[1] if len(parts) > 1 else ""


class SelfProfileUpdateSerializer(serializers.ModelSerializer):
    """User updates own profile — password and unique/system fields are not included."""

    class Meta:
        model = User
        fields = (
            "name",
            "email",
            "mobile_number",
            "alternative_contact_number",
            "address",
            "profile_picture",
        )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        _sync_name_to_user_fields(instance)
        instance.save()
        return instance


class ProfileCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "name",
            "email",
            "mobile_number",
            "alternative_contact_number",
            "address",
            "profile_picture",
        )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.is_profile_completed = True
        _sync_name_to_user_fields(instance)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    personID = serializers.CharField()
    password = serializers.CharField(write_only=True)
