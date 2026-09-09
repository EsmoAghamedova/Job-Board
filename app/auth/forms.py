from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


def password_strength(password):
    """Return a six-step score for a password or passphrase."""
    if len(password) < 8:
        return 0

    words = password.split()
    is_passphrase = (
        len(password) >= 15
        and 5 <= len(words) <= 7
        and all(word.isalpha() for word in words)
    )
    if is_passphrase:
        return 5

    character_types = sum([
        any(character.islower() for character in password),
        any(character.isupper() for character in password),
        any(character.isdigit() for character in password),
        any(not character.isalnum() for character in password),
    ])

    if len(password) < 10:
        return 1
    if character_types >= 4:
        return 6 if len(password) >= 15 else 5
    if character_types >= 3:
        return 5
    if character_types >= 2:
        return 4
    return 2


def validate_password_strength(form, field):
    password = field.data or ""
    if password_strength(password) < 4:
        raise ValidationError(
            "Use at least 8 characters and a mix of letters, numbers, or symbols."
        )


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[
                       DataRequired(), Length(min=2, max=120)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[
                             DataRequired(), Length(min=8), validate_password_strength])
    confirm_password = PasswordField("Confirm Password", validators=[
                                     DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ProfileForm(FlaskForm):
    name = StringField("Name", validators=[
                       DataRequired(), Length(min=2, max=120)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    picture = FileField("Profile picture", validators=[
                        FileAllowed(["jpg", "jpeg", "png", "gif"])])
    submit = SubmitField("Save profile")


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField(
        "Current password", validators=[DataRequired()])
    new_password = PasswordField("New password", validators=[
        DataRequired(), Length(min=8), validate_password_strength])
    confirm_password = PasswordField("Confirm new password", validators=[
        DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Change password")


class DeleteAccountForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Delete account")
