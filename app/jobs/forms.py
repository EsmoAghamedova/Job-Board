from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class JobForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=160)])
    short_description = StringField("Short description", validators=[
                                    DataRequired(), Length(max=300)])
    full_description = TextAreaField(
        "Full description", validators=[DataRequired()])
    company = StringField("Company", validators=[
                          DataRequired(), Length(max=160)])
    salary = StringField("Salary", validators=[DataRequired(), Length(max=80)])
    location = StringField("Location", validators=[
                           DataRequired(), Length(max=120)])
    category = SelectField("Category", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save job")


class ApplicationForm(FlaskForm):
    name = StringField("Full name", validators=[
                       DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[
                        DataRequired(), Email(), Length(max=120)])
    phone = StringField("Phone", validators=[DataRequired(), Length(max=40)])
    cv = FileField("CV / resume", validators=[FileRequired(), FileAllowed(
        ["pdf", "doc", "docx"], "PDF, DOC, or DOCX files only.")])
    cover_letter = TextAreaField("Message to the company", validators=[
                                 DataRequired(), Length(min=20, max=3000)])
    submit = SubmitField("Send application")
