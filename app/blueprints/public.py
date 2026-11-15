from flask import (
    Blueprint,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_required
from app.models import db, Libro

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    return redirect(url_for("public.mostrar_libros"))


@public_bp.route("/libros")
def mostrar_libros():
    busqueda=request.args.get("busqueda","").strip()
    solo_con_stock=request.args.get("solo_con_stock")
    consulta = Libro.query
    if busqueda:
        consulta=consulta.filter(Libro.titulo.contains(busqueda))
    if solo_con_stock:
        consulta=consulta.filter(Libro.stock>0)

    libros=consulta.all()
    genero_fav = request.cookies.get("genero_fav")
    
    return render_template(
        "catalogo.html",
        lista_libros=libros,
        genero_fav=genero_fav,
        busqueda=busqueda,
        solo_con_stock=solo_con_stock
    )


@public_bp.route("/libro/<int:libro_id>")
def ver_libro(libro_id):
    libro = db.get_or_404(Libro, libro_id)
    
    return render_template("libro_detalle.html", libro=libro)


@public_bp.route("/genero-favorito/<string:genero>")
def guardar_genero(genero):
    respuesta=make_response(redirect(url_for("public.mostrar_libros")))
    respuesta.set_cookie(
        "genero_fav",
        genero,
        max_age=15*24*60*60,
        httponly=True,
        samesite="Lax"
    )
    flash(f"Genero favorito guardado: {genero}!","exito")
    return respuesta

@public_bp.route("/limpiar-genero")
def limpiar_genero():
    respuesta=make_response(redirect(url_for("public.mostrar_libros")))
    respuesta.delete_cookie("genero_fav")
    flash("Preferencia eliminada","info")
    return respuesta


@public_bp.route("/carrito/anadir/<int:libro_id>", methods=["POST"])
@login_required
def anadir_al_carrito(libro_id):
    carrito = session.get("carrito", [])
    libro=db.get_or_404(Libro, libro_id)
    max_carrito=5
    
    if libro.stock <= 0:
        flash("Ese libro está agotado.", "error")
        return redirect(url_for("public.mostrar_libros"))
    else:
        if libro_id in carrito:
            flash("Ese libro ya está en el carrito.", "error")
            return redirect(url_for("public.mostrar_libros"))
        else:
            if len(carrito)<max_carrito:
                carrito.append(libro_id)
                session["carrito"]=carrito
                session.permanent=True
                session.modified=True
                flash("Se añadió el libro al carrito.", "exito")
            else:
                flash("Tiene superado el límite de productos en el carrito.", "error")
    return redirect(url_for("public.mostrar_libros"))


@public_bp.route("/carrito")
@login_required
def ver_carrito():
    ids=session.get("carrito",[])
    libros=Libro.query.filter(Libro.id.in_(ids)).all()
    ids_validos = [libro.id for libro in libros]
    if len(ids_validos) != len(ids):
        session["carrito"] = ids_validos
        session.modified = True
    total_sin_descuento=0
    for libro in libros:
        total_sin_descuento+=libro.precio
    descuento_aplicado= total_sin_descuento>60
    if descuento_aplicado:
        total_final=total_sin_descuento-(total_sin_descuento*0.1)
        
    else:
        total_final=total_sin_descuento
    total_final=round(total_final,2)    
    return render_template(
        "carrito.html",
        libros=libros,
        total_sin_descuento=total_sin_descuento,
        descuento_aplicado=descuento_aplicado,
        total_final=total_final,
    )


@public_bp.route("/carrito/quitar/<int:libro_id>", methods=["POST"])
@login_required
def quitar_del_carrito(libro_id):
    carrito = session.get("carrito", [])
    if libro_id in carrito:
        carrito.remove(libro_id)
        ver_carrito()
        flash("Se ha eliminado con éxito","exito")
    else:
        flash("El libro no está en el carrito","error")
        
    return redirect(url_for("public.ver_carrito"))
""" @public_bp.route("/carrito/quitar/<int:libro_id>", methods=["POST"])
@login_required
def quitar_del_carrito(libro_id):
    carrito = session.get("carrito", [])
    if libro_id in carrito:
        carrito.remove(libro_id)
        session["carrito"] = carrito
        session.modified = True
        flash("Libro quitado del carrito.", "info")
    else:
        flash("Ese libro no estaba en el carrito.", "error")
    return redirect(url_for("public.ver_carrito"))
 """
@public_bp.route("/carrito/confirmar", methods=["POST"])
@login_required
def confirmar_compra():
    ids = session.get("carrito", [])
    libros = Libro.query.filter(Libro.id.in_(ids)).all()

    if not libros:
        flash("Tu carrito está vacío.", "info")
        return redirect(url_for("public.ver_carrito"))

    sin_stock = [libro.titulo for libro in libros if libro.stock <= 0]
    if sin_stock:
        flash("Ya no queda stock de: " + ", ".join(sin_stock), "error")
        return redirect(url_for("public.ver_carrito"))

    for libro in libros:
        libro.stock -= 1
    db.session.commit()

    session.pop("carrito", None)
    flash("¡Compra realizada correctamente!", "exito")
    return redirect(url_for("public.mostrar_libros"))
    
