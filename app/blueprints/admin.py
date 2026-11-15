import os
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user
from werkzeug.utils import secure_filename
from app.models import db, login_manager, Libro
from app.forms import LibroForm

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
@admin_bp.before_request
def solo_gestores():
    if not current_user.is_authenticated:
        return login_manager.unauthorized()  
    if not current_user.es_gestor:
        abort(403) 

@admin_bp.route("/libro/nuevo", methods=["GET", "POST"])
def crear_libro():
    form = LibroForm()
    if form.validate_on_submit():
        libro=Libro(
            titulo=form.titulo.data,
            autor=form.autor.data,
            genero=form.genero.data,
            precio=form.precio.data,
            stock=form.stock.data 
        )
        archivo = form.archivo_portada.data
        if archivo and archivo.filename:
            nombre_seguro = secure_filename(archivo.filename)
            nombre_final = f"{libro.genero.lower()}_{nombre_seguro}"
            libro.portada = nombre_final
            ruta = os.path.join(current_app.config["UPLOAD_FOLDER"], nombre_final)
            archivo.save(ruta)
        db.session.add(libro)
        db.session.commit()
        flash(f"Libro «{libro.titulo}» creado correctamente.", "exito")
        return redirect(url_for("public.mostrar_libros"))
       
                    
    return render_template("libro_form.html", form=form, titulo="Nuevo Libro")


@admin_bp.route("/libro/<int:libro_id>/editar", methods=["GET", "POST"])
def editar_libro(libro_id):
    libro = db.get_or_404(Libro, libro_id)
    form = LibroForm(obj=libro, id_actual=libro.id)

    if form.validate_on_submit():
        libro.titulo = form.titulo.data
        libro.autor = form.autor.data
        libro.genero = form.genero.data
        libro.precio = form.precio.data
        libro.stock = form.stock.data

        archivo = form.archivo_portada.data
        if archivo and archivo.filename:
            nombre_seguro = secure_filename(archivo.filename)
            nombre_final = f"{libro.genero.lower()}_{nombre_seguro}"

            if libro.portada and libro.portada != nombre_final:
                ruta_antigua = os.path.join(current_app.config["UPLOAD_FOLDER"], libro.portada)
                if os.path.exists(ruta_antigua):
                    os.remove(ruta_antigua)

            ruta = os.path.join(current_app.config["UPLOAD_FOLDER"], nombre_final)
            archivo.save(ruta)
            libro.portada = nombre_final

        db.session.commit()
        flash(f"Libro «{libro.titulo}» actualizado correctamente.", "exito")
        return redirect(url_for("public.mostrar_libros"))

    return render_template(
        "libro_form.html",
        form=form,
        titulo="Editar Libro",
        libro=libro,
    )

@admin_bp.route("/libro/<int:libro_id>/eliminar", methods=["POST"])
def eliminar_libro(libro_id):
    libro = db.get_or_404(Libro, libro_id)
    if libro.stock==0:
        if libro.portada:
            ruta =os.path.join(current_app.config["UPLOAD_FOLDER"], libro.portada)
            if os.path.exists(ruta):
                os.remove(ruta)
        titulo=libro.titulo
        db.session.delete(libro)
        db.session.commit()   
        flash(f"Se ha eliminado el libro con el título  «{titulo}»", "exito")
        return redirect(url_for("public.mostrar_libros"))
                  
    else:
        flash(f"No se puede eliminar «{libro.titulo}»: aún tiene {libro.stock} unidades en stock.", "error")
        return redirect(url_for("public.mostrar_libros"))
    
