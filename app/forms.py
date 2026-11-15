from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    BooleanField,
    FloatField,
    IntegerField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    ValidationError,
    InputRequired
)
from app.models import Libro, Usuario


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión (Ya implementado)."""

    email = StringField(
        "Correo Electrónico",
        validators=[
            DataRequired(message="Introduce tu correo electrónico."),
            Email(message="Formato de correo no válido."),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="Introduce tu contraseña.")],
    )
    remember = BooleanField("Mantener sesión iniciada")
    submit = SubmitField("Entrar a la Librería")


class LibroForm(FlaskForm):
    """Formulario para crear y editar libros."""
    
    titulo = StringField(
        "Título",
        validators=[
            DataRequired(message="El título es obligatorio."),
            Length(min=2, max=150, message="Entre 2 y 150 caracteres."),
        ],
    )
    autor = StringField(
        "Autor",
        validators=[
            DataRequired(message="El autor es obligatorio."),
            Length(min=3, max=100, message="Entre 3 y 100 caracteres."),
        ],
    )
    genero = StringField(
        "Género (ej. Novela, Ciencia ficción, Informática)",
        validators=[
            DataRequired(message="El género es obligatorio."),
            Length(min=3, max=50, message="Entre 3 y 50 caracteres."),
        ],
    )

    precio = FloatField("Precio (€)", validators=[DataRequired(),NumberRange(min=3,max=200,message="El precio debe de ser más de 3€ y menos de 200€")])
    stock = IntegerField("Unidades en stock", default=10,validators=[InputRequired(),NumberRange(min=0,message="El valor no puede ser negativo")])
    archivo_portada = FileField(
        "Portada (JPG, PNG)",
        validators=[FileAllowed(["jpg", "jpeg", "png"], "Solo se admiten imágenes JPG, JPEG o PNG.")],
    )
    submit = SubmitField("Guardar Libro")
    def __init__(self, *args, id_actual=None, **kwargs):
            super().__init__(*args, **kwargs)
            self.id_actual = id_actual
    def validate_titulo(self, field):
        existente = Libro.query.filter_by(titulo=field.data).first()
        if existente and existente.id != self.id_actual:
            raise ValidationError("Ese libro ya está registrado.")


class RegistroForm(FlaskForm):
    """Formulario de alta para nuevos clientes."""

    username = StringField(
        "Nombre de Usuario",
        validators=[
            DataRequired(message="El nombre de usuario es obligatorio."),
            Length(min=3, max=50, message="Debe tener entre 3 y 50 caracteres."),
        ],
    )
    email = StringField(
        "Correo Electrónico",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Introduce un correo válido."),
        ],
    )

    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(min=6, message="Mínimo 6 caracteres."),
        ],
    )
    confirm_password = PasswordField(
        "Confirmar Contraseña",
        validators=[
            DataRequired(message="Confirma tu contraseña."),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ],
    )
    submit = SubmitField("Crear mi cuenta")

    def validate_username(self, field):
        if Usuario.query.filter_by(username=field.data).first():
            raise ValidationError("Ese nombre de usuario ya está registrado.")

    def validate_email(self, field):
        if Usuario.query.filter_by(email=field.data).first():
            raise ValidationError("Ese correo electrónico ya está en uso.")


class CambiarPasswordForm(FlaskForm):
    """Formulario para cambiar la contraseña desde el perfil."""

    submit = SubmitField("Actualizar Contraseña")
